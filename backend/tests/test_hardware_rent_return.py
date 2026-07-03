"""Tests for hardware rent and return endpoints."""

from tests.conftest import auth_header
from app.models.hardware import HardwareAsset


def test_rent_available_device(client, users, available_device):
    response = client.post(
        f"/api/hardware/{available_device.id}/rent",
        headers=auth_header(users["alice"]),
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "In Use"
    assert data["assigned_to"] == "alice"


def test_rent_unavailable_device_returns_400(client, users, rented_device):
    response = client.post(
        f"/api/hardware/{rented_device.id}/rent",
        headers=auth_header(users["bob"]),
    )

    assert response.status_code == 400
    assert "cannot be rented" in response.json()["detail"].lower()


def test_rent_repair_device_returns_400(client, users, db_session):
    device = HardwareAsset(
        name="Broken Tablet",
        brand="Samsung",
        status="Repair",
    )
    db_session.add(device)
    db_session.commit()
    db_session.refresh(device)

    response = client.post(
        f"/api/hardware/{device.id}/rent",
        headers=auth_header(users["alice"]),
    )

    assert response.status_code == 400


def test_rent_without_auth_returns_401(client, available_device):
    response = client.post(f"/api/hardware/{available_device.id}/rent")
    assert response.status_code == 401


def test_return_own_rented_device(client, users, rented_device):
    response = client.post(
        f"/api/hardware/{rented_device.id}/return",
        headers=auth_header(users["alice"]),
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Available"
    assert data["assigned_to"] is None


def test_return_device_rented_by_another_user_returns_403(client, users, rented_device):
    response = client.post(
        f"/api/hardware/{rented_device.id}/return",
        headers=auth_header(users["bob"]),
    )

    assert response.status_code == 403
    assert "did not rent" in response.json()["detail"].lower()


def test_return_available_device_returns_400(client, users, available_device):
    response = client.post(
        f"/api/hardware/{available_device.id}/return",
        headers=auth_header(users["alice"]),
    )

    assert response.status_code == 400
    assert "cannot be returned" in response.json()["detail"].lower()
