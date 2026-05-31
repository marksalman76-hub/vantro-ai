
from backend.app.runtime.delegated_workforce_execution_runtime import (
    execute_delegated_workforce_plan,
)

plan = {
    "action_packets": [
        {
            "packet_id": "auto_safe_001",
            "recommended_agent": "marketing_specialist_agent",
            "implementation_action": "Create healthcare positioning strategy document draft",
            "risk_level": "medium",
            "approval_required": False,
        },
        {
            "packet_id": "auto_risky_001",
            "recommended_agent": "marketing_specialist_agent",
            "implementation_action": "Launch paid campaign and increase budget",
            "risk_level": "high",
            "approval_required": False,
        },
        {
            "packet_id": "auto_not_owned_001",
            "recommended_agent": "seo_agent",
            "implementation_action": "Create SEO topic cluster draft",
            "risk_level": "medium",
            "approval_required": False,
        },
    ]
}

result = execute_delegated_workforce_plan(
    implementation_plan=plan,
    owner_approved=False,
    client_owned_agents=["marketing_specialist_agent"],
    package_tier="business",
)

assert result["success"] is True
assert result["completed_count"] == 1
assert result["queued_count"] == 1
assert result["blocked_count"] == 1

completed = result["completed_results"][0]
assert completed["autonomous_governance"] is True
assert completed["autonomous_route"] == "autonomously_executed"
assert completed["performed_actual_action"] is True
assert completed["deliverable"]["asset_status"] == "created"

queued = result["queued_results"][0]
assert queued["autonomous_route"] == "queued_for_owner_approval"
assert queued["performed_actual_action"] is False

blocked = result["blocked_results"][0]
assert blocked["autonomous_route"] == "recommendation_only"
assert blocked["performed_actual_action"] is False

enterprise_result = execute_delegated_workforce_plan(
    implementation_plan=plan,
    owner_approved=False,
    client_owned_agents=[],
    package_tier="enterprise",
)

assert enterprise_result["success"] is True
assert enterprise_result["completed_count"] == 2
assert enterprise_result["queued_count"] == 1
assert enterprise_result["blocked_count"] == 0

print("AUTONOMOUS_WORKFORCE_RUNTIME_TEST_PASSED")
