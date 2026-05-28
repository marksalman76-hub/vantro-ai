from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def assert_true(condition, message):
    if not condition:
        raise AssertionError(message)


status = client.get("/admin/autonomous-workforce-orchestration/status")
assert_true(status.status_code == 200, status.text)
data = status.json()
assert_true(data["success"] is True, "status success failed")
assert_true(data["visibility_only"] is True, "status must be visibility only")
assert_true(data["autonomous_uncontrolled_actions_enabled"] is False, "uncontrolled autonomy must be blocked")
assert_true(data["live_external_call_executed"] is False, "status must not execute live call")
assert_true(data["external_action_performed"] is False, "status must not perform action")
assert_true(data["credential_values_exposed"] is False, "credentials exposed")
assert_true(data["governance_enforced"] is True, "governance not enforced")
assert_true(data["owner_approval_required_for_spend_scale_contracts"] is True, "owner approval protection missing")

for key in [
    "delegated_subtask_packets",
    "agent_to_agent_execution_packets",
    "orchestration_execution_graph",
    "orchestration_replay_recovery_packet",
    "provider_health_linked",
    "provider_recovery_linked",
    "customer_safe_status_packets",
    "uncontrolled_autonomy_blocked",
]:
    assert_true(data["foundation_layers"][key] is True, f"{key} missing")

plan = client.post("/admin/autonomous-workforce-orchestration/plan", json={
    "tenant_id": "owner_admin",
    "project_id": "orchestration_foundation_test",
    "lead_agent": "head_agent",
    "objective": "Prepare launch execution plan.",
    "requested_agents": ["marketing_specialist_agent", "seo_agent", "crm_ai_agent"],
})
assert_true(plan.status_code == 200, plan.text)
plan_data = plan.json()
assert_true(plan_data["success"] is True, "plan success failed")
assert_true(plan_data["visibility_only"] is True, "plan must be visibility only")
assert_true(plan_data["live_external_call_executed"] is False, "plan must not execute live call")
assert_true(plan_data["external_action_performed"] is False, "plan must not perform action")
assert_true(plan_data["credential_values_exposed"] is False, "plan exposed credentials")
assert_true(plan_data["governance_enforced"] is True, "plan governance not enforced")
assert_true(plan_data["plan"]["packet_count"] == 3, "packet count mismatch")
assert_true(plan_data["execution_graph"]["node_count"] == 4, "graph node count mismatch")
assert_true(plan_data["execution_graph"]["edge_count"] == 3, "graph edge count mismatch")

recovery = client.post("/admin/autonomous-workforce-orchestration/recovery", json={
    "orchestration_id": plan_data["plan"]["orchestration_id"],
    "failure_reason": "provider_timeout",
    "attempt_count": 1,
})
assert_true(recovery.status_code == 200, recovery.text)
recovery_data = recovery.json()
assert_true(recovery_data["success"] is True, "recovery success failed")
assert_true(recovery_data["retry_allowed"] is True, "retry should be allowed")
assert_true(recovery_data["next_action"] == "retry_prepared", "wrong recovery next action")
assert_true(recovery_data["live_external_call_executed"] is False, "recovery must not execute live call")
assert_true(recovery_data["credential_values_exposed"] is False, "recovery exposed credentials")

print("AUTONOMOUS_WORKFORCE_ORCHESTRATION_FOUNDATION_TEST_PASSED")
print({
    "foundation_layers": data["foundation_layers"],
    "packet_count": plan_data["plan"]["packet_count"],
    "graph_nodes": plan_data["execution_graph"]["node_count"],
    "graph_edges": plan_data["execution_graph"]["edge_count"],
    "recovery_next_action": recovery_data["next_action"],
})
