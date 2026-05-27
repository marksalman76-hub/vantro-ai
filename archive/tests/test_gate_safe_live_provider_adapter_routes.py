import os
from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_live_provider_status_route_blocks_without_credentials(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    response = client.get("/live-provider-adapter-runtime-status/openai")
    assert response.status_code == 200
    data = response.json()
    assert data["known_adapter"] is True
    assert data["configured"] is False
    assert data["ready"] is False
    assert "OPENAI_API_KEY" in data["missing"]
    assert data["credential_values_exposed"] is False
    assert data["owner_governed_execution_required"] is True


def test_live_provider_execute_route_blocks_without_credentials(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    response = client.post(
        "/live-provider-adapter-execute/openai",
        json={
            "tenant_id": "tenant-test",
            "request_id": "request-test",
            "prompt": "test",
            "live_execution_requested": True,
            "owner_governed_execution_confirmed": True,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "blocked"
    assert data["execution_result"]["reason"] == "provider_credentials_missing"
    assert data["credential_values_exposed"] is False
    assert data["owner_governed_execution_required"] is True
    assert data["customer_safe"] is True


def test_live_provider_execute_route_prepares_when_all_gates_pass(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-secret-not-exposed")
    response = client.post(
        "/live-provider-adapter-execute/openai",
        json={
            "tenant_id": "tenant-test",
            "request_id": "request-test",
            "prompt": "test",
            "live_execution_requested": True,
            "owner_governed_execution_confirmed": True,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready_for_live_provider_call"
    assert data["execution_result"]["adapter_name"] == "openai_live_execution_adapter_v1"
    assert data["execution_result"]["credential_values_exposed"] is False
    assert data["audit_linkage"]["audit_event_type"] == "provider_execution_linkage"


def test_timeout_polling_asset_health_routes(monkeypatch):
    timeout = client.get("/live-provider-adapter-timeout-policy/runway").json()
    assert timeout["timeout_policy"]["job_timeout_seconds"] >= 900
    assert timeout["credential_values_exposed"] is False

    polling = client.get("/live-provider-adapter-polling-packet/runway/job-123").json()
    assert polling["provider_job_id"] == "job-123"
    assert polling["credential_values_exposed"] is False

    asset = client.post(
        "/live-provider-adapter-asset-packet",
        json={
            "tenant_id": "tenant-test",
            "asset_id": "asset-123",
            "provider_key": "openai",
            "asset_type": "image",
        },
    ).json()
    assert asset["customer_safe"] is True
    assert asset["download_allowed"] is True
    assert len(asset["signature"]) == 64
    assert asset["credential_values_exposed"] is False

    health = client.post(
        "/live-provider-adapter-health-score",
        json={
            "success_count": 8,
            "failure_count": 1,
            "timeout_count": 1,
            "average_latency_ms": 35000,
        },
    ).json()
    assert "health_score" in health
    assert "failover_recommended" in health


def test_failure_and_failover_routes(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-secret-not-exposed")
    monkeypatch.delenv("RUNWAY_API_KEY", raising=False)

    failure = client.post(
        "/live-provider-adapter-failure-normalisation",
        json={
            "provider_key": "openai",
            "error_code": "provider_timeout",
            "message": "Provider timed out safely.",
            "retryable": True,
            "status_code": 504,
        },
    ).json()
    assert failure["status"] == "failed"
    assert failure["retryable"] is True
    assert failure["credential_values_exposed"] is False

    failover = client.post(
        "/live-provider-adapter-failover-routing",
        json={
            "requested_provider": "runway",
            "available_providers": ["openai", "runway"],
        },
    ).json()
    assert "openai" in failover["available_configured_providers"]
    assert "runway" not in failover["available_configured_providers"]
    assert failover["credential_values_exposed"] is False
