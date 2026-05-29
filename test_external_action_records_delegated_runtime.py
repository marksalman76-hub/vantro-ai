
from backend.app.runtime.delegated_workforce_execution_runtime import execute_delegated_workforce_plan
from backend.app.runtime.durable_external_action_records import list_external_action_records

plan = {
    "action_packets": [
        {
            "packet_id": "external_records_runtime_001",
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
assert result["completed_count"] == 1

completed = result["completed_results"][0]
assert completed["external_action_performed"] is True
assert completed["live_external_call_executed"] is True
assert completed["external_action_records_persisted"] is True
assert completed["external_action_record_count"] >= 3

records = list_external_action_records(tenant_id="owner_admin", limit=20)
assert records["success"] is True
assert any(r.get("packet_id") == "external_records_runtime_001" for r in records["records"])

print("EXTERNAL_ACTION_RECORDS_DELEGATED_RUNTIME_TEST_PASSED")
