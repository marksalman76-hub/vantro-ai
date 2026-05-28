from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def assert_true(condition, message):
    if not condition:
        raise AssertionError(message)


status = client.get("/admin/provider-activation-visibility")
assert_true(status.status_code == 200, f"visibility route failed: {status.status_code} {status.text}")
data = status.json()

assert_true(data["success"] is True, "visibility route should succeed")
assert_true(data["visibility_only"] is True, "visibility route must be visibility only")
assert_true(data["external_action_performed"] is False, "must not perform external action")
assert_true(data["live_external_call_executed"] is False, "must not execute live external call")
assert_true(data["credential_values_exposed"] is False, "must not expose credential values")
assert_true(data["governance_enforced"] is True, "governance must remain enforced")
assert_true("registry_status" in data, "registry status missing")
assert_true("dispatch_policy_status" in data, "dispatch policy status missing")
assert_true("controlled_openai_status" in data, "controlled OpenAI status missing")
assert_true(data["dispatch_policy_status"]["requires_final_policy_enablement"] is True, "final policy enablement must be required")

for provider, runtime in data["provider_runtime_status"].items():
    assert_true(runtime["credential_values_exposed"] is False, f"{provider} exposed credentials")
    assert_true(runtime["customer_safe"] is True, f"{provider} not customer safe")

blocked = client.post("/admin/provider-activation-visibility/evaluate", json={
    "provider_key": "openai",
    "capability": "text_generation",
    "tenant_id": "owner_admin",
    "request_id": "test_provider_activation_visibility_blocked",
    "prompt": "Visibility test only.",
    "live_execution_requested": False,
    "owner_governed_execution_confirmed": False,
})
assert_true(blocked.status_code == 200, f"evaluate blocked failed: {blocked.status_code} {blocked.text}")
blocked_data = blocked.json()
assert_true(blocked_data["success"] is True, "evaluate should succeed")
assert_true(blocked_data["visibility_only"] is True, "evaluate must be visibility only")
assert_true(blocked_data["external_action_performed"] is False, "evaluate must not perform external action")
assert_true(blocked_data["live_external_call_executed"] is False, "evaluate must not execute live external call")
assert_true(blocked_data["credential_values_exposed"] is False, "evaluate must not expose credentials")
assert_true(blocked_data["dispatch_policy"]["live_external_call_executed"] is False, "dispatch policy must not execute externally")

ready_probe = client.post("/admin/provider-activation-visibility/evaluate", json={
    "provider_key": "openai",
    "capability": "text_generation",
    "tenant_id": "owner_admin",
    "request_id": "test_provider_activation_visibility_ready_probe",
    "prompt": "Visibility test only.",
    "live_execution_requested": True,
    "owner_governed_execution_confirmed": True,
})
assert_true(ready_probe.status_code == 200, f"evaluate ready probe failed: {ready_probe.status_code} {ready_probe.text}")
ready_data = ready_probe.json()
assert_true(ready_data["success"] is True, "ready probe should succeed")
assert_true(ready_data["live_external_call_executed"] is False, "ready probe route must not claim external call")
assert_true(ready_data["credential_values_exposed"] is False, "ready probe must not expose credentials")
assert_true(ready_data["dispatch_policy"]["live_external_call_executed"] is False, "ready probe dispatch policy must not execute externally")

openai_probe = ready_data.get("controlled_openai_probe") or {}
assert_true(openai_probe.get("live_external_call_executed") is False, "controlled OpenAI probe must not execute externally unless final env gates enable it")
assert_true(openai_probe.get("credential_values_exposed") is False, "controlled OpenAI probe must not expose credentials")

print("PROVIDER_ACTIVATION_VISIBILITY_TEST_PASSED")
print(data)
print(blocked_data)
print(ready_data)
