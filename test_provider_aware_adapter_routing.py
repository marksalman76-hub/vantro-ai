
from backend.app.runtime.action_adapter_execution_layer import classify_action_adapter, execute_action_adapter

packet = {
    "implementation_action": "Send governed live email verification through connected email provider",
}

assert classify_action_adapter({**packet, "connected_integrations": ["email"]}) == "stakeholder_interview_outreach_adapter"

result = execute_action_adapter(
    packet,
    tenant_id="client_demo_001",
    connected_integrations=["email"],
    owner_approved=True,
)

assert result["adapter"] == "stakeholder_interview_outreach_adapter"
assert result["performed_actual_action"] is True
assert result.get("actions_performed")

print("PROVIDER_AWARE_ADAPTER_ROUTING_TEST_PASSED")
