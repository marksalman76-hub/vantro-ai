from backend.app.runtime.delegated_workforce_execution_runtime import (
    execute_delegated_workforce_plan,
)

sample_plan = {
    "action_packets": [
        {
            "packet_id": "packet_1",
            "recommended_agent": "security_compliance_agent",
            "approval_required": True,
            "risk_level": "high",
        },
        {
            "packet_id": "packet_2",
            "recommended_agent": "analytics_optimisation_agent",
            "approval_required": False,
            "risk_level": "medium",
        },
        {
            "packet_id": "packet_3",
            "recommended_agent": "lead_generator_appointment_setter_agent",
            "approval_required": False,
            "risk_level": "medium",
        },
    ]
}

result = execute_delegated_workforce_plan(
    implementation_plan=sample_plan,
    owner_approved=True,
    client_owned_agents=[
        "analytics_optimisation_agent",
    ],
    package_tier="starter",
)

assert result["success"] is True
assert result["completed_count"] == 1
assert result["blocked_count"] == 2

blocked = result["blocked_results"][0]

assert blocked["delegate_execution"] == "blocked"
assert blocked["recommendation_visibility"] is True
assert blocked["upsell_visibility"] is True
assert blocked["execution_preview"] == "allowed"

completed = result["completed_results"][0]

assert completed["assigned_agent"] == "analytics_optimisation_agent"
assert completed["execution_status"] == "completed"

print("DELEGATED_WORKFORCE_EXECUTION_RUNTIME_TEST_PASSED")
print({
    "completed_count": result["completed_count"],
    "blocked_count": result["blocked_count"],
})
