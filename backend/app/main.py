from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi_csrf_protect.exceptions import CsrfProtectError

from app.core.config import settings
from app.core.database import engine, Base
import app.models  # noqa: F401 — register models with Base.metadata
from app.security.middleware import SecurityMiddleware
from app.ai.router import router as ai_router
from app.api.routes.hardware import router as hardware_router
from app.api.routes.auth import router as auth_router
from app.admin import setup_admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create all tables on startup
    Base.metadata.create_all(bind=engine)
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="The Rental Shop API", lifespan=lifespan)

    # CORS Middleware - use configured origins for proper credentials support
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["X-Total-Count", "X-Page-Count"],
    )

    # Security Middleware - disabled for demo
    # app.add_middleware(
    #     SecurityMiddleware,
    #     secret_key=settings.secret_key,
    #     rate_limit_window=settings.rate_limit_window,
    #     rate_limit_max_requests=settings.rate_limit_max_requests,
    #     csrf_enabled=settings.csrf_enabled,
    #     jwt_enabled=settings.jwt_enabled,
    # )

    # Include routers
    app.include_router(auth_router)
    app.include_router(hardware_router)
    app.include_router(ai_router)

    # Health check endpoint
    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}

    # Global CSRF exception handler
    @app.exception_handler(CsrfProtectError)
    async def csrf_protect_exception_handler(request: Request, exc: CsrfProtectError):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message},
        )

    # SQLAdmin mounts its own SessionMiddleware via AuthenticationBackend.
    # Do not add a global SessionMiddleware here — a duplicate would overwrite
    # the admin session cookie on every response.
    setup_admin(app)

    return app


app = create_app()
