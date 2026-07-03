import time
import hashlib
import hmac
import jwt
from collections import defaultdict
from typing import Optional
from datetime import datetime, timedelta

from fastapi import Request, HTTPException, status, Depends
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from fastapi_csrf_protect import CsrfProtect
from fastapi_csrf_protect.exceptions import CsrfProtectError

from app.core.csrf import get_csrf_config  # noqa: F401 - loads CSRF config


class RateLimitStore:
    """In-memory sliding window rate limiter for IP/token-based tracking."""

    def __init__(self, window_seconds: int = 60, max_requests: int = 100):
        self.window_seconds = window_seconds
        self.max_requests = max_requests
        self.requests: dict[str, list[float]] = defaultdict(list)

    def is_allowed(self, identifier: str) -> bool:
        """Check if identifier is within rate limit."""
        now = time.time()
        cutoff = now - self.window_seconds

        # Clean old requests outside the window
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier] if req_time > cutoff
        ]

        # Check if under limit
        if len(self.requests[identifier]) < self.max_requests:
            self.requests[identifier].append(now)
            return True

        return False


class CSRFTokenValidator:
    """CSRF token validation using HMAC-SHA256."""

    def __init__(self, secret_key: str):
        self.secret_key = secret_key.encode()

    def generate_token(self, session_id: str) -> str:
        """Generate a CSRF token for a session."""
        return hmac.new(
            self.secret_key,
            session_id.encode(),
            hashlib.sha256,
        ).hexdigest()

    def verify_token(self, session_id: str, token: str) -> bool:
        """Verify a CSRF token against a session."""
        expected = self.generate_token(session_id)
        return hmac.compare_digest(expected, token)


class SecurityMiddleware(BaseHTTPMiddleware):
    """
    Comprehensive security middleware for FastAPI ASGI pipeline.
    Handles rate limiting, CSRF validation, and JWT/session verification.
    """

    def __init__(
        self,
        app,
        secret_key: str,
        rate_limit_window: int = 60,
        rate_limit_max_requests: int = 100,
        csrf_enabled: bool = True,
        jwt_enabled: bool = True,
    ):
        super().__init__(app)
        self.secret_key = secret_key
        self.rate_limiter = RateLimitStore(rate_limit_window, rate_limit_max_requests)
        self.csrf_validator = CSRFTokenValidator(secret_key)
        self.csrf_enabled = csrf_enabled
        self.jwt_enabled = jwt_enabled
        self.protected_methods = {"POST", "PUT", "DELETE", "PATCH"}
        self.csrf_header_name = "x-csrf-token"
        self.jwt_header_name = "authorization"

    def _get_client_identifier(self, request: Request) -> str:
        """Extract client identifier (IP or auth token)."""
        # Try to get auth token first
        auth_header = request.headers.get(self.jwt_header_name, "")
        if auth_header.startswith("Bearer "):
            return auth_header[7:]  # Return token without "Bearer " prefix

        # Fall back to client IP
        client_ip = request.client.host if request.client else "unknown"
        return client_ip

    def _get_session_id(self, request: Request) -> Optional[str]:
        """Extract session ID from cookies or headers."""
        # Check for session cookie (Starlette SessionMiddleware uses "session" by default)
        session_cookie = request.cookies.get("session")
        if session_cookie:
            return session_cookie

        # Check for session_id cookie (legacy)
        session_cookie = request.cookies.get("session_id")
        if session_cookie:
            return session_cookie

        # Check for session header
        session_header = request.headers.get("x-session-id")
        if session_header:
            return session_header

        return None

    async def dispatch(self, request: Request, call_next):
        """Main middleware dispatch handler."""

        # Handle CORS preflight requests directly - return 200 with CORS headers
        if request.method == "OPTIONS":
            response = JSONResponse(content={"detail": "OK"}, status_code=200)
            origin = request.headers.get("origin")
            if origin:
                response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, PATCH, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "*"
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Max-Age"] = "86400"
            return response

        # 1. Rate Limiting Check
        client_id = self._get_client_identifier(request)
        if not self.rate_limiter.is_allowed(client_id):
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Rate limit exceeded"},
            )

        # 2. JWT/Session Verification (if enabled)
        if self.jwt_enabled:
            auth_header = request.headers.get(self.jwt_header_name, "")

            # Skip auth for public endpoints and GET requests
            is_public = self._is_public_endpoint(request.url.path)
            is_read_only = request.method == "GET"
            
            if not is_public and not is_read_only:
                if not auth_header:
                    return JSONResponse(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        content={"detail": "Missing authorization header"},
                        headers={"WWW-Authenticate": "Bearer"},
                    )

                # Validate Bearer format
                if not auth_header.startswith("Bearer "):
                    return JSONResponse(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        content={"detail": "Invalid authorization header format"},
                        headers={"WWW-Authenticate": "Bearer"},
                    )

                # Extract and validate token
                token = auth_header[7:]
                if not token or len(token) < 10:
                    return JSONResponse(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        content={"detail": "Invalid token"},
                        headers={"WWW-Authenticate": "Bearer"},
                    )

                # Validate JWT signature
                try:
                    from app.core.config import settings
                    jwt.decode(token, settings.secret_key, algorithms=["HS256"])
                except jwt.ExpiredSignatureError:
                    return JSONResponse(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        content={"detail": "Token has expired"},
                        headers={"WWW-Authenticate": "Bearer"},
                    )
                except jwt.InvalidTokenError:
                    return JSONResponse(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        content={"detail": "Invalid token"},
                        headers={"WWW-Authenticate": "Bearer"},
                    )

        # 3. CSRF Verification (if enabled and method is mutable)
        # Skip CSRF for admin panel - it uses its own session management
        if self.csrf_enabled and request.method in self.protected_methods and not request.url.path.startswith("/admin"):
            csrf_protect = CsrfProtect()
            try:
                await csrf_protect.validate_csrf(request)
            except CsrfProtectError as exc:
                return JSONResponse(
                    status_code=exc.status_code,
                    content={"detail": exc.message},
                )

        # 4. Add security headers to request state
        request.state.client_id = client_id
        request.state.session_id = self._get_session_id(request)
        request.state.timestamp = datetime.utcnow()

        # 5. Call next middleware/route handler
        response = await call_next(request)

        # 6. Add security response headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # Relaxed CSP for admin panel and development
        if request.url.path.startswith("/admin"):
            response.headers["Content-Security-Policy"] = "default-src 'self' 'unsafe-inline' 'unsafe-eval' data: blob:; img-src 'self' data: blob:; font-src 'self' data:;"
        else:
            response.headers["Content-Security-Policy"] = "default-src 'self'"

        return response

    def _is_public_endpoint(self, path: str) -> bool:
        """Check if endpoint is public (no auth required)."""
        public_paths = [
            "/health",
            "/docs",
            "/openapi.json",
            "/redoc",
            "/api/auth/login",
            "/api/auth/csrf-token",
            "/api/ai/health",
            "/api/ai/chat",
            "/admin",
        ]
        return any(path.startswith(p) for p in public_paths)
