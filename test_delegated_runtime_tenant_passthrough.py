
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.runtime.delegated_workforce_execution_runtime import execute_delegated_workforce_plan

plan = {
    "action_packets": [
        {
            "packet_id": "tenant_passthrough_001",
            "recommended_agent": "email_reply_agent",
            "title": "Send governed live Brevo execution verification email",
            "risk_level": "medium",
            "approval_required": False,
        }
    ]
}

runtime_result = execute_delegated_workforce_plan(
    implementation_plan=plan,
    owner_approved=True,
    client_owned_agents=["email_reply_agent"],
    package_tier="enterprise",
    connected_integrations=["email"],
    tenant_id="client_demo_001",
)

assert runtime_result["success"] is True
completed = runtime_result["completed_results"][0]
assert completed["deliverable"]["actions_performed"][0]["tenant_id"] == "client_demo_001"

client = TestClient(app)
response = client.post(
    "/delegated-workforce-execution",
    json={
        "implementation_plan": plan,
        "owner_approved": True,
        "client_owned_agents": ["email_reply_agent"],
        "package_tier": "enterprise",
        "connected_integrations": ["email"],
        "tenant_id": "client_demo_001",
    },
)

body = response.json()
assert body["success"] is True
completed_route = body["completed_results"][0]
assert completed_route["deliverable"]["actions_performed"][0]["tenant_id"] == "client_demo_001"

print("DELEGATED_RUNTIME_TENANT_PASSTHROUGH_TEST_PASSED")
