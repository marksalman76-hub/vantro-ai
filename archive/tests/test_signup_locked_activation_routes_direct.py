from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

reset = client.post("/one-time-agent-selection-lock/reset-for-tests").json()
assert reset["reset"] is True

status = client.get("/signup-locked-activation/status").json()
assert status["signup_locked_activation_bridge_ready"] is True

draft = client.post(
    "/signup-locked-activation/draft",
    json={
        "tenant_id": "tenant-test",
        "package_id": "package-starter-1",
        "plan": "starter",
        "selected_agent_keys": ["seo_agent", "marketing_specialist_agent", "email_reply_agent"],
    },
).json()
assert draft["status"] == "draft_created"

activated = client.post(
    "/signup-locked-activation/activate",
    json={
        "tenant_id": "tenant-test",
        "package_id": "package-starter-1",
        "draft_id": draft["draft"]["draft_id"],
    },
).json()
assert activated["status"] == "activated"
assert activated["selection_locked"] is True
assert activated["client_can_change_selection"] is False

existing = client.get(
    "/signup-locked-activation/selection-status?tenant_id=tenant-test&package_id=package-starter-1"
).json()
assert existing["status"] == "found"
assert existing["selection_locked"] is True

blocked = client.post(
    "/signup-locked-activation/draft",
    json={
        "tenant_id": "tenant-test",
        "package_id": "package-starter-1",
        "plan": "starter",
        "selected_agent_keys": ["crm_agent"],
    },
).json()
assert blocked["status"] == "blocked"

change = client.post(
    "/signup-locked-activation/request-change",
    json={
        "tenant_id": "tenant-test",
        "package_id": "package-starter-1",
        "requested_agent_keys": ["crm_agent"],
        "reason": "Client wants to change agents.",
    },
).json()
assert change["status"] == "owner_admin_review_required"

print("SIGNUP_LOCKED_ACTIVATION_ROUTES_DIRECT_TESTS_PASSED")
print("draft_status", draft["status"])
print("activated_status", activated["status"])
print("existing_status", existing["status"])
print("blocked_status", blocked["status"])
print("change_status", change["status"])
