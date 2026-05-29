
from backend.app.runtime.external_action_readiness_classifier import classify_external_action_readiness
from backend.app.runtime.action_adapter_execution_layer import execute_action_adapter

ready = classify_external_action_readiness(
    adapter="stakeholder_interview_outreach_adapter",
    connected_integrations=["email"],
    owner_approved=True,
)

assert ready["success"] is True
assert ready["external_action_ready"] is True
assert ready["live_execution_allowed"] is True
assert ready["missing_connections"] == []

blocked = classify_external_action_readiness(
    adapter="stakeholder_interview_outreach_adapter",
    connected_integrations=[],
    owner_approved=True,
)

assert blocked["external_action_ready"] is False
assert "email" in blocked["missing_connections"]

result = execute_action_adapter(
    {
        "implementation_action": "Send governed live email verification through connected email provider",
        "execution_adapter_target": "stakeholder_interview_outreach_adapter",
    },
    tenant_id="client_demo_001",
    connected_integrations=["email"],
    owner_approved=True,
)

assert result["adapter"] == "stakeholder_interview_outreach_adapter"
assert result["external_action_ready"] is True
assert "real_external_execution" in result

print("STAKEHOLDER_EXTERNAL_ACTION_READINESS_TEST_PASSED")
