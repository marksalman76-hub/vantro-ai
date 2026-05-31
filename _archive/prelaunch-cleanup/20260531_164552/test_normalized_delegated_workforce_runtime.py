
from backend.app.runtime.delegated_workforce_execution_runtime import execute_delegated_workforce_plan

plan = {
    "action_packets": [
        {
            "packet_id": "norm_runtime_001",
            "recommended_agent": "marketing_specialist_agent",
            "title": "4. Execution plan with concrete steps",
            "risk_level": "medium",
            "approval_required": False,
        },
        {
            "packet_id": "norm_runtime_002",
            "recommended_agent": "marketing_specialist_agent",
            "title": "Commission targeted healthcare technology market research and client interviews",
            "risk_level": "medium",
            "approval_required": False,
        },
        {
            "packet_id": "norm_runtime_003",
            "recommended_agent": "marketing_specialist_agent",
            "title": "Launch paid campaign and increase budget",
            "risk_level": "medium",
            "approval_required": False,
        },
    ]
}

result = execute_delegated_workforce_plan(
    implementation_plan=plan,
    owner_approved=False,
    client_owned_agents=["marketing_specialist_agent"],
    package_tier="enterprise",
)

assert result["success"] is True
assert result["normalization"]["normalized_count"] == 3
assert result["completed_count"] >= 2
assert result["queued_count"] >= 1

completed_actions = [
    item.get("completed_output", "")
    for item in result["completed_results"]
]
assert any("Created" in item for item in completed_actions)

for item in result["completed_results"]:
    assert item.get("normalization_applied") is True or item.get("real_execution") is True

print("NORMALIZED_DELEGATED_WORKFORCE_RUNTIME_TEST_PASSED")
