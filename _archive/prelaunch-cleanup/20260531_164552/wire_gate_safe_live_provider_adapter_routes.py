from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

main_path = ROOT / "backend" / "app" / "main.py"
test_file = ROOT / "test_gate_safe_live_provider_adapter_routes.py"
backup_dir = ROOT / "backups" / f"gate_safe_adapter_routes_before_{STAMP}"
backup_dir.mkdir(parents=True, exist_ok=True)

if not main_path.exists():
    raise FileNotFoundError(f"Missing main.py: {main_path}")

main_text = main_path.read_text(encoding="utf-8")
(backup_dir / "main.py").write_text(main_text, encoding="utf-8")

if test_file.exists():
    (backup_dir / test_file.name).write_text(test_file.read_text(encoding="utf-8"), encoding="utf-8")

route_block = r'''

# ---------------------------------------------------------------------------
# Gate-safe live provider adapter routes
# Added by wire_gate_safe_live_provider_adapter_routes.py
# Purpose:
# - expose credential-safe provider adapter runtime checks
# - expose owner-governed execution preparation only
# - keep real provider calls blocked unless credentials + owner execution gates pass
# ---------------------------------------------------------------------------

try:
    from backend.app.runtime.live_provider_adapters import (
        build_failover_routing_packet,
        build_polling_packet,
        calculate_provider_health_score,
        create_execution_audit_linkage,
        create_signed_asset_delivery_packet,
        execute_gate_safe_provider_request,
        live_provider_adapter_runtime_status,
        normalise_provider_failure,
        provider_timeout_policy,
    )
except Exception:  # pragma: no cover
    build_failover_routing_packet = None
    build_polling_packet = None
    calculate_provider_health_score = None
    create_execution_audit_linkage = None
    create_signed_asset_delivery_packet = None
    execute_gate_safe_provider_request = None
    live_provider_adapter_runtime_status = None
    normalise_provider_failure = None
    provider_timeout_policy = None


@app.get("/live-provider-adapter-runtime-status/{provider_key}")
def live_provider_adapter_runtime_status_route(provider_key: str):
    if live_provider_adapter_runtime_status is None:
        return {
            "status": "unavailable",
            "reason": "live_provider_adapter_runtime_not_loaded",
            "credential_values_exposed": False,
        }

    return live_provider_adapter_runtime_status(provider_key)


@app.post("/live-provider-adapter-execute/{provider_key}")
async def live_provider_adapter_execute_route(provider_key: str, payload: dict):
    if execute_gate_safe_provider_request is None:
        return {
            "status": "blocked",
            "reason": "live_provider_adapter_runtime_not_loaded",
            "credential_values_exposed": False,
        }

    safe_payload = dict(payload or {})
    result = execute_gate_safe_provider_request(provider_key, safe_payload)

    tenant_id = safe_payload.get("tenant_id") or "unknown-tenant"
    request_id = safe_payload.get("request_id") or "unknown-request"
    provider_job_id = result.get("provider_job_id")

    audit_linkage = None
    if create_execution_audit_linkage is not None:
        audit_linkage = create_execution_audit_linkage(
            tenant_id=tenant_id,
            request_id=request_id,
            provider_key=provider_key,
            provider_job_id=provider_job_id,
            execution_status=result.get("status", "blocked"),
        )

    return {
        "status": result.get("status"),
        "provider_key": provider_key,
        "execution_result": result,
        "audit_linkage": audit_linkage,
        "owner_governed_execution_required": True,
        "credential_values_exposed": False,
        "customer_safe": True,
    }


@app.get("/live-provider-adapter-timeout-policy/{provider_key}")
def live_provider_adapter_timeout_policy_route(provider_key: str):
    if provider_timeout_policy is None:
        return {
            "status": "unavailable",
            "reason": "live_provider_adapter_runtime_not_loaded",
            "credential_values_exposed": False,
        }

    return {
        "provider_key": provider_key,
        "timeout_policy": provider_timeout_policy(provider_key),
        "credential_values_exposed": False,
    }


@app.get("/live-provider-adapter-polling-packet/{provider_key}/{provider_job_id}")
def live_provider_adapter_polling_packet_route(provider_key: str, provider_job_id: str):
    if build_polling_packet is None:
        return {
            "status": "unavailable",
            "reason": "live_provider_adapter_runtime_not_loaded",
            "credential_values_exposed": False,
        }

    return build_polling_packet(provider_key, provider_job_id)


@app.post("/live-provider-adapter-failover-routing")
async def live_provider_adapter_failover_routing_route(payload: dict):
    if build_failover_routing_packet is None:
        return {
            "status": "unavailable",
            "reason": "live_provider_adapter_runtime_not_loaded",
            "credential_values_exposed": False,
        }

    safe_payload = dict(payload or {})
    requested_provider = safe_payload.get("requested_provider") or safe_payload.get("provider_key") or ""
    available_providers = safe_payload.get("available_providers") or []

    return build_failover_routing_packet(
        requested_provider=requested_provider,
        available_providers=available_providers,
    )


@app.post("/live-provider-adapter-health-score")
async def live_provider_adapter_health_score_route(payload: dict):
    if calculate_provider_health_score is None:
        return {
            "status": "unavailable",
            "reason": "live_provider_adapter_runtime_not_loaded",
            "credential_values_exposed": False,
        }

    safe_payload = dict(payload or {})
    return calculate_provider_health_score(
        success_count=int(safe_payload.get("success_count", 0) or 0),
        failure_count=int(safe_payload.get("failure_count", 0) or 0),
        timeout_count=int(safe_payload.get("timeout_count", 0) or 0),
        average_latency_ms=safe_payload.get("average_latency_ms"),
    )


@app.post("/live-provider-adapter-failure-normalisation")
async def live_provider_adapter_failure_normalisation_route(payload: dict):
    if normalise_provider_failure is None:
        return {
            "status": "unavailable",
            "reason": "live_provider_adapter_runtime_not_loaded",
            "credential_values_exposed": False,
        }

    safe_payload = dict(payload or {})
    return normalise_provider_failure(
        provider_key=safe_payload.get("provider_key") or "unknown",
        error_code=safe_payload.get("error_code") or "provider_error",
        message=safe_payload.get("message") or "Provider execution failed safely.",
        retryable=bool(safe_payload.get("retryable", True)),
        status_code=safe_payload.get("status_code"),
    )


@app.post("/live-provider-adapter-asset-packet")
async def live_provider_adapter_asset_packet_route(payload: dict):
    if create_signed_asset_delivery_packet is None:
        return {
            "status": "unavailable",
            "reason": "live_provider_adapter_runtime_not_loaded",
            "credential_values_exposed": False,
        }

    safe_payload = dict(payload or {})
    return create_signed_asset_delivery_packet(
        tenant_id=safe_payload.get("tenant_id") or "unknown-tenant",
        asset_id=safe_payload.get("asset_id") or "unknown-asset",
        provider_key=safe_payload.get("provider_key") or "unknown-provider",
        asset_type=safe_payload.get("asset_type") or "generated_asset",
        expires_in_seconds=int(safe_payload.get("expires_in_seconds", 3600) or 3600),
    )
'''

marker = "# Gate-safe live provider adapter routes"
if marker in main_text:
    print("GATE_SAFE_PROVIDER_ADAPTER_ROUTES_ALREADY_PRESENT")
else:
    main_path.write_text(main_text.rstrip() + "\n" + route_block + "\n", encoding="utf-8")
    print("GATE_SAFE_PROVIDER_ADAPTER_ROUTES_WIRED")

test_file.write_text(r'''
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
'''.lstrip(), encoding="utf-8")

print(f"Backup folder: {backup_dir}")
print(f"Updated: {main_path}")
print(f"Created/updated: {test_file}")
print("Routes added without enabling real external provider calls.")