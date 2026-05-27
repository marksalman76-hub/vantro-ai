from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

reset = client.post("/one-time-agent-selection-lock/reset-for-tests").json()
assert reset["reset"] is True

status = client.get("/one-time-agent-selection-lock/status").json()
assert status["client_selects_once_per_package"] is True
assert status["selection_locked_after_activation"] is True

draft = client.post(
    "/one-time-agent-selection-lock/draft",
    json={
        "tenant_id": "tenant-test",
        "package_id": "package-starter-1",
        "plan": "starter",
        "selected_agent_keys": ["seo_agent", "marketing_specialist_agent", "email_reply_agent"],
    },
).json()
assert draft["status"] == "draft_created"
assert draft["draft"]["activation_allowed"] is True

activated = client.post(
    "/one-time-agent-selection-lock/activate",
    json={
        "tenant_id": "tenant-test",
        "package_id": "package-starter-1",
        "draft_id": draft["draft"]["draft_id"],
    },
).json()
assert activated["status"] == "activated"
assert activated["selection_locked"] is True
assert activated["client_can_change_selection"] is False

blocked = client.post(
    "/one-time-agent-selection-lock/draft",
    json={
        "tenant_id": "tenant-test",
        "package_id": "package-starter-1",
        "plan": "starter",
        "selected_agent_keys": ["crm_agent"],
    },
).json()
assert blocked["status"] == "blocked"
assert blocked["reason"] == "package_agent_selection_already_activated"

existing = client.get(
    "/one-time-agent-selection-lock/activated?tenant_id=tenant-test&package_id=package-starter-1"
).json()
assert existing["status"] == "found"
assert existing["client_can_change_selection"] is False

change = client.post(
    "/one-time-agent-selection-lock/request-change",
    json={
        "tenant_id": "tenant-test",
        "package_id": "package-starter-1",
        "requested_agent_keys": ["crm_agent"],
        "reason": "Client wants to swap.",
    },
).json()
assert change["status"] == "owner_admin_review_required"
assert change["client_can_change_selection"] is False

print("ONE_TIME_AGENT_SELECTION_LOCK_ROUTES_DIRECT_TESTS_PASSED")
print("activated_status", activated["status"])
print("active_agents", len(activated["activated_selection"]["active_agents"]))
print("blocked", blocked["status"], blocked["reason"])
print("change_status", change["status"])
