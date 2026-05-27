import os
from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)

os.environ.pop("OPENAI_API_KEY", None)
os.environ.pop("REAL_PROVIDER_HTTP_DISPATCH_ENABLED", None)
os.environ.pop("OPENAI_ACTUAL_NETWORK_CALL_ENABLED", None)

status = client.get("/controlled-openai-live-execution/status").json()
assert status["controlled_live_execution_ready"] is True
assert status["openai_api_key_present"] is False
assert status["credential_values_exposed"] is False

blocked_no_key = client.post(
    "/controlled-openai-live-execution/execute",
    json={
        "tenant_id": "tenant-test",
        "request_id": "request-test",
        "prompt": "test",
        "live_execution_requested": True,
        "owner_governed_execution_confirmed": True,
    },
).json()
assert blocked_no_key["status"] == "blocked"
assert blocked_no_key["live_external_call_executed"] is False

os.environ["OPENAI_API_KEY"] = "test-secret-not-exposed"

blocked_policy = client.post(
    "/controlled-openai-live-execution/execute",
    json={
        "tenant_id": "tenant-test",
        "request_id": "request-test",
        "prompt": "test",
        "live_execution_requested": True,
        "owner_governed_execution_confirmed": True,
    },
).json()
assert blocked_policy["status"] == "blocked"
assert blocked_policy["reason"] == "real_provider_http_dispatch_globally_disabled"

os.environ["REAL_PROVIDER_HTTP_DISPATCH_ENABLED"] = "true"

ready_no_network = client.post(
    "/controlled-openai-live-execution/execute",
    json={
        "tenant_id": "tenant-test",
        "request_id": "request-test",
        "prompt": "test",
        "live_execution_requested": True,
        "owner_governed_execution_confirmed": True,
    },
).json()
assert ready_no_network["status"] == "ready_but_network_call_disabled"
assert ready_no_network["live_external_call_executed"] is False
assert ready_no_network["credential_values_exposed"] is False

print("CONTROLLED_OPENAI_LIVE_EXECUTION_ROUTES_DIRECT_TESTS_PASSED")
print("status_ready", status["controlled_live_execution_ready"])
print("blocked_no_key", blocked_no_key["status"])
print("blocked_policy", blocked_policy["status"], blocked_policy["reason"])
print("ready_no_network", ready_no_network["status"], ready_no_network["reason"])
