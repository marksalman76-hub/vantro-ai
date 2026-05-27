import requests

BASE = "https://ecommerce-ai-agent-platform-2ir4zecmi.vercel.app"

selected = ["seo_agent", "marketing_specialist_agent", "email_reply_agent"]

print("Testing:", BASE)

r = requests.post(
    f"{BASE}/api/signup-agent-selection/validate",
    json={
        "plan": "starter",
        "selected_agent_keys": selected,
    },
    timeout=30,
)
print("\n=== validate ===")
print("status", r.status_code)
print(r.text[:1200])
r.raise_for_status()

data = r.json()
assert data["valid"] is True
assert data["activation_allowed"] is True
assert data["selected_count"] == 3

r = requests.post(
    f"{BASE}/api/signup-agent-selection/activation-packet",
    json={
        "plan": "starter",
        "selected_agent_keys": selected,
    },
    timeout=30,
)
print("\n=== activation packet ===")
print("status", r.status_code)
print(r.text[:1600])
r.raise_for_status()

packet = r.json()
assert packet["status"] == "activation_packet_ready"
assert packet["selected_count"] == 3
assert packet["packet"]["activation_allowed"] is True
assert packet["packet"]["client_access_limited_to_paid_selected_agents"] is True
assert len(packet["packet"]["client_visible_agents"]) == 3
assert packet["packet"]["client_hidden_agents_count"] == 24
assert packet["credential_values_exposed"] is False

print("\nLIVE_SIGNUP_AGENT_ACTIVATION_PACKET_TEST_PASSED")
print("selected", packet["packet"]["client_visible_agents"])
print("hidden_unpurchased", packet["packet"]["client_hidden_agents_count"])