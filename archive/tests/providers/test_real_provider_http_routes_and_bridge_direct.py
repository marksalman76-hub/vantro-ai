import os
from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)

os.environ.pop("OPENAI_API_KEY", None)

status = client.get("/real-provider-http/runtime-status/openai").json()
assert status["known_adapter"] is True
assert status["configured"] is False
assert status["ready"] is False
assert "OPENAI_API_KEY" in status["missing"]
assert status["real_http_dispatch_enabled"] is False
assert status["credential_values_exposed"] is False

packet = client.post(
    "/real-provider-http/request-packet/openai",
    json={"prompt": "test", "model": "gpt-test"},
).json()
assert packet["provider_key"] == "openai"
assert packet["provider_endpoint"] == "responses"
assert packet["input_present"] is True
assert packet["credential_values_exposed"] is False

blocked = client.post(
    "/real-provider-http/execute/openai",
    json={
        "tenant_id": "tenant-test",
        "request_id": "request-test",
        "prompt": "test",
        "live_execution_requested": True,
        "owner_governed_execution_confirmed": True,
    },
).json()
assert blocked["status"] == "blocked"
assert blocked["reason"] == "provider_credentials_missing"
assert blocked["live_external_call_executed"] is False
assert blocked["credential_values_exposed"] is False

bridge_blocked = client.post(
    "/real-provider-http/dispatch-bridge/openai",
    json={
        "tenant_id": "tenant-test",
        "request_id": "request-test",
        "task_type": "image_generation",
        "payload": {"prompt": "test"},
        "live_execution_requested": True,
        "owner_governed_execution_confirmed": True,
    },
).json()
assert bridge_blocked["orchestration_status"] == "blocked"
assert bridge_blocked["http_dispatch_status"] == "blocked"
assert bridge_blocked["live_external_call_executed"] is False
assert bridge_blocked["credential_values_exposed"] is False

os.environ["OPENAI_API_KEY"] = "test-secret-not-exposed"

ready = client.post(
    "/real-provider-http/execute/openai",
    json={
        "tenant_id": "tenant-test",
        "request_id": "request-test",
        "prompt": "test",
        "live_execution_requested": True,
        "owner_governed_execution_confirmed": True,
    },
).json()
assert ready["status"] == "ready_for_real_http_dispatch"
assert ready["request_packet"]["provider_endpoint"] == "responses"
assert ready["live_external_call_executed"] is False
assert ready["dispatch_blocked_until_provider_credentials_and_final_policy_enablement"] is True
assert ready["credential_values_exposed"] is False

bridge_ready = client.post(
    "/real-provider-http/dispatch-bridge/openai",
    json={
        "tenant_id": "tenant-test",
        "request_id": "request-test",
        "task_type": "image_generation",
        "payload": {"prompt": "test"},
        "live_execution_requested": True,
        "owner_governed_execution_confirmed": True,
    },
).json()
assert bridge_ready["orchestration_status"] == "ready_for_live_provider_call"
assert bridge_ready["http_dispatch_status"] == "ready_for_real_http_dispatch"
assert bridge_ready["real_http_dispatch_enabled"] is False
assert bridge_ready["live_external_call_executed"] is False
assert bridge_ready["credential_values_exposed"] is False

success = client.post(
    "/real-provider-http/success-normalisation/openai",
    json={
        "tenant_id": "tenant-test",
        "request_id": "request-test",
        "asset_type": "text",
        "raw_response": {
            "id": "provider-job-123",
            "output_text": "Safe generated result.",
        },
    },
).json()
assert success["status"] == "completed"
assert success["provider_job_id"] == "provider-job-123"
assert success["asset_packet"]["customer_safe"] is True
assert success["credential_values_exposed"] is False

error = client.post(
    "/real-provider-http/error-normalisation/openai",
    json={
        "exception_type": "auth_error",
        "status_code": 401,
    },
).json()
assert error["failure_code"] == "provider_auth_error"
assert error["retryable"] is False
assert error["owner_review_required"] is True
assert error["credential_values_exposed"] is False

bridge_status = client.get("/real-provider-http/dispatch-bridge-status/openai").json()
assert bridge_status["bridge_ready"] is True
assert bridge_status["real_http_dispatch_enabled"] is False
assert bridge_status["credential_values_exposed"] is False

print("REAL_PROVIDER_HTTP_ROUTES_AND_BRIDGE_DIRECT_TESTS_PASSED")
print("status_configured", status["configured"])
print("request_endpoint", packet["provider_endpoint"])
print("blocked_status", blocked["status"], blocked["reason"])
print("bridge_blocked", bridge_blocked["orchestration_status"], bridge_blocked["http_dispatch_status"])
print("ready_status", ready["status"])
print("bridge_ready", bridge_ready["orchestration_status"], bridge_ready["http_dispatch_status"])
print("success_status", success["status"], success["provider_job_id"])
print("error_failure", error["failure_code"], error["retryable"])
print("bridge_status", bridge_status["bridge_ready"], bridge_status["real_http_dispatch_enabled"])
