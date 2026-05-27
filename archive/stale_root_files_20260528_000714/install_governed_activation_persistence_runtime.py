from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP_DIR = ROOT / "backups" / f"governed_activation_persistence_before_{STAMP}"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

runtime_path = ROOT / "backend" / "app" / "runtime" / "governed_activation_persistence.py"
test_path = ROOT / "test_governed_activation_persistence_runtime.py"

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
from typing import Any, Dict, List, Optional
from uuid import uuid4


_ACTIVATED_AGENT_REGISTRY: Dict[str, Dict[str, Any]] = {}
_CHANGE_REQUEST_QUEUE: Dict[str, Dict[str, Any]] = {}
_ACTIVATION_AUDIT_LEDGER: List[Dict[str, Any]] = []


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _clean_agent_ids(agent_ids: Any) -> List[str]:
    if not isinstance(agent_ids, list):
        return []
    clean: List[str] = []
    for item in agent_ids:
        if isinstance(item, str):
            value = item.strip()
            if value and value not in clean:
                clean.append(value)
    return clean


def _ledger_event(
    *,
    tenant_id: str,
    event_type: str,
    status: str,
    actor_role: str,
    details: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    event = {
        "event_id": f"activation_event_{uuid4().hex[:12]}",
        "tenant_id": tenant_id,
        "event_type": event_type,
        "status": status,
        "actor_role": actor_role,
        "created_at": _now(),
        "customer_safe": True,
        "credential_values_exposed": False,
        "details": deepcopy(details or {}),
    }
    _ACTIVATION_AUDIT_LEDGER.append(event)
    return deepcopy(event)


def persist_activation_packet(packet: Dict[str, Any], actor_role: str = "system") -> Dict[str, Any]:
    tenant_id = str(packet.get("tenant_id") or packet.get("client_id") or "").strip()
    package_id = str(packet.get("package_id") or packet.get("package") or "").strip()
    selected_agents = _clean_agent_ids(packet.get("selected_agents") or packet.get("agent_ids"))

    if not tenant_id:
        return {
            "success": False,
            "status": "rejected",
            "error": "missing_tenant_id",
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    if not selected_agents:
        return {
            "success": False,
            "status": "rejected",
            "error": "missing_selected_agents",
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    existing = _ACTIVATED_AGENT_REGISTRY.get(tenant_id)
    if existing and existing.get("activation_locked") is True:
        return {
            "success": False,
            "status": "blocked",
            "workflow_status": "activation_change_blocked",
            "next_stage": "owner_admin_review_required",
            "tenant_id": tenant_id,
            "activated_agents": deepcopy(existing.get("activated_agents", [])),
            "requested_agents": selected_agents,
            "message": "Client post-activation agent changes are blocked and require owner/admin approval.",
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    record = {
        "tenant_id": tenant_id,
        "package_id": package_id,
        "activated_agents": selected_agents,
        "activation_locked": True,
        "activation_status": "activated",
        "activation_version": 1,
        "activated_at": _now(),
        "updated_at": _now(),
        "source": "signup_activation_packet",
        "entitlement_hydrated": True,
        "customer_safe": True,
        "credential_values_exposed": False,
    }

    _ACTIVATED_AGENT_REGISTRY[tenant_id] = record

    _ledger_event(
        tenant_id=tenant_id,
        event_type="activation_persisted",
        status="activated",
        actor_role=actor_role,
        details={
            "package_id": package_id,
            "activated_agent_count": len(selected_agents),
            "activation_locked": True,
        },
    )

    return {
        "success": True,
        "status": "activated",
        "workflow_status": "activation_persisted",
        "next_stage": "activation_state_hydration",
        "tenant_id": tenant_id,
        "activation_record": deepcopy(record),
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def hydrate_activation_state(tenant_id: str) -> Dict[str, Any]:
    key = str(tenant_id or "").strip()
    record = _ACTIVATED_AGENT_REGISTRY.get(key)

    if not record:
        return {
            "success": False,
            "status": "not_found",
            "tenant_id": key,
            "activated_agents": [],
            "entitlement_hydrated": False,
            "activation_locked": False,
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    _ledger_event(
        tenant_id=key,
        event_type="activation_state_hydrated",
        status="found",
        actor_role="system",
        details={"activated_agent_count": len(record.get("activated_agents", []))},
    )

    return {
        "success": True,
        "status": "found",
        "tenant_id": key,
        "activation_state": deepcopy(record),
        "activated_agents": deepcopy(record.get("activated_agents", [])),
        "entitlement_hydrated": True,
        "activation_locked": bool(record.get("activation_locked")),
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def hydrate_runtime_entitlements(tenant_id: str) -> Dict[str, Any]:
    state = hydrate_activation_state(tenant_id)
    if not state.get("success"):
        return {
            **state,
            "runtime_entitlements": {
                "allowed_agent_ids": [],
                "agent_execution_allowed": False,
            },
        }

    agents = state.get("activated_agents", [])
    return {
        "success": True,
        "status": "runtime_entitlements_hydrated",
        "tenant_id": tenant_id,
        "runtime_entitlements": {
            "allowed_agent_ids": deepcopy(agents),
            "agent_execution_allowed": True,
            "post_activation_client_changes_blocked": True,
            "owner_admin_required_for_post_activation_changes": True,
        },
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def submit_activation_change_request(
    *,
    tenant_id: str,
    requested_agents: List[str],
    reason: str = "",
    actor_role: str = "client",
) -> Dict[str, Any]:
    key = str(tenant_id or "").strip()
    requested = _clean_agent_ids(requested_agents)

    if not key:
        return {
            "success": False,
            "status": "rejected",
            "error": "missing_tenant_id",
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    request_id = f"activation_change_{uuid4().hex[:12]}"
    record = _ACTIVATED_AGENT_REGISTRY.get(key, {})

    change = {
        "request_id": request_id,
        "tenant_id": key,
        "requested_agents": requested,
        "current_agents": deepcopy(record.get("activated_agents", [])),
        "reason": reason,
        "status": "owner_admin_review_required",
        "created_at": _now(),
        "updated_at": _now(),
        "actor_role": actor_role,
        "client_self_service_allowed": False,
        "credential_values_exposed": False,
        "customer_safe": True,
    }

    _CHANGE_REQUEST_QUEUE[request_id] = change

    _ledger_event(
        tenant_id=key,
        event_type="activation_change_requested",
        status="owner_admin_review_required",
        actor_role=actor_role,
        details={"request_id": request_id, "requested_agent_count": len(requested)},
    )

    return {
        "success": True,
        "status": "owner_admin_review_required",
        "workflow_status": "activation_change_queued",
        "next_stage": "owner_admin_review",
        "change_request": deepcopy(change),
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def approve_activation_change_request(request_id: str, actor_role: str = "owner_admin") -> Dict[str, Any]:
    change = _CHANGE_REQUEST_QUEUE.get(str(request_id or "").strip())

    if not change:
        return {
            "success": False,
            "status": "not_found",
            "error": "change_request_not_found",
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    if actor_role not in {"owner", "admin", "owner_admin", "system_admin"}:
        return {
            "success": False,
            "status": "blocked",
            "error": "owner_admin_required",
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    tenant_id = change["tenant_id"]
    existing = _ACTIVATED_AGENT_REGISTRY.get(tenant_id, {})
    version = int(existing.get("activation_version", 1)) + 1

    updated = {
        **existing,
        "tenant_id": tenant_id,
        "activated_agents": deepcopy(change.get("requested_agents", [])),
        "activation_locked": True,
        "activation_status": "activated",
        "activation_version": version,
        "updated_at": _now(),
        "entitlement_hydrated": True,
        "credential_values_exposed": False,
        "customer_safe": True,
    }

    _ACTIVATED_AGENT_REGISTRY[tenant_id] = updated
    change["status"] = "approved"
    change["updated_at"] = _now()

    _ledger_event(
        tenant_id=tenant_id,
        event_type="activation_change_approved",
        status="approved",
        actor_role=actor_role,
        details={"request_id": request_id, "activation_version": version},
    )

    return {
        "success": True,
        "status": "approved",
        "workflow_status": "activation_change_approved",
        "activation_record": deepcopy(updated),
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def reconcile_activation_state(tenant_id: str) -> Dict[str, Any]:
    state = hydrate_activation_state(tenant_id)
    if not state.get("success"):
        return {
            "success": False,
            "status": "reconciliation_required",
            "tenant_id": tenant_id,
            "recovery_action": "owner_admin_review_required",
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    return {
        "success": True,
        "status": "reconciled",
        "tenant_id": tenant_id,
        "activation_locked": state.get("activation_locked"),
        "entitlement_hydrated": state.get("entitlement_hydrated"),
        "activated_agent_count": len(state.get("activated_agents", [])),
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def get_activation_audit_ledger(tenant_id: Optional[str] = None) -> Dict[str, Any]:
    if tenant_id:
        events = [e for e in _ACTIVATION_AUDIT_LEDGER if e.get("tenant_id") == tenant_id]
    else:
        events = list(_ACTIVATION_AUDIT_LEDGER)

    return {
        "success": True,
        "event_count": len(events),
        "events": deepcopy(events),
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def get_activation_persistence_status() -> Dict[str, Any]:
    return {
        "success": True,
        "governed_activation_persistence_ready": True,
        "activated_registry_enabled": True,
        "runtime_entitlement_hydration_enabled": True,
        "change_request_queue_enabled": True,
        "owner_admin_required_for_post_activation_changes": True,
        "activation_audit_ledger_enabled": True,
        "activation_reconciliation_enabled": True,
        "credential_values_exposed": False,
        "customer_safe": True,
    }
''', encoding="utf-8")

test_path.write_text(r'''
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
''', encoding="utf-8")

print("GOVERNED_ACTIVATION_PERSISTENCE_RUNTIME_INSTALLED")
print(f"Backup folder: {BACKUP_DIR}")
print(f"Created/updated: {runtime_path}")
print(f"Created/updated: {test_path}")