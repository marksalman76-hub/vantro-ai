from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP_DIR = ROOT / "backups" / f"activation_governance_admin_visibility_before_{STAMP}"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

runtime_path = ROOT / "backend" / "app" / "runtime" / "activation_governance_admin_visibility.py"
test_path = ROOT / "test_activation_governance_admin_visibility.py"

for path in [runtime_path, test_path]:
    if path.exists():
        backup = BACKUP_DIR / path.relative_to(ROOT)
        backup.parent.mkdir(parents=True, exist_ok=True)
        backup.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")

runtime_path.parent.mkdir(parents=True, exist_ok=True)

runtime_path.write_text(r'''
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
''', encoding="utf-8")

test_path.write_text(r'''
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
''', encoding="utf-8")

print("ACTIVATION_GOVERNANCE_ADMIN_VISIBILITY_INSTALLED")
print(f"Backup folder: {BACKUP_DIR}")
print(f"Created/updated: {runtime_path}")
print(f"Created/updated: {test_path}")