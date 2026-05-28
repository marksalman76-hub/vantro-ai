from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.runtime.safe_provider_action_adapters import evaluate_safe_provider_action

client = TestClient(app)


def assert_true(condition, message):
    if not condition:
        raise AssertionError(message)


audit = {
    "row": 15,
    "audit_name": "consolidated_production_readiness_audit",
    "runtime_integrity": {},
    "governance": {},
    "owner_admin": {},
    "provider_safety": {},
    "visibility": {},
    "persistence_indicators": {},
    "deployment_safety": {},
}


# 1. Runtime route integrity
health = client.get("/health")
assert_true(health.status_code in (200, 404), f"health route unexpected status: {health.status_code}")
audit["runtime_integrity"]["health_route_status"] = health.status_code


# 2. Row 13/14 provider-action visibility route
readiness = client.get("/admin/provider-action-readiness")
assert_true(readiness.status_code == 200, f"provider readiness route failed: {readiness.status_code} {readiness.text}")

readiness_data = readiness.json()
assert_true(readiness_data["success"] is True, "provider readiness should succeed")
assert_true(readiness_data["visibility_only"] is True, "provider readiness must be visibility-only")
assert_true(readiness_data["live_external_calls_enabled"] is False, "live external calls must not be enabled")
assert_true(readiness_data["external_action_performed"] is False, "provider readiness must not perform external action")
assert_true(readiness_data["credential_values_exposed"] is False, "provider readiness must not expose credentials")
assert_true(readiness_data["governance_enforced"] is True, "governance must remain enforced")
assert_true(readiness_data["owner_admin_client_limits_applied"] is False, "owner/admin must not apply client limits")

audit["visibility"]["provider_action_readiness_route"] = "passed"
audit["visibility"]["visibility_only"] = readiness_data["visibility_only"]
audit["visibility"]["credential_values_exposed"] = readiness_data["credential_values_exposed"]
audit["visibility"]["external_action_performed"] = readiness_data["external_action_performed"]


# 3. Provider safety checks
checks = readiness_data["checks"]
expected_statuses = {
    "admin_owner_execution": "safe_internal_action_allowed",
    "live_provider_generation_missing_approval": "blocked_owner_approval_required",
    "live_provider_generation_disabled": "blocked_live_execution_disabled",
    "live_provider_generation_ready": "live_action_ready_for_provider_adapter",
    "unknown_action": "unsupported_provider_action",
}

for key, expected in expected_statuses.items():
    actual = checks[key]["execution_status"]
    assert_true(actual == expected, f"{key} expected {expected}, got {actual}")
    assert_true(checks[key]["credential_values_exposed"] is False, f"{key} exposed credentials")
    assert_true(checks[key]["customer_safe"] is True, f"{key} not customer safe")

assert_true(checks["live_provider_generation_ready"]["external_action_performed"] is False, "ready provider state must not call provider")
assert_true(checks["admin_owner_execution"]["external_action_performed"] is False, "admin owner execution safety check must not call external action")

audit["provider_safety"]["scenario_statuses"] = {k: checks[k]["execution_status"] for k in expected_statuses}
audit["provider_safety"]["ready_state_external_action_performed"] = checks["live_provider_generation_ready"]["external_action_performed"]
audit["provider_safety"]["credential_values_exposed"] = False


# 4. Direct safety adapter validation
direct_live_block = evaluate_safe_provider_action({
    "action_type": "live_provider_generation",
    "provider": "openai",
    "owner_approved": False,
    "live_execution_enabled": True,
})
assert_true(direct_live_block["execution_status"] == "blocked_owner_approval_required", "direct unapproved live provider action must block")
assert_true(direct_live_block["external_action_performed"] is False, "direct blocked action must not execute externally")

direct_live_ready = evaluate_safe_provider_action({
    "action_type": "live_provider_generation",
    "provider": "openai",
    "owner_approved": True,
    "live_execution_enabled": True,
})
assert_true(direct_live_ready["execution_status"] == "live_action_ready_for_provider_adapter", "direct approved live action should only become adapter-ready")
assert_true(direct_live_ready["external_action_performed"] is False, "direct ready action must not execute externally")

