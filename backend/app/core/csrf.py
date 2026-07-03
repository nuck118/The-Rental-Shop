"""CSRF protection configuration using fastapi-csrf-protect."""

import os
from pydantic_settings import BaseSettings
from fastapi_csrf_protect import CsrfProtect


class CsrfSettings(BaseSettings):
    """Settings for fastapi-csrf-protect.

    These values are loaded from environment variables / .env file.
    Available options:
      - secret_key: signing key (defaults to app SECRET_KEY)
      - cookie_key: cookie name (default: fastapi-csrf-token)
      - cookie_path: cookie path (default: /)
      - cookie_domain: cookie domain (default: None)
      - cookie_samesite: SameSite attribute (default: lax)
      - cookie_secure: Secure attribute (default: False)
      - httponly: HttpOnly attribute (default: True)
      - max_age: cookie/token max age in seconds (default: 3600)
      - token_key: form field name for body token (default: csrf-token)
      - header_name: header name for token (default: X-CSRF-Token)
      - token_location: where to look for token - header or body (default: header)
      - methods: HTTP methods to protect (default: POST, PUT, PATCH, DELETE)
    """

    secret_key: str = ""
    cookie_key: str = "fastapi-csrf-token"
    cookie_path: str = "/"
    cookie_domain: str | None = None
    cookie_samesite: str = "lax"
    cookie_secure: bool = False
    httponly: bool = True
    max_age: int = 3600
    token_key: str = "csrf-token"
    header_name: str = "X-CSRF-Token"
    token_location: str = "header"
    methods: list[str] = ["POST", "PUT", "PATCH", "DELETE"]


@CsrfProtect.load_config
def get_csrf_config() -> CsrfSettings:
    """Load CSRF configuration from application settings."""
    from app.core.config import settings

    # Check if we're in production (HTTPS required for cross-domain cookies)
    is_production = os.environ.get("ENVIRONMENT") == "production"
    
    # For cross-domain requests (vercel.app -> onrender.com), we need SameSite=None and Secure
    if is_production:
        return CsrfSettings(
            secret_key=settings.secret_key,
            cookie_samesite="none",
            cookie_secure=True,
        )
    else:
        # Use lax SameSite for local development; none requires secure=True which
        # breaks plain-HTTP local testing. Production should use secure=True.
        return CsrfSettings(
            secret_key=settings.secret_key,
            cookie_samesite="lax",
            cookie_secure=False,
        )
