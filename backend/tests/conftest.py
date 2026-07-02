"""Shared pytest fixtures for backend API tests."""
import pytest
from datetime import datetime, timedelta

import jwt
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.routes.hardware import router as hardware_router
from app.core.config import settings
from app.core.database import Base, get_db
from app.core.user import create_user
from app.models.hardware import HardwareAsset
import app.models  # noqa: F401 — register models with Base.metadata


@pytest.fixture
def db_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db_session):
    app = FastAPI()
    app.include_router(hardware_router)

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def users(db_session):
    owner = create_user(
        db_session,
        username="alice",
        email="alice@example.com",
        password="password123",
    )
    other = create_user(
        db_session,
        username="bob",
        email="bob@example.com",
        password="password123",
    )
    return {"alice": owner, "bob": other}


def auth_header(user) -> dict[str, str]:
    token = jwt.encode(
        {
            "sub": str(user.id),
            "username": user.username,
            "exp": datetime.utcnow() + timedelta(hours=1),
        },
        settings.secret_key,
        algorithm="HS256",
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def available_device(db_session):
    device = HardwareAsset(
        name="Test Laptop",
        brand="Dell",
        status="Available",
    )
    db_session.add(device)
    db_session.commit()
    db_session.refresh(device)
    return device


@pytest.fixture
def rented_device(db_session, users):
    device = HardwareAsset(
        name="Rented Phone",
        brand="Apple",
        status="In Use",
        assigned_to=users["alice"].username,
    )
    db_session.add(device)
    db_session.commit()
    db_session.refresh(device)
    return device
