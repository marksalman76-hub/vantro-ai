
from backend.app.runtime.delegated_workforce_execution_runtime import execute_delegated_workforce_plan
from backend.app.runtime.persistent_action_execution_history import list_action_execution_history

plan = {
    "action_packets": [
        {
            "packet_id": "history_auto_001",
            "recommended_agent": "marketing_specialist_agent",
            "implementation_action": "Conduct stakeholder interviews with healthcare providers and payers",
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
)

assert result["success"] is True
assert result["completed_count"] == 1

completed = result["completed_results"][0]
assert completed["performed_actual_action"] is True
assert completed["history_persisted"] is True
assert completed["history_id"]

history = list_action_execution_history(tenant_id="owner_admin", limit=10)
assert history["success"] is True
assert history["count"] >= 1
assert any(r.get("packet_id") == "history_auto_001" for r in history["records"])

print("ACTION_HISTORY_WORKFORCE_RUNTIME_TEST_PASSED")
