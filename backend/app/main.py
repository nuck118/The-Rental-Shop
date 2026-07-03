from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

    # Security Middleware
    app.add_middleware(
        SecurityMiddleware,
        secret_key=settings.secret_key,
        rate_limit_window=settings.rate_limit_window,
        rate_limit_max_requests=settings.rate_limit_max_requests,
        csrf_enabled=settings.csrf_enabled,
        jwt_enabled=settings.jwt_enabled,
    )

    # CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["X-Total-Count", "X-Page-Count"],
    )

    # Include routers
    app.include_router(auth_router)
    app.include_router(hardware_router)
    app.include_router(ai_router)

    # SQLAdmin mounts its own SessionMiddleware via AuthenticationBackend.
    # Do not add a global SessionMiddleware here — a duplicate would overwrite
    # the admin session cookie on every response.
    setup_admin(app)

    return app


app = create_app()
