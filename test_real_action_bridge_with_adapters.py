
from backend.app.runtime.real_action_execution_bridge import execute_real_action_packet

interview_packet = {
    "packet_id": "adapter_bridge_001",
    "assigned_agent": "marketing_specialist_agent",
    "implementation_action": "Conduct stakeholder interviews with healthcare providers and payers",
    "risk_level": "medium",
}

result = execute_real_action_packet(interview_packet, tenant_id="tenant_test")

assert result["success"] is True
assert result["performed_actual_action"] is True
assert result["execution_status"] == "adapter_action_executed"
assert result["adapter"] == "stakeholder_interview_outreach_adapter"
assert len(result["actions_performed"]) >= 2
assert result["deliverable"]["actions_performed"][0]["type"] == "email_draft_created"

risky_packet = {
    "packet_id": "adapter_bridge_risky_001",
    "assigned_agent": "marketing_specialist_agent",
    "implementation_action": "Launch paid campaign and increase budget",
    "risk_level": "high",
}

risky_result = execute_real_action_packet(risky_packet, tenant_id="tenant_test", owner_approved=False)

assert risky_result["performed_actual_action"] is False
assert risky_result["owner_approval_required"] is True
assert risky_result["execution_status"] == "blocked_owner_approval_required"

print("REAL_ACTION_BRIDGE_WITH_ADAPTERS_TEST_PASSED")
