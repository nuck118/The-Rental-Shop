from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from piccolo_admin.endpoints import create_admin
from piccolo.engine import engine_finder

from app.core.config import settings
from app.models.hardware import HardwareAsset
from app.security.middleware import SecurityMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    engine = engine_finder()
    await engine.start_connection_pool()
    yield
    await engine.close_connection_pool()


def create_app() -> FastAPI:
    app = FastAPI(title="The Rental Shop API", lifespan=lifespan)

    # Security Middleware (must be added first, before CORS)
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

    app.mount("/admin", create_admin(tables=[HardwareAsset]))

    return app


app = create_app()
