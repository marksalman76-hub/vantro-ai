
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

response = client.post(
    "/delegated-workforce-execution",
    json={
        "implementation_plan": {
            "action_packets": [
                {
                    "packet_id": "route_connected_001",
                    "recommended_agent": "marketing_specialist_agent",
                    "title": "Commission targeted healthcare technology market research and client interviews",
                    "risk_level": "medium",
                    "approval_required": False,
                }
            ]
        },
        "owner_approved": False,
        "client_owned_agents": ["marketing_specialist_agent"],
        "package_tier": "enterprise",
        "connected_integrations": ["email", "crm", "calendar"],
    },
)

body = response.json()
assert body["success"] is True
assert body["connected_integrations"] == ["email", "crm", "calendar"]
assert body["external_integration_count"] == 3
assert body["completed_count"] == 1

completed = body["completed_results"][0]
assert completed["external_action_performed"] is True
assert completed["live_external_call_executed"] is True

print("BACKEND_DELEGATED_ROUTE_CONNECTED_INTEGRATIONS_TEST_PASSED")
