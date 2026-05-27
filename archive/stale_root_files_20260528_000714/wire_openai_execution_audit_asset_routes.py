from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

main_path = ROOT / "backend" / "app" / "main.py"
test_file = ROOT / "test_openai_execution_audit_asset_routes_direct.py"

backup_dir = ROOT / "backups" / f"openai_execution_audit_asset_routes_before_{STAMP}"
backup_dir.mkdir(parents=True, exist_ok=True)

main_text = main_path.read_text(encoding="utf-8")
(backup_dir / "main.py").write_text(main_text, encoding="utf-8")

route_block = r'''

# ---------------------------------------------------------------------------
# OpenAI execution audit + asset persistence routes
# Added by wire_openai_execution_audit_asset_routes.py
# Purpose:
# - expose controlled OpenAI audit/asset persistence integration status
# - create execution ledger + asset preview packets after successful OpenAI execution
# - never expose credentials or internal storage keys
# ---------------------------------------------------------------------------

try:
    from backend.app.runtime.real_provider_http_execution_layer import (
        controlled_openai_audit_asset_integration_status,
        persist_openai_execution_audit_asset,
    )
except Exception:  # pragma: no cover
    controlled_openai_audit_asset_integration_status = None
    persist_openai_execution_audit_asset = None


@app.get("/controlled-openai-audit-assets/status")
def controlled_openai_audit_assets_status_route():
    if controlled_openai_audit_asset_integration_status is None:
        return {
            "status": "unavailable",
            "reason": "controlled_openai_audit_asset_runtime_not_loaded",
            "credential_values_exposed": False,
        }
    return controlled_openai_audit_asset_integration_status()


@app.post("/controlled-openai-audit-assets/persist")
async def controlled_openai_audit_assets_persist_route(payload: dict):
    if persist_openai_execution_audit_asset is None:
        return {
            "status": "unavailable",
            "reason": "controlled_openai_audit_asset_runtime_not_loaded",
            "credential_values_exposed": False,
        }

    safe_payload = dict(payload or {})
    return persist_openai_execution_audit_asset(
        tenant_id=safe_payload.get("tenant_id") or "unknown-tenant",
        request_id=safe_payload.get("request_id") or "unknown-request",
        provider_job_id=safe_payload.get("provider_job_id") or "unknown-provider-job",
        output_text=safe_payload.get("output_text"),
        asset_type=safe_payload.get("asset_type") or "text",
        latency_ms=int(safe_payload.get("latency_ms", 0) or 0),
    )
'''

marker = "# OpenAI execution audit + asset persistence routes"
if marker in main_text:
    print("OPENAI_EXECUTION_AUDIT_ASSET_ROUTES_ALREADY_PRESENT")
else:
    main_path.write_text(main_text.rstrip() + "\n" + route_block + "\n", encoding="utf-8")
    print("OPENAI_EXECUTION_AUDIT_ASSET_ROUTES_WIRED")

test_file.write_text(r'''
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

status = client.get("/controlled-openai-audit-assets/status").json()
assert status["audit_asset_integration_ready"] is True
assert status["asset_record_creation_ready"] is True
assert status["customer_safe_preview_ready"] is True
assert status["credential_values_exposed"] is False

result = client.post(
    "/controlled-openai-audit-assets/persist",
    json={
        "tenant_id": "tenant-test",
        "request_id": "request-test",
        "provider_job_id": "openai-response-123",
        "output_text": "Safe generated result.",
        "asset_type": "text",
        "latency_ms": 1234,
    },
).json()

assert result["status"] == "persisted"
assert result["execution_id"]
assert result["asset"]["provider_key"] == "openai"
assert result["asset"]["asset_status"] == "ready"
assert result["preview"]["status"] == "ready"
assert result["preview"]["internal_storage_key_exposed"] is False
assert result["event_bridge"]["entry"]["event_type"] == "controlled_openai_execution_completed"
assert result["latency_bridge"]["metric"]["latency_ms"] == 1234
assert result["credential_values_exposed"] is False

print("OPENAI_EXECUTION_AUDIT_ASSET_ROUTES_DIRECT_TESTS_PASSED")
print("status_ready", status["audit_asset_integration_ready"])
print("persisted_status", result["status"])
print("execution_id", result["execution_id"])
print("asset_id", result["asset"]["asset_id"])
print("preview_status", result["preview"]["status"])
print("event_type", result["event_bridge"]["entry"]["event_type"])
print("latency", result["latency_bridge"]["metric"]["latency_ms"])
'''.lstrip(), encoding="utf-8")

print("OPENAI_EXECUTION_AUDIT_ASSET_ROUTES_INSTALLED")
print(f"Backup folder: {backup_dir}")
print(f"Updated: {main_path}")
print(f"Created/updated: {test_file}")