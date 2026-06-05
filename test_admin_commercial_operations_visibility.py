from backend.app.core.admin_commercial_operations_visibility import admin_commercial_operations_status

def assert_true(value, message):
    if not value:
        raise AssertionError(message)

status = admin_commercial_operations_status()

assert_true(status["success"], "status should succeed")
assert_true(status["commercial_operations_ready"], "commercial operations should be ready")
assert_true(status["operator_visibility_ready"], "operator visibility should be ready")
assert_true(status["refund_operations_visible"], "refund visibility missing")
assert_true(status["industry_agent_store_visible"], "industry store visibility missing")
assert_true(status["learning_vault_visible"], "learning vault visibility missing")
assert_true(status["billing_operations_visible"], "billing visibility missing")
assert_true(status["integration_operations_visible"], "integration visibility missing")
assert_true(status["launch_readiness_visible"], "launch readiness visibility missing")
assert_true(status["credential_values_exposed"] is False, "credentials must not be exposed")
assert_true(len(status["sections"]) >= 6, "commercial sections missing")
assert_true(len(status["next_operator_actions"]) >= 6, "operator actions missing")

print("ADMIN_COMMERCIAL_OPERATIONS_VISIBILITY_TEST_PASSED")
