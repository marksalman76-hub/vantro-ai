from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

status = client.get("/real-agent-component-catalogue/status").json()
assert status["real_agent_component_catalogue_locked"] is True
assert status["commercial_catalogue_count"] == 27
assert status["visible_agent_count"] == 33
assert status["operational_component_count"] == 48

counts = client.get("/real-agent-component-catalogue/counts").json()["counts"]
assert counts["client_facing_agents"] == 27
assert counts["system_agents"] == 6

full = client.get("/real-agent-component-catalogue/full").json()
assert full["commercial_catalogue_count"] == 27
assert full["total_operational_component_count"] == 48

head = client.get("/real-agent-component-catalogue/component/head_agent").json()
assert head["found"] is True
assert head["component"]["enterprise_only"] is True

business = client.get("/real-agent-component-catalogue/client-selectable?plan=business").json()
assert business["count"] == 26
assert business["head_agent_available"] is False

enterprise = client.get("/real-agent-component-catalogue/client-selectable?plan=enterprise").json()
assert enterprise["count"] == 27
assert enterprise["head_agent_available"] is True

print("REAL_AGENT_COMPONENT_CATALOGUE_ROUTES_DIRECT_TESTS_PASSED")
print("commercial_catalogue_count", status["commercial_catalogue_count"])
print("visible_agent_count", status["visible_agent_count"])
print("operational_component_count", status["operational_component_count"])
print("business_selectable", business["count"])
print("enterprise_selectable", enterprise["count"])
