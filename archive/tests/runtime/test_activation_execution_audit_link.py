
from backend.app.runtime.activation_execution_audit_link import (
    get_activation_execution_audit_status,
    list_activation_execution_decisions,
    record_activation_execution_decision,
)

tenant_id = "test-activation-execution-audit-link-001"

status = get_activation_execution_audit_status()
assert status["activation_execution_audit_link_ready"] is True
assert status["credential_values_exposed"] is False

approved = record_activation_execution_decision(
    tenant_id=tenant_id,
    requested_agent="seo_agent",
    actor_role="client",
    execution_allowed=True,
    entitlement_check={
        "success": True,
        "status": "approved",
        "entitlement_source": "governed_activation_persistence",
        "credential_values_exposed": False,
        "customer_safe": True,
    },
)
assert approved["decision_status"] == "approved"
assert approved["execution_allowed"] is True
assert approved["credential_values_exposed"] is False

blocked = record_activation_execution_decision(
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
        "credential_values_exposed": False,
        "customer_safe": True,
    },
)
assert blocked["decision_status"] == "blocked"
assert blocked["owner_admin_review_required"] is True
assert blocked["entitlement_error"] == "requested_agent_not_activated"

listed = list_activation_execution_decisions(tenant_id)
assert listed["success"] is True
assert listed["event_count"] == 2
assert listed["credential_values_exposed"] is False

print("ACTIVATION_EXECUTION_AUDIT_LINK_TESTS_PASSED")
print("status_ready", status["activation_execution_audit_link_ready"])
print("approved_status", approved["decision_status"])
print("blocked_status", blocked["decision_status"])
print("listed_event_count", listed["event_count"])
