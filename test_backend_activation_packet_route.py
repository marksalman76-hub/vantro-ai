
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

response = client.post(
    "/signup-agent-selection/activation-packet",
    json={
        "tenant_id": "client_demo_001",
        "plan": "starter",
        "selected_agents": ["marketing_specialist_agent", "head_agent"],
    },
)

assert response.status_code == 200
body = response.json()

assert body["success"] is True
assert body["profile"] == "backend_signup_activation_packet_runtime_v1"
assert body["tenant_id"] == "client_demo_001"
assert body["package_tier"] == "starter"
assert body["activated_agents"] == ["marketing_specialist_agent"]
assert body["enterprise_only_agents_blocked"] == ["head_agent"]
assert body["fallback_required"] is False
assert body["credential_values_exposed"] is False

print("BACKEND_ACTIVATION_PACKET_ROUTE_TEST_PASSED")
