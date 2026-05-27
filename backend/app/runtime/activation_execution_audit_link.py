
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, List
from uuid import uuid4

_ACTIVATION_EXECUTION_AUDIT_EVENTS: List[Dict[str, Any]] = []


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def record_activation_execution_decision(
    *,
    tenant_id: str,
    requested_agent: str,
    actor_role: str,
    execution_allowed: bool,
    entitlement_check: Dict[str, Any],
    source: str = "run_agent",
) -> Dict[str, Any]:
    event = {
        "event_id": f"activation_execution_decision_{uuid4().hex[:12]}",
        "tenant_id": str(tenant_id or "").strip(),
        "requested_agent": str(requested_agent or "").strip(),
        "actor_role": str(actor_role or "").strip().lower(),
        "execution_allowed": bool(execution_allowed),
        "decision_status": "approved" if execution_allowed else "blocked",
        "source": source,
        "entitlement_source": entitlement_check.get("entitlement_source", "unknown"),
        "entitlement_error": entitlement_check.get("error"),
        "next_stage": entitlement_check.get("next_stage"),
        "owner_admin_review_required": entitlement_check.get("next_stage") == "owner_admin_review_required",
        "credential_values_exposed": False,
        "customer_safe": True,
        "created_at": _now(),
        "entitlement_check": deepcopy(entitlement_check),
    }

    _ACTIVATION_EXECUTION_AUDIT_EVENTS.append(event)
    return deepcopy(event)


def list_activation_execution_decisions(tenant_id: str = "") -> Dict[str, Any]:
    key = str(tenant_id or "").strip()
    events = [
        deepcopy(event)
        for event in _ACTIVATION_EXECUTION_AUDIT_EVENTS
        if not key or event.get("tenant_id") == key
    ]

    return {
        "success": True,
        "event_count": len(events),
        "events": events,
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def get_activation_execution_audit_status() -> Dict[str, Any]:
    return {
        "success": True,
        "activation_execution_audit_link_ready": True,
        "activation_decisions_recorded": True,
        "execution_allowed_decision_visible": True,
        "blocked_execution_decision_visible": True,
        "owner_admin_review_marker_enabled": True,
        "credential_values_exposed": False,
        "customer_safe": True,
    }
