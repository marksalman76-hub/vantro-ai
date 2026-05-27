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
