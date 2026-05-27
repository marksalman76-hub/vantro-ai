
from backend.app.runtime.activation_execution_audit_link import record_activation_execution_decision
from backend.app.runtime.activation_governance_admin_visibility import (
    get_activation_governance_admin_visibility,
    get_activation_governance_admin_visibility_status,
)
from backend.app.runtime.governed_activation_persistence import persist_activation_packet

tenant_id = "test-activation-governance-admin-visibility-001"

status = get_activation_governance_admin_visibility_status()
assert status["activation_governance_admin_visibility_ready"] is True
assert status["credential_values_exposed"] is False

persisted = persist_activation_packet(
    {
        "tenant_id": tenant_id,
        "package_id": "business",
        "selected_agents": ["seo_agent", "email_reply_agent"],
    },
    actor_role="system",
)
assert persisted["success"] is True

record_activation_execution_decision(
    tenant_id=tenant_id,
    requested_agent="seo_agent",
    actor_role="client",
    execution_allowed=True,
    entitlement_check={
        "success": True,
        "status": "approved",
        "entitlement_source": "governed_activation_persistence",
    },
)

record_activation_execution_decision(
    tenant_id=tenant_id,
    requested_agent="head_agent",
    actor_role="client",
    execution_allowed=False,
    entitlement_check={
        "success": False,
        "status": "blocked",
        "error": "requested_agent_not_activated",
        "next_stage": "owner_admin_review_required",
        "entitlement_source": "governed_activation_persistence",
    },
)

visibility = get_activation_governance_admin_visibility(tenant_id)
assert visibility["success"] is True
assert visibility["activation_governance_admin_visibility_ready"] is True
assert visibility["summary"]["activation_ledger_event_count"] >= 1
assert visibility["summary"]["execution_decision_event_count"] >= 2
assert visibility["summary"]["blocked_execution_decision_count"] >= 1
assert visibility["summary"]["owner_admin_review_required_count"] >= 1
assert visibility["summary"]["runtime_entitlement_hydration_ready"] is True
assert visibility["credential_values_exposed"] is False

print("ACTIVATION_GOVERNANCE_ADMIN_VISIBILITY_TESTS_PASSED")
print("status_ready", status["activation_governance_admin_visibility_ready"])
print("ledger_events", visibility["summary"]["activation_ledger_event_count"])
print("execution_decisions", visibility["summary"]["execution_decision_event_count"])
print("blocked_decisions", visibility["summary"]["blocked_execution_decision_count"])
print("owner_review_required", visibility["summary"]["owner_admin_review_required_count"])
