
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

tenant_id = "test-governed-activation-routes-001"

status = client.get("/governed-activation-persistence/status")
assert status.status_code == 200
status_json = status.json()
assert status_json["governed_activation_persistence_ready"] is True
assert status_json["credential_values_exposed"] is False

persist = client.post(
    "/governed-activation-persistence/persist",
    json={
        "tenant_id": tenant_id,
        "package_id": "business",
        "selected_agents": ["seo_agent", "email_reply_agent", "marketing_specialist_agent"],
    },
    headers={"x-actor-role": "system"},
)
assert persist.status_code == 200
persist_json = persist.json()
assert persist_json["success"] is True
assert persist_json["status"] == "activated"

hydrate = client.get(f"/governed-activation-persistence/hydrate/{tenant_id}")
assert hydrate.status_code == 200
hydrate_json = hydrate.json()
assert hydrate_json["success"] is True
assert hydrate_json["status"] == "found"
assert hydrate_json["activation_locked"] is True

runtime = client.get(f"/governed-activation-persistence/runtime-entitlements/{tenant_id}")
assert runtime.status_code == 200
runtime_json = runtime.json()
assert runtime_json["success"] is True
assert runtime_json["runtime_entitlements"]["agent_execution_allowed"] is True

blocked = client.post(
    "/governed-activation-persistence/persist",
    json={
        "tenant_id": tenant_id,
        "package_id": "business",
        "selected_agents": ["seo_agent"],
    },
    headers={"x-actor-role": "client"},
)
assert blocked.status_code == 200
blocked_json = blocked.json()
assert blocked_json["success"] is False
assert blocked_json["status"] == "blocked"
assert blocked_json["next_stage"] == "owner_admin_review_required"

change = client.post(
    "/governed-activation-persistence/change-request",
    json={
        "tenant_id": tenant_id,
        "requested_agents": ["seo_agent", "email_reply_agent"],
        "reason": "Client requested package adjustment.",
    },
    headers={"x-actor-role": "client"},
)
assert change.status_code == 200
change_json = change.json()
assert change_json["success"] is True
assert change_json["status"] == "owner_admin_review_required"

request_id = change_json["change_request"]["request_id"]

approved = client.post(
    "/governed-activation-persistence/change-request/approve",
    json={"request_id": request_id},
    headers={"x-actor-role": "owner_admin"},
)
assert approved.status_code == 200
approved_json = approved.json()
assert approved_json["success"] is True
assert approved_json["status"] == "approved"

reconcile = client.get(f"/governed-activation-persistence/reconcile/{tenant_id}")
assert reconcile.status_code == 200
reconcile_json = reconcile.json()
assert reconcile_json["success"] is True
assert reconcile_json["status"] == "reconciled"

ledger = client.get(f"/governed-activation-persistence/audit-ledger?tenant_id={tenant_id}")
assert ledger.status_code == 200
ledger_json = ledger.json()
assert ledger_json["success"] is True
assert ledger_json["event_count"] >= 4
assert ledger_json["credential_values_exposed"] is False

print("GOVERNED_ACTIVATION_PERSISTENCE_ROUTES_TESTS_PASSED")
print("status_ready", status_json["governed_activation_persistence_ready"])
print("persist_status", persist_json["status"])
print("hydrate_status", hydrate_json["status"])
print("runtime_status", runtime_json["status"])
print("blocked_status", blocked_json["status"])
print("change_status", change_json["status"])
print("approved_status", approved_json["status"])
print("reconcile_status", reconcile_json["status"])
print("ledger_event_count", ledger_json["event_count"])
