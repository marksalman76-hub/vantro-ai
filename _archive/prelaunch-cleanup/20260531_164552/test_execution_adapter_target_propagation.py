
from backend.app.runtime.action_adapter_execution_layer import execute_action_adapter

packet = {
    "implementation_action": "Send governed live email verification through connected email provider",
    "execution_adapter_target": "stakeholder_interview_outreach_adapter",
}

result = execute_action_adapter(
    packet,
    tenant_id="tenant_test",
    connected_integrations=["email"],
    owner_approved=True,
)

assert result["adapter"] == "stakeholder_interview_outreach_adapter"
assert result["external_readiness"]["adapter"] == "stakeholder_interview_outreach_adapter"
assert result["performed_actual_action"] is True

print("EXECUTION_ADAPTER_TARGET_PROPAGATION_TEST_PASSED")
