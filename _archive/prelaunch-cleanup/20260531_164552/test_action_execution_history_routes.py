
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.runtime.persistent_action_execution_history import record_action_execution

client = TestClient(app)

record_action_execution(
    tenant_id="route_test",
    packet_id="route_packet_001",
    assigned_agent="marketing_specialist_agent",
    execution_payload={
        "execution_status": "autonomously_executed",
        "performed_actual_action": True,
        "deliverable": {
            "adapter": "stakeholder_interview_outreach_adapter",
            "actions_performed": [{"type": "email_draft_created", "status": "created"}],
        },
    },
)

blocked = client.get(
    "/admin/action-execution-history?tenant_id=route_test",
    headers={"x-actor-role": "client"},
)
assert blocked.json()["success"] is False

ready = client.get(
    "/admin/action-execution-history/readiness",
    headers={"x-actor-role": "owner_admin"},
)
assert ready.json()["success"] is True

history = client.get(
    "/admin/action-execution-history?tenant_id=route_test&limit=5",
    headers={"x-actor-role": "owner_admin"},
)
body = history.json()
assert body["success"] is True
assert body["count"] >= 1
assert body["records"][0]["tenant_id"] == "route_test"

print("ACTION_EXECUTION_HISTORY_ROUTES_TEST_PASSED")