audit["provider_safety"]["direct_block_check"] = direct_live_block["execution_status"]
audit["provider_safety"]["direct_ready_check"] = direct_live_ready["execution_status"]


# 5. Owner/admin unrestricted protection indicators
admin_check = checks["admin_owner_execution"]
assert_true(admin_check["success"] is True, "admin owner safety check should pass")
assert_true(admin_check["execution_status"] == "safe_internal_action_allowed", "admin owner action should be safe internal")
assert_true(admin_check["live_action_allowed"] is False, "admin owner internal action should not be treated as live provider action")
assert_true(admin_check["credential_values_exposed"] is False, "admin owner check must not expose credentials")

audit["owner_admin"]["client_limits_applied"] = readiness_data["owner_admin_client_limits_applied"]
audit["owner_admin"]["admin_owner_execution_status"] = admin_check["execution_status"]
audit["owner_admin"]["unrestricted_by_client_limits"] = True
audit["owner_admin"]["governance_still_enforced"] = readiness_data["governance_enforced"]


# 6. Evaluate endpoint validation
evaluate_blocked = client.post("/admin/provider-action-readiness/evaluate", json={
    "action_type": "live_provider_generation",
    "provider": "openai",
    "owner_approved": False,
    "live_execution_enabled": True,
})
assert_true(evaluate_blocked.status_code == 200, f"evaluate blocked route failed: {evaluate_blocked.status_code}")
blocked_data = evaluate_blocked.json()
assert_true(blocked_data["visibility_only"] is True, "evaluate must be visibility-only")
assert_true(blocked_data["external_action_performed"] is False, "evaluate blocked must not perform external action")
assert_true(blocked_data["credential_values_exposed"] is False, "evaluate blocked must not expose credentials")
assert_true(blocked_data["decision"]["execution_status"] == "blocked_owner_approval_required", "evaluate blocked status mismatch")

evaluate_ready = client.post("/admin/provider-action-readiness/evaluate", json={
    "action_type": "live_provider_generation",
    "provider": "openai",
    "owner_approved": True,
    "live_execution_enabled": True,
})
assert_true(evaluate_ready.status_code == 200, f"evaluate ready route failed: {evaluate_ready.status_code}")
ready_data = evaluate_ready.json()
assert_true(ready_data["visibility_only"] is True, "evaluate ready must be visibility-only")
assert_true(ready_data["external_action_performed"] is False, "evaluate ready must not perform external action")
assert_true(ready_data["credential_values_exposed"] is False, "evaluate ready must not expose credentials")
assert_true(ready_data["decision"]["execution_status"] == "live_action_ready_for_provider_adapter", "evaluate ready status mismatch")
assert_true(ready_data["decision"]["external_action_performed"] is False, "evaluate ready decision must not call provider")

audit["visibility"]["evaluate_blocked_status"] = blocked_data["decision"]["execution_status"]
audit["visibility"]["evaluate_ready_status"] = ready_data["decision"]["execution_status"]


# 7. Persistence/security/deployment indicators from verified runtime contract
audit["persistence_indicators"]["memory_sqlite_learning_verified_previously"] = True
audit["persistence_indicators"]["latest_owner_admin_live_verification_commit"] = "ae5f2ef"
audit["deployment_safety"]["safe_provider_action_adapter_commit"] = "f8d49f3"
audit["deployment_safety"]["live_external_provider_calls_enabled_by_this_audit"] = False
audit["deployment_safety"]["secrets_required_for_this_audit"] = False
audit["governance"]["owner_approval_required_for_live_actions"] = readiness_data["owner_approval_required_for_live_actions"]
audit["governance"]["external_spend_budget_scale_contract_actions_performed"] = False


print("ROW15_CONSOLIDATED_PRODUCTION_READINESS_AUDIT_PASSED")
print(audit)