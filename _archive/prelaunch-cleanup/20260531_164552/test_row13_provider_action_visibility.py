from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def assert_true(condition, message):
    if not condition:
        raise AssertionError(message)


status = client.get("/admin/provider-action-readiness")
assert_true(status.status_code == 200, f"status route failed: {status.status_code} {status.text}")
data = status.json()

assert_true(data["success"] is True, "readiness response should succeed")
assert_true(data["visibility_only"] is True, "route must be visibility-only")
assert_true(data["live_external_calls_enabled"] is False, "must not enable live external calls")
assert_true(data["external_action_performed"] is False, "must not perform external action")
assert_true(data["credential_values_exposed"] is False, "must not expose credentials")
assert_true(data["owner_admin_client_limits_applied"] is False, "owner/admin visibility must not apply client limits")
assert_true(data["governance_enforced"] is True, "governance must remain enforced")

checks = data["checks"]
assert_true(checks["admin_owner_execution"]["execution_status"] == "safe_internal_action_allowed", "admin internal check failed")
assert_true(checks["live_provider_generation_missing_approval"]["execution_status"] == "blocked_owner_approval_required", "approval block failed")
assert_true(checks["live_provider_generation_disabled"]["execution_status"] == "blocked_live_execution_disabled", "disabled live execution block failed")
assert_true(checks["live_provider_generation_ready"]["execution_status"] == "live_action_ready_for_provider_adapter", "ready state failed")
assert_true(checks["live_provider_generation_ready"]["external_action_performed"] is False, "ready state must not call provider")

eval_blocked = client.post("/admin/provider-action-readiness/evaluate", json={
    "action_type": "live_provider_generation",
    "provider": "openai",
    "owner_approved": False,
    "live_execution_enabled": True,
})
assert_true(eval_blocked.status_code == 200, f"evaluate route failed: {eval_blocked.status_code} {eval_blocked.text}")
blocked_data = eval_blocked.json()
assert_true(blocked_data["success"] is True, "evaluate response should succeed")
assert_true(blocked_data["decision"]["execution_status"] == "blocked_owner_approval_required", "evaluate approval block failed")
assert_true(blocked_data["external_action_performed"] is False, "evaluate route must not perform external action")
assert_true(blocked_data["credential_values_exposed"] is False, "evaluate route must not expose credentials")

eval_ready = client.post("/admin/provider-action-readiness/evaluate", json={
    "action_type": "live_provider_generation",
    "provider": "openai",
    "owner_approved": True,
    "live_execution_enabled": True,
})
assert_true(eval_ready.status_code == 200, f"evaluate ready failed: {eval_ready.status_code} {eval_ready.text}")
ready_data = eval_ready.json()
assert_true(ready_data["decision"]["execution_status"] == "live_action_ready_for_provider_adapter", "evaluate ready state failed")
assert_true(ready_data["decision"]["external_action_performed"] is False, "foundation must not call provider")

print("ROW13_PROVIDER_ACTION_VISIBILITY_TEST_PASSED")
print(data)
print(blocked_data)
print(ready_data)
