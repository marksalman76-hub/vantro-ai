from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def assert_true(condition, message):
    if not condition:
        raise AssertionError(message)


for route in [
    "/admin/provider-workforce-runtime-hardening",
    "/admin/provider-runtime-health",
    "/admin/provider-recovery-readiness",
]:
    response = client.get(route)
    assert_true(response.status_code == 200, f"{route} failed: {response.status_code} {response.text}")
    data = response.json()
    assert_true(data["success"] is True, f"{route} success failed")
    assert_true(data["visibility_only"] is True, f"{route} must be visibility only")
    assert_true(data["external_action_performed"] is False, f"{route} performed external action")
    assert_true(data["live_external_call_executed"] is False, f"{route} executed live external call")
    assert_true(data["credential_values_exposed"] is False, f"{route} exposed credentials")
    assert_true(data["customer_safe"] is True, f"{route} not customer safe")
    assert_true(data["governance_enforced"] is True, f"{route} governance not enforced")

health = client.get("/admin/provider-runtime-health").json()
assert_true("provider_statuses" in health, "provider statuses missing")
assert_true(health["provider_count"] >= 1, "provider count missing")
for provider, status in health["provider_statuses"].items():
    assert_true(status["credential_values_exposed"] is False, f"{provider} exposed credentials")
    assert_true(status["customer_safe"] is True, f"{provider} not customer safe")
    assert_true("health_score" in status, f"{provider} health score missing")
    assert_true("health_state" in status, f"{provider} health state missing")

recovery = client.get("/admin/provider-recovery-readiness").json()
assert_true(recovery["retry_escalation_linked"] is True, "retry escalation should be linked")
assert_true(recovery["timeline_events_linked"] is True, "timeline events should be linked")
assert_true(recovery["safe_queue_preparation_enabled"] is True, "safe queue prep should be enabled")
assert_true(recovery["dispatch_policy_layer_enabled"] is True, "dispatch policy should be enabled")

hardening = client.get("/admin/provider-workforce-runtime-hardening").json()
layers = hardening["hardening_layers"]
for key in [
    "provider_health_scoring",
    "provider_registry_visibility",
    "dispatch_policy_visibility",
    "worker_foundation_visibility",
    "retry_recovery_readiness",
    "admin_safe_status_packets",
    "credential_safe_visibility",
    "external_execution_not_triggered_by_status_routes",
]:
    assert_true(layers[key] is True, f"{key} not enabled")

print("PROVIDER_WORKFORCE_RUNTIME_HARDENING_TEST_PASSED")
print({
    "provider_count": health["provider_count"],
    "configured_provider_count": health["configured_provider_count"],
    "ready_provider_count": health["ready_provider_count"],
    "recovery_modes": recovery["recovery_modes"],
    "hardening_layers": layers,
})
