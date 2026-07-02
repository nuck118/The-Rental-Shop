from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from piccolo_admin.endpoints import create_admin
from piccolo.engine import engine_finder

from app.core.config import settings
from app.models.hardware import HardwareAsset


@asynccontextmanager
async def lifespan(app: FastAPI):
    engine = engine_finder()
    await engine.start_connection_pool()
    yield
    await engine.close_connection_pool()


def create_app() -> FastAPI:
    app = FastAPI(title="The Rental Shop API", lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.mount("/admin", create_admin(tables=[HardwareAsset]))

    return app


app = create_app()
