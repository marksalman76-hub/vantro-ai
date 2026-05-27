
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

tenant_id = "test-runtime-entitlement-hydration-routes-001"

status = client.get("/runtime-entitlement-hydration/status")
assert status.status_code == 200
status_json = status.json()
assert status_json["runtime_entitlement_hydration_bridge_ready"] is True
assert status_json["credential_values_exposed"] is False

owner = client.post(
    "/runtime-entitlement-hydration/check",
    json={"tenant_id": tenant_id, "agent_id": "head_agent"},
    headers={"x-actor-role": "owner_admin"},
)
assert owner.status_code == 200
owner_json = owner.json()
assert owner_json["success"] is True
assert owner_json["execution_allowed"] is True
assert owner_json["status"] == "owner_admin_unrestricted"

missing_activation = client.post(
    "/runtime-entitlement-hydration/check",
    json={"tenant_id": tenant_id, "agent_id": "seo_agent"},
    headers={"x-actor-role": "client"},
)
assert missing_activation.status_code == 200
missing_activation_json = missing_activation.json()
assert missing_activation_json["success"] is False
assert missing_activation_json["error"] == "activation_state_not_found"

seed = client.post(
    "/runtime-entitlement-hydration/seed",
    json={
        "tenant_id": tenant_id,
        "package_id": "business",
        "selected_agents": ["seo_agent", "email_reply_agent"],
    },
    headers={"x-actor-role": "system"},
)
assert seed.status_code == 200
seed_json = seed.json()
assert seed_json["success"] is True
assert seed_json["status"] == "activated"

approved = client.post(
    "/runtime-entitlement-hydration/check",
    json={"tenant_id": tenant_id, "agent_id": "seo_agent"},
    headers={"x-actor-role": "client"},
)
assert approved.status_code == 200
approved_json = approved.json()
assert approved_json["success"] is True
assert approved_json["execution_allowed"] is True
assert approved_json["status"] == "approved"

blocked = client.post(
    "/runtime-entitlement-hydration/check",
    json={"tenant_id": tenant_id, "agent_id": "head_agent"},
    headers={"x-actor-role": "client"},
)
assert blocked.status_code == 200
blocked_json = blocked.json()
assert blocked_json["success"] is False
assert blocked_json["execution_allowed"] is False
assert blocked_json["error"] == "requested_agent_not_activated"
assert blocked_json["next_stage"] == "owner_admin_review_required"

print("RUNTIME_ENTITLEMENT_HYDRATION_BRIDGE_ROUTES_TESTS_PASSED")
print("status_ready", status_json["runtime_entitlement_hydration_bridge_ready"])
print("owner_status", owner_json["status"])
print("missing_activation_error", missing_activation_json["error"])
print("seed_status", seed_json["status"])
print("approved_status", approved_json["status"])
print("blocked_error", blocked_json["error"])
