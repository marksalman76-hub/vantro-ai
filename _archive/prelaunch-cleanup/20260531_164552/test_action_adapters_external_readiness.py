
from backend.app.runtime.action_adapter_execution_layer import execute_action_adapter

packet = {
    "implementation_action": "Conduct stakeholder interviews with healthcare providers and payers",
}

fallback = execute_action_adapter(
    packet,
    tenant_id="tenant_test",
    connected_integrations=["email"],
)
assert fallback["performed_actual_action"] is True
assert fallback["external_action_ready"] is False
assert fallback["internal_fallback_used"] is True
assert "crm" in fallback["missing_connections"]
assert "calendar" in fallback["missing_connections"]

ready = execute_action_adapter(
    packet,
    tenant_id="tenant_test",
    connected_integrations=["email", "crm", "calendar"],
)
assert ready["performed_actual_action"] is True
assert ready["external_action_ready"] is True
assert ready["internal_fallback_used"] is False
assert ready["external_readiness"]["route"] == "external_action_ready"

risky = execute_action_adapter(
    {"implementation_action": "Launch paid campaign and increase budget"},
    tenant_id="tenant_test",
    connected_integrations=["ads"],
    owner_approved=False,
)
assert risky["owner_approval_required"] is True
assert risky["external_action_ready"] is False
assert risky["external_readiness"]["route"] == "owner_approval_required"

print("ACTION_ADAPTERS_EXTERNAL_READINESS_TEST_PASSED")
