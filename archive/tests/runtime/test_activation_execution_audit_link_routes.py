
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

tenant_id = "test-activation-execution-audit-routes-001"

status = client.get("/activation-execution-audit/status")
assert status.status_code == 200
status_json = status.json()
assert status_json["activation_execution_audit_link_ready"] is True
assert status_json["credential_values_exposed"] is False

record = client.post(
    "/activation-execution-audit/record",
    json={
        "tenant_id": tenant_id,
        "requested_agent": "seo_agent",
        "actor_role": "client",
        "execution_allowed": True,
        "source": "route_test",
        "entitlement_check": {
            "success": True,
            "status": "approved",
            "entitlement_source": "governed_activation_persistence",
            "credential_values_exposed": False,
            "customer_safe": True,
        },
    },
)
assert record.status_code == 200
record_json = record.json()
assert record_json["decision_status"] == "approved"
assert record_json["credential_values_exposed"] is False

blocked = client.post(
    "/activation-execution-audit/record",
    json={
        "tenant_id": tenant_id,
        "requested_agent": "head_agent",
        "actor_role": "client",
        "execution_allowed": False,
        "source": "route_test",
        "entitlement_check": {
            "success": False,
            "status": "blocked",
            "error": "requested_agent_not_activated",
            "next_stage": "owner_admin_review_required",
            "entitlement_source": "governed_activation_persistence",
            "credential_values_exposed": False,
            "customer_safe": True,
        },
    },
)
assert blocked.status_code == 200
blocked_json = blocked.json()
assert blocked_json["decision_status"] == "blocked"
assert blocked_json["owner_admin_review_required"] is True

listed = client.get(f"/activation-execution-audit/decisions?tenant_id={tenant_id}")
assert listed.status_code == 200
listed_json = listed.json()
assert listed_json["success"] is True
assert listed_json["event_count"] >= 2
assert listed_json["credential_values_exposed"] is False

print("ACTIVATION_EXECUTION_AUDIT_LINK_ROUTES_TESTS_PASSED")
print("status_ready", status_json["activation_execution_audit_link_ready"])
print("record_status", record_json["decision_status"])
print("blocked_status", blocked_json["decision_status"])
print("listed_event_count", listed_json["event_count"])
