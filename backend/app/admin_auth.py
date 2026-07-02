import jwt
from typing import Optional
from starlette.requests import Request
from starlette.responses import RedirectResponse
from sqladmin.authentication import AuthenticationBackend

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.user import User


class AdminAuthenticationBackend(AuthenticationBackend):
    """Authentication backend for SQLAdmin using JWT tokens."""

    def __init__(self, secret_key: str = None):
        """Initialize with secret key."""
        self.secret_key = secret_key or settings.secret_key
        super().__init__(secret_key=self.secret_key)

    async def login(self, request: Request) -> bool:
        """Handle login form submission."""
        form = await request.form()
        username = form.get("username")
        password = form.get("password")

        if not username or not password:
            return False

        # Get database session
        db = SessionLocal()
        try:
            # Find user by username
            user = db.query(User).filter(User.username == username).first()

            if not user or not user.is_active:
                return False

            # Check if user is admin
            if not user.is_admin:
                return False

            # Verify password
            from app.core.user import verify_password
            if not verify_password(password, user.password_hash):
                return False

            # Generate JWT token
            payload = {
                "sub": str(user.id),
                "username": user.username,
                "is_admin": user.is_admin,
            }
            token = jwt.encode(payload, settings.secret_key, algorithm="HS256")

            # Store token in session
            request.session["admin_token"] = token
            request.session["admin_user"] = username

            return True
        finally:
            db.close()

    async def logout(self, request: Request) -> bool:
        """Handle logout."""
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> Optional[RedirectResponse]:
        """Check if user is authenticated."""
        # Check for token in session
        token = request.session.get("admin_token")
        username = request.session.get("admin_user")

        if not token or not username:
            return RedirectResponse(url=request.url_for("admin:login"), status_code=302)

        # Validate token
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])

            # Check if user is still admin
            db = SessionLocal()
            try:
                user = db.query(User).filter(User.username == username).first()
                if not user or not user.is_admin or not user.is_active:
                    request.session.clear()
                    return RedirectResponse(url=request.url_for("admin:login"), status_code=302)
            finally:
                db.close()

            return None  # User is authenticated
        except jwt.ExpiredSignatureError:
            request.session.clear()
            return RedirectResponse(url=request.url_for("admin:login"), status_code=302)
        except jwt.InvalidTokenError:
            request.session.clear()
            return RedirectResponse(url=request.url_for("admin:login"), status_code=302)
