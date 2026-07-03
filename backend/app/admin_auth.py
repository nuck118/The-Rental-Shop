import jwt
from typing import Union

from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette.responses import RedirectResponse
from sqladmin.authentication import AuthenticationBackend

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.user import User

# Session settings shared with SQLAdmin's internal SessionMiddleware.
# SQLAdmin mounts its own SessionMiddleware; do NOT add a second one on the
# FastAPI app or the outer middleware will overwrite the admin session cookie.
ADMIN_SESSION_KWARGS = {
    "session_cookie": "session",
    "max_age": 1209600,  # 14 days
    "same_site": "none",  # Changed to none for cross-domain requests
    "https_only": True,   # Required for same_site=none
}


class AdminAuthenticationBackend(AuthenticationBackend):
    """Authentication backend for SQLAdmin using session-stored JWT tokens."""

    def __init__(self, secret_key: str | None = None, **session_kwargs):
        self.secret_key = secret_key or settings.secret_key
        session_options = {**ADMIN_SESSION_KWARGS, **session_kwargs}
        self.middlewares = [
            Middleware(
                SessionMiddleware,
                secret_key=self.secret_key,
                **session_options,
            ),
        ]

    async def login(self, request: Request) -> bool:
        """Handle login form submission."""
        form = await request.form()
        username = form.get("username")
        password = form.get("password")

        if not username or not password:
            return False

        db = SessionLocal()
        try:
            user = db.query(User).filter(User.username == username).first()

            if not user or not user.is_active or not user.is_admin:
                return False

            from app.core.user import verify_password

            if not verify_password(password, user.password_hash):
                return False

            payload = {
                "sub": str(user.id),
                "username": user.username,
                "is_admin": user.is_admin,
            }
            token = jwt.encode(payload, self.secret_key, algorithm="HS256")

            request.session["admin_token"] = token
            request.session["admin_user"] = username
            return True
        finally:
            db.close()

    async def logout(self, request: Request) -> bool:
        """Handle logout."""
        request.session.clear()
        return True

    async def authenticate(
        self, request: Request
    ) -> Union[bool, RedirectResponse]:
        """Check if user is authenticated."""
        token = request.session.get("admin_token")
        username = request.session.get("admin_user")

        if not token or not username:
            return RedirectResponse(
                url=request.url_for("admin:login"), status_code=302
            )

        try:
            jwt.decode(token, self.secret_key, algorithms=["HS256"])
        except jwt.InvalidTokenError:
            request.session.clear()
            return RedirectResponse(
                url=request.url_for("admin:login"), status_code=302
            )

        db = SessionLocal()
        try:
            user = db.query(User).filter(User.username == username).first()
            if not user or not user.is_admin or not user.is_active:
                request.session.clear()
                return RedirectResponse(
                    url=request.url_for("admin:login"), status_code=302
                )
        finally:
            db.close()

        request.state.admin_user_id = user.id
        request.state.admin_user = user
        return True
