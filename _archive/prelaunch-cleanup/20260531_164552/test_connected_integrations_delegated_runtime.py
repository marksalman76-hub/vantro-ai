
from backend.app.runtime.delegated_workforce_execution_runtime import execute_delegated_workforce_plan

plan = {
    "action_packets": [
        {
            "packet_id": "external_connected_001",
            "recommended_agent": "marketing_specialist_agent",
            "title": "Commission targeted healthcare technology market research and client interviews",
            "risk_level": "medium",
            "approval_required": False,
        }
    ]
}

result = execute_delegated_workforce_plan(
    implementation_plan=plan,
    owner_approved=False,
    client_owned_agents=["marketing_specialist_agent"],
    package_tier="enterprise",
    connected_integrations=["email", "crm", "calendar"],
)

assert result["success"] is True
assert result["external_integration_count"] == 3
assert result["completed_count"] == 1

completed = result["completed_results"][0]
assert completed["performed_actual_action"] is True
assert completed["deliverable"]["actions_performed"]
assert completed["deliverable"]["adapter"] == "stakeholder_interview_outreach_adapter"

# External readiness/bridge values live inside deliverable/action result chain.
assert completed["external_action_performed"] is True
assert completed["live_external_call_executed"] is True

print("CONNECTED_INTEGRATIONS_DELEGATED_RUNTIME_TEST_PASSED")
