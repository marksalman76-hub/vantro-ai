
from backend.app.runtime.delegated_workforce_execution_runtime import (
    execute_delegated_workforce_plan,
)

plan = {
    "action_packets": [
        {
            "packet_id": "packet_001",
            "recommended_agent": "marketing_specialist_agent",
            "implementation_action": "Create healthcare positioning strategy document",
            "risk_level": "medium",
            "approval_required": False,
        },
        {
            "packet_id": "packet_002",
            "recommended_agent": "marketing_specialist_agent",
            "implementation_action": "Launch paid campaign and increase budget",
            "risk_level": "high",
            "approval_required": True,
        }
    ]
}

result = execute_delegated_workforce_plan(
    implementation_plan=plan,
    owner_approved=False,
    client_owned_agents=["marketing_specialist_agent"],
    package_tier="enterprise",
)

assert result["success"] is True
assert result["completed_count"] >= 1

completed = result["completed_results"][0]

assert completed["real_execution"] is True
assert completed["performed_actual_action"] is True
assert completed["deliverable"]["asset_status"] == "created"

print("REAL_WORKFORCE_EXECUTION_RUNTIME_TEST_PASSED")
