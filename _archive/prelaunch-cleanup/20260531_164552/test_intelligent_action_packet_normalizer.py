
from backend.app.runtime.intelligent_action_packet_normalizer import (
    normalize_action_packet,
    normalize_implementation_plan,
)

bad_heading = {
    "packet_id": "bad_001",
    "recommended_agent": "marketing_specialist_agent",
    "title": "4. Execution plan with concrete steps",
    "risk_level": "medium",
}

normalised_heading = normalize_action_packet(bad_heading)
assert normalised_heading["normalization_applied"] is True
assert "checklist" in normalised_heading["implementation_action"].lower()
assert normalised_heading["execution_type"] == "autonomous_safe_operational"
assert normalised_heading["safe_action_score"] > 0.8

vague_strategy = {
    "packet_id": "bad_002",
    "recommended_agent": "marketing_specialist_agent",
    "title": "b. Capability building & strategic partnerships",
    "risk_level": "medium",
}

normalised_strategy = normalize_action_packet(vague_strategy)
assert "partner" in normalised_strategy["implementation_action"].lower()
assert normalised_strategy["execution_adapter_target"] in {
    "general_operational_task_adapter",
    "stakeholder_interview_outreach_adapter",
}

safe_action = {
    "packet_id": "safe_001",
    "recommended_agent": "marketing_specialist_agent",
    "title": "Commission targeted healthcare technology market research and client interviews",
    "risk_level": "medium",
}

normalised_safe = normalize_action_packet(safe_action)
assert "outreach draft" in normalised_safe["implementation_action"].lower()
assert normalised_safe["execution_adapter_target"] == "stakeholder_interview_outreach_adapter"
assert normalised_safe["approval_required"] is False

risky_action = {
    "packet_id": "risky_001",
    "recommended_agent": "marketing_specialist_agent",
    "title": "Launch paid campaign and increase budget",
    "risk_level": "medium",
}

normalised_risky = normalize_action_packet(risky_action)
assert normalised_risky["approval_required"] is True
assert normalised_risky["execution_type"] == "approval_required"

plan = normalize_implementation_plan({
    "action_packets": [bad_heading, vague_strategy, safe_action, risky_action]
})

assert plan["normalization"]["input_count"] == 4
assert plan["normalization"]["normalized_count"] == 4
assert plan["normalization"]["executable_count"] == 3
assert plan["normalization"]["approval_required_count"] == 1

print("INTELLIGENT_ACTION_PACKET_NORMALIZER_TEST_PASSED")
