from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

status = client.get("/catalogue-entitlement-bridge/status").json()
assert status["catalogue_entitlement_bridge_ready"] is True
assert status["commercial_catalogue_count"] == 27

business_agents = client.get("/catalogue-entitlement-bridge/selectable-agents/business").json()
assert business_agents["available_count"] == 26
assert business_agents["head_agent_available"] is False

enterprise_agents = client.get("/catalogue-entitlement-bridge/selectable-agents/enterprise").json()
assert enterprise_agents["available_count"] == 27
assert enterprise_agents["head_agent_available"] is True

valid = client.post(
    "/catalogue-entitlement-bridge/validate-selection",
    json={
        "plan": "starter",
        "selected_agent_keys": ["seo_agent", "marketing_specialist_agent", "email_reply_agent"],
    },
).json()
assert valid["valid"] is True

blocked = client.post(
    "/catalogue-entitlement-bridge/validate-selection",
    json={
        "plan": "business",
        "selected_agent_keys": ["head_agent"],
    },
).json()
assert blocked["valid"] is False
assert blocked["enterprise_blocked_agent_keys"] == ["head_agent"]

packet = client.post(
    "/catalogue-entitlement-bridge/activation-packet",
    json={
        "plan": "starter",
        "selected_agent_keys": ["seo_agent", "marketing_specialist_agent", "email_reply_agent"],
    },
).json()
assert packet["activation_allowed"] is True
assert len(packet["active_agents"]) == 3
assert packet["client_access_limited_to_paid_selected_agents"] is True

print("CATALOGUE_ENTITLEMENT_BRIDGE_ROUTES_DIRECT_TESTS_PASSED")
print("commercial_catalogue_count", status["commercial_catalogue_count"])
print("business_available", business_agents["available_count"])
print("enterprise_available", enterprise_agents["available_count"])
print("packet_active_agents", len(packet["active_agents"]))
print("hidden_unpurchased", packet["client_hidden_agents_count"])
