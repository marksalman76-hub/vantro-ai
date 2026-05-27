
from backend.app.runtime.governed_activation_persistence import (
    approve_activation_change_request,
    get_activation_audit_ledger,
    get_activation_persistence_status,
    hydrate_activation_state,
    hydrate_runtime_entitlements,
    persist_activation_packet,
    reconcile_activation_state,
    submit_activation_change_request,
)

tenant_id = "test-governed-activation-tenant-001"

status = get_activation_persistence_status()
assert status["governed_activation_persistence_ready"] is True
assert status["credential_values_exposed"] is False

packet = {
    "tenant_id": tenant_id,
    "package_id": "business",
    "selected_agents": ["seo_agent", "email_reply_agent", "marketing_specialist_agent"],
}

persisted = persist_activation_packet(packet, actor_role="system")
assert persisted["success"] is True
assert persisted["status"] == "activated"
assert persisted["activation_record"]["activation_locked"] is True

hydrated = hydrate_activation_state(tenant_id)
assert hydrated["success"] is True
assert hydrated["status"] == "found"
assert hydrated["activation_locked"] is True
assert hydrated["entitlement_hydrated"] is True
assert len(hydrated["activated_agents"]) == 3

runtime = hydrate_runtime_entitlements(tenant_id)
assert runtime["success"] is True
assert runtime["runtime_entitlements"]["agent_execution_allowed"] is True
assert "seo_agent" in runtime["runtime_entitlements"]["allowed_agent_ids"]

blocked_second_packet = persist_activation_packet(
    {
        "tenant_id": tenant_id,
        "package_id": "business",
        "selected_agents": ["seo_agent"],
    },
    actor_role="client",
)
assert blocked_second_packet["success"] is False
assert blocked_second_packet["status"] == "blocked"
assert blocked_second_packet["next_stage"] == "owner_admin_review_required"

change = submit_activation_change_request(
    tenant_id=tenant_id,
    requested_agents=["seo_agent", "email_reply_agent"],
    reason="Package adjustment requested by client.",
    actor_role="client",
)
assert change["success"] is True
assert change["status"] == "owner_admin_review_required"
request_id = change["change_request"]["request_id"]

approved = approve_activation_change_request(request_id, actor_role="owner_admin")
assert approved["success"] is True
assert approved["status"] == "approved"
assert approved["activation_record"]["activation_version"] == 2
assert len(approved["activation_record"]["activated_agents"]) == 2

reconciled = reconcile_activation_state(tenant_id)
assert reconciled["success"] is True
assert reconciled["status"] == "reconciled"
assert reconciled["activated_agent_count"] == 2

ledger = get_activation_audit_ledger(tenant_id)
assert ledger["success"] is True
assert ledger["event_count"] >= 4
assert ledger["credential_values_exposed"] is False

print("GOVERNED_ACTIVATION_PERSISTENCE_RUNTIME_TESTS_PASSED")
print("status_ready", status["governed_activation_persistence_ready"])
print("persisted_status", persisted["status"])
print("hydrated_status", hydrated["status"])
print("runtime_status", runtime["status"])
print("blocked_status", blocked_second_packet["status"])
print("change_status", change["status"])
print("approved_status", approved["status"])
print("reconciled_status", reconciled["status"])
print("ledger_event_count", ledger["event_count"])
