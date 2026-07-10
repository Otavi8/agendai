"""Integration tests for AgendAI domain endpoints."""

from datetime import UTC, datetime, timedelta

import pytest

pytestmark = pytest.mark.asyncio


async def test_agendai_operational_flow(client, auth_headers):
    """Create core domain records, register check-in, and read dashboard/detail."""
    driver_response = await client.post(
        "/api/v1/agendai/drivers",
        headers=auth_headers,
        json={
            "name": "Joao Motorista",
            "cpf": "12345678900",
            "email": "joao@example.com",
            "phone": "+5511999999999",
            "company": "Transportadora Teste",
            "notes": "Cadastro de teste",
        },
    )
    assert driver_response.status_code == 200
    driver = driver_response.json()

    vehicle_response = await client.post(
        "/api/v1/agendai/vehicles",
        headers=auth_headers,
        json={
            "driver_id": driver["id"],
            "plate": "ABC1D23",
            "model": "Truck",
            "color": "Branco",
            "year": 2024,
        },
    )
    assert vehicle_response.status_code == 200
    vehicle = vehicle_response.json()

    supplier_response = await client.post(
        "/api/v1/agendai/suppliers",
        headers=auth_headers,
        json={
            "name": "Fornecedor Teste",
            "contact_email": "fornecedor@example.com",
            "contact_phone": "+5511888888888",
            "authorized_email_domain": "example.com",
        },
    )
    assert supplier_response.status_code == 200
    supplier = supplier_response.json()

    appointment_response = await client.post(
        "/api/v1/agendai/appointments",
        headers=auth_headers,
        json={
            "driver_id": driver["id"],
            "vehicle_id": vehicle["id"],
            "supplier_id": supplier["id"],
            "scheduled_at": (datetime.now(UTC) + timedelta(hours=1)).isoformat(),
            "dock": "Doca 01",
            "load_reference": "NF-123",
            "notes": "Recebimento prioritario",
        },
    )
    assert appointment_response.status_code == 200
    appointment = appointment_response.json()
    assert appointment["status"] == "pending"

    summary_response = await client.get("/api/v1/agendai/dashboard/summary", headers=auth_headers)
    assert summary_response.status_code == 200
    assert summary_response.json()["pending_appointments"] == 1

    detail_response = await client.get(f"/api/v1/agendai/appointments/{appointment['id']}", headers=auth_headers)
    assert detail_response.status_code == 200
    detail = detail_response.json()
    assert detail["driver"]["name"] == "Joao Motorista"
    assert detail["vehicle"]["plate"] == "ABC1D23"
    assert detail["supplier"]["name"] == "Fornecedor Teste"

    check_in_response = await client.post(
        f"/api/v1/agendai/appointments/{appointment['id']}/check-ins",
        headers=auth_headers,
        json={"method": "manual", "notes": "Check-in confirmado pela portaria"},
    )
    assert check_in_response.status_code == 200
    assert check_in_response.json()["method"] == "manual"

    updated_detail_response = await client.get(f"/api/v1/agendai/appointments/{appointment['id']}", headers=auth_headers)
    assert updated_detail_response.status_code == 200
    assert updated_detail_response.json()["appointment"]["status"] == "checked_in"
    assert len(updated_detail_response.json()["check_ins"]) == 1


async def test_agendai_late_alert_generation_and_integration_status(client, auth_headers):
    """Generate a late check-in alert and verify external integrations are disabled."""
    driver = (
        await client.post(
            "/api/v1/agendai/drivers",
            headers=auth_headers,
            json={"name": "Maria Motorista", "cpf": "98765432100"},
        )
    ).json()
    vehicle = (
        await client.post(
            "/api/v1/agendai/vehicles",
            headers=auth_headers,
            json={"driver_id": driver["id"], "plate": "XYZ9A87"},
        )
    ).json()
    supplier = (
        await client.post(
            "/api/v1/agendai/suppliers",
            headers=auth_headers,
            json={"name": "Fornecedor Atraso"},
        )
    ).json()

    appointment_response = await client.post(
        "/api/v1/agendai/appointments",
        headers=auth_headers,
        json={
            "driver_id": driver["id"],
            "vehicle_id": vehicle["id"],
            "supplier_id": supplier["id"],
            "scheduled_at": (datetime.now(UTC) - timedelta(minutes=20)).isoformat(),
        },
    )
    assert appointment_response.status_code == 200

    alert_response = await client.post("/api/v1/agendai/alerts/generate-late", headers=auth_headers)
    assert alert_response.status_code == 200
    created_alerts = alert_response.json()["created_alerts"]
    assert len(created_alerts) == 1
    assert created_alerts[0]["alert_type"] == "late_check_in"

    alerts_response = await client.get("/api/v1/agendai/alerts", headers=auth_headers)
    assert alerts_response.status_code == 200
    assert len(alerts_response.json()) == 1

    integration_response = await client.get("/api/v1/agendai/integrations/status", headers=auth_headers)
    assert integration_response.status_code == 200
    assert integration_response.json() == {
        "gmail_enabled": False,
        "whatsapp_enabled": False,
        "minio_enabled": False,
    }
