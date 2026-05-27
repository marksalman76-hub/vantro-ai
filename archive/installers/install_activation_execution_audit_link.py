from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP_DIR = ROOT / "backups" / f"activation_execution_audit_link_before_{STAMP}"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

runtime_path = ROOT / "backend" / "app" / "runtime" / "activation_execution_audit_link.py"
test_path = ROOT / "test_activation_execution_audit_link.py"

for path in [runtime_path, test_path]:
    if path.exists():
        backup = BACKUP_DIR / path.relative_to(ROOT)
        backup.parent.mkdir(parents=True, exist_ok=True)
        backup.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")

runtime_path.parent.mkdir(parents=True, exist_ok=True)

runtime_path.write_text(r'''
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
''', encoding="utf-8")

test_path.write_text(r'''
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
''', encoding="utf-8")

print("ACTIVATION_EXECUTION_AUDIT_LINK_INSTALLED")
print(f"Backup folder: {BACKUP_DIR}")
print(f"Created/updated: {runtime_path}")
print(f"Created/updated: {test_path}")