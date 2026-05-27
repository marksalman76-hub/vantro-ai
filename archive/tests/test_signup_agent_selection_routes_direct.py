from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

status = client.get("/signup-agent-selection/status").json()
assert status["signup_agent_selection_bridge_ready"] is True
assert status["uses_locked_27_agent_catalogue"] is True

starter = client.get("/signup-agent-selection/options/starter").json()
assert starter["max_selectable_agents"] == 3
assert starter["available_count"] == 26

enterprise = client.get("/signup-agent-selection/options/enterprise").json()
assert enterprise["max_selectable_agents"] == 27
assert enterprise["available_count"] == 27
assert enterprise["head_agent_available"] is True

valid = client.post(
    "/signup-agent-selection/validate",
    json={
        "plan": "starter",
        "selected_agent_keys": ["seo_agent", "marketing_specialist_agent", "email_reply_agent"],
    },
).json()
assert valid["valid"] is True
assert valid["activation_allowed"] is True

blocked = client.post(
    "/signup-agent-selection/validate",
    json={
        "plan": "business",
        "selected_agent_keys": ["head_agent"],
    },
).json()
assert blocked["valid"] is False
assert blocked["enterprise_blocked_agent_keys"] == ["head_agent"]

packet = client.post(
    "/signup-agent-selection/activation-packet",
    json={
        "plan": "starter",
        "selected_agent_keys": ["seo_agent", "marketing_specialist_agent", "email_reply_agent"],
    },
).json()
assert packet["status"] == "activation_packet_ready"
assert packet["selected_count"] == 3

print("SIGNUP_AGENT_SELECTION_ROUTES_DIRECT_TESTS_PASSED")
print("starter_available", starter["available_count"])
print("enterprise_available", enterprise["available_count"])
print("valid_selected", valid["selected_count"])
print("packet_selected", packet["selected_count"])
