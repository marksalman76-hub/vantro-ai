
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.runtime.durable_external_action_records import record_external_actions

client = TestClient(app)

record_external_actions(
    tenant_id="route_external_test",
    execution_id="exec_route_test",
    packet_id="packet_route_test",
    assigned_agent="crm_ai_agent",
    deliverable={
        "deliverable_id": "deliverable_route_test",
        "adapter": "stakeholder_interview_outreach_adapter",
        "actions_performed": [
            {
                "type": "crm_task_created",
                "status": "executed",
                "provider": "governed_crm_runtime",
                "task_id": "crm_task_route_test",
            }
        ],
    },
)

blocked = client.get(
    "/admin/external-action-records?tenant_id=route_external_test",
    headers={"x-actor-role": "client"},
)
assert blocked.json()["success"] is False

ready = client.get(
    "/admin/external-action-records/readiness",
    headers={"x-actor-role": "owner_admin"},
)
assert ready.json()["success"] is True

records = client.get(
    "/admin/external-action-records?tenant_id=route_external_test&limit=5",
    headers={"x-actor-role": "owner_admin"},
)
body = records.json()
assert body["success"] is True
assert body["count"] >= 1
assert body["records"][0]["provider_reference_id"] == "crm_task_route_test"

print("EXTERNAL_ACTION_RECORD_ROUTES_TEST_PASSED")
