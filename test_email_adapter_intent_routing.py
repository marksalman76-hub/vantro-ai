
from backend.app.runtime.intelligent_action_packet_normalizer import normalize_action_packet

packet = {
    "packet_id": "email_route_001",
    "recommended_agent": "email_reply_agent",
    "title": "Send governed live Brevo execution verification email",
    "risk_level": "medium",
    "approval_required": False,
}

result = normalize_action_packet(packet)

assert result["execution_adapter_target"] == "stakeholder_interview_outreach_adapter"
assert "email" in result["implementation_action"].lower()
assert result["execution_type"] == "autonomous_safe_operational"
assert result["approval_required"] is False

print("EMAIL_ADAPTER_INTENT_ROUTING_TEST_PASSED")
