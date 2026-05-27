
from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict

from backend.app.runtime.activation_execution_audit_link import list_activation_execution_decisions
from backend.app.runtime.governed_activation_persistence import get_activation_audit_ledger
from backend.app.runtime.runtime_entitlement_hydration_bridge import get_runtime_entitlement_hydration_bridge_status


def get_activation_governance_admin_visibility(tenant_id: str = "") -> Dict[str, Any]:
    ledger = get_activation_audit_ledger(tenant_id or None)
    decisions = list_activation_execution_decisions(tenant_id)
    hydration = get_runtime_entitlement_hydration_bridge_status()

    ledger_events = ledger.get("events", [])
    decision_events = decisions.get("events", [])

    blocked_decisions = [
        event for event in decision_events
        if event.get("decision_status") == "blocked"
    ]

    owner_review_events = [
        event for event in ledger_events + decision_events
        if event.get("next_stage") == "owner_admin_review_required"
        or event.get("owner_admin_review_required") is True
        or event.get("status") == "owner_admin_review_required"
    ]

    activated_events = [
        event for event in ledger_events
        if event.get("status") == "activated"
        or event.get("event_type") == "activation_persisted"
    ]

    summary = {
        "tenant_filter": tenant_id or "all",
        "activation_ledger_event_count": len(ledger_events),
        "execution_decision_event_count": len(decision_events),
        "blocked_execution_decision_count": len(blocked_decisions),
        "owner_admin_review_required_count": len(owner_review_events),
        "activation_persisted_count": len(activated_events),
        "runtime_entitlement_hydration_ready": bool(hydration.get("runtime_entitlement_hydration_bridge_ready")),
        "client_execution_limited_to_activated_agents": bool(hydration.get("client_execution_limited_to_activated_agents")),
        "owner_admin_unrestricted_access_preserved": bool(hydration.get("owner_admin_unrestricted_access_preserved")),
    }

    return {
        "success": True,
        "activation_governance_admin_visibility_ready": True,
        "summary": summary,
        "recent_activation_events": deepcopy(ledger_events[-10:]),
        "recent_execution_decisions": deepcopy(decision_events[-10:]),
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def get_activation_governance_admin_visibility_status() -> Dict[str, Any]:
    return {
        "success": True,
        "activation_governance_admin_visibility_ready": True,
        "activation_lock_audit_visible": True,
        "blocked_change_review_visible": True,
        "entitlement_hydration_visible": True,
        "customer_safe_admin_summary_enabled": True,
        "credential_values_exposed": False,
        "customer_safe": True,
    }
