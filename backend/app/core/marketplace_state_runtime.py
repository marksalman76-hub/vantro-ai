from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from backend.app.core.marketplace_activation_runtime import (
    activate_marketplace_agent,
    deactivate_marketplace_agent,
    build_client_marketplace_workspace,
)
from backend.app.core.marketplace_entitlement_runtime import PACKAGE_LIMITS
from backend.app.runtime.canonical_entitlement_activation_runtime import (
    activate_entitlement_once,
    owner_admin_override_entitlement,
    validate_package_downgrade as canonical_validate_package_downgrade,
)


DATA_DIR = Path.cwd() / "runtime_data"
STATE_FILE = DATA_DIR / "marketplace_tenant_state.jsonl"
AUDIT_FILE = DATA_DIR / "marketplace_activation_audit.jsonl"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_jsonl(path: Path, limit: int = 5000) -> List[Dict[str, Any]]:
    if not path.exists():
        return []

    records = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            try:
                records.append(json.loads(line))
            except Exception:
                continue

    return records[-limit:]


def _rewrite_jsonl(path: Path, records: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def _append_jsonl(path: Path, record: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def _unique(values: List[str]) -> List[str]:
    return list(dict.fromkeys([str(v).strip().lower() for v in values if str(v).strip()]))


def _find_state(records: List[Dict[str, Any]], tenant_id: str) -> Dict[str, Any] | None:
    for record in reversed(records):
        if record.get("tenant_id") == tenant_id:
            return record
    return None


def upsert_marketplace_state(payload: Dict[str, Any]) -> Dict[str, Any]:
    tenant_id = str(payload.get("tenant_id") or "").strip()
    if not tenant_id:
        return {"success": False, "error": "tenant_id_required"}

    state = {
        "tenant_id": tenant_id,
        "client_number": payload.get("client_number"),
        "package": str(payload.get("package") or "starter").lower(),
        "purchased_agents": _unique(payload.get("purchased_agents") or []),
        "active_agents": _unique(payload.get("active_agents") or payload.get("activated_agents") or []),
        "updated_at": _now(),
        "state_profile": "priority9_marketplace_state_v1",
        "client_access_limited_to_paid_agents": True,
        "internal_config_hidden_from_client": True,
        "secret_exposure": False,
        "entitlement_bypass": False,
        "governance_bypass": False,
    }

    records = _read_jsonl(STATE_FILE)
    records = [r for r in records if r.get("tenant_id") != tenant_id]
    records.append(state)
    _rewrite_jsonl(STATE_FILE, records)

    _append_jsonl(AUDIT_FILE, {
        "timestamp": _now(),
        "event_type": "marketplace_state_upserted",
        "tenant_id": tenant_id,
        "client_number": state.get("client_number"),
        "package": state.get("package"),
    })

    canonical_sync = owner_admin_override_entitlement(
        tenant_id=tenant_id,
        package=state["package"],
        selected_agents=state["active_agents"] or state["purchased_agents"],
        actor_role=str(payload.get("actor_role") or "owner_admin"),
        source="marketplace_state_runtime",
    )

    return {
        "success": True,
        "state": state,
        "state_store_role": "audit_visibility_cache",
        "canonical_entitlement_sync": canonical_sync,
    }


def get_marketplace_state(payload: Dict[str, Any]) -> Dict[str, Any]:
    tenant_id = str(payload.get("tenant_id") or "").strip()
    if not tenant_id:
        return {"success": False, "error": "tenant_id_required"}

    records = _read_jsonl(STATE_FILE)
    state = _find_state(records, tenant_id)

    if not state:
        return {
            "success": False,
            "error": "marketplace_state_not_found",
            "tenant_id": tenant_id,
        }

    workspace = build_client_marketplace_workspace(state)

    return {
        "success": True,
        "state": state,
        "workspace": workspace,
        "customer_safe_response_mode": True,
        "secret_exposure": False,
        "internal_config_hidden_from_client": True,
    }


def persist_activation_action(payload: Dict[str, Any]) -> Dict[str, Any]:
    tenant_id = str(payload.get("tenant_id") or "").strip()
    action = str(payload.get("action") or "activate").strip().lower()
    agent_id = str(payload.get("agent_id") or "").strip().lower()

    if not tenant_id:
        return {"success": False, "error": "tenant_id_required"}

    records = _read_jsonl(STATE_FILE)
    state = _find_state(records, tenant_id)

    if not state:
        initial = upsert_marketplace_state(payload)
        state = initial.get("state", {})

    action_payload = {
        **state,
        "agent_id": agent_id,
    }

    if action == "activate":
        result = activate_marketplace_agent(action_payload)
    elif action == "deactivate":
        result = deactivate_marketplace_agent(action_payload)
    else:
        return {"success": False, "error": "unsupported_marketplace_action"}

    if result.get("success"):
        state["active_agents"] = result.get("active_agents", state.get("active_agents", []))
        state["updated_at"] = _now()
        owner_admin_override_entitlement(
            tenant_id=tenant_id,
            package=state.get("package"),
            selected_agents=state.get("active_agents", []),
            actor_role=str(payload.get("actor_role") or "owner_admin"),
            source="marketplace_activation_action",
        )

        records = [r for r in _read_jsonl(STATE_FILE) if r.get("tenant_id") != tenant_id]
        records.append(state)
        _rewrite_jsonl(STATE_FILE, records)

    _append_jsonl(AUDIT_FILE, {
        "timestamp": _now(),
        "event_type": f"marketplace_agent_{action}",
        "tenant_id": tenant_id,
        "client_number": state.get("client_number"),
        "agent_id": agent_id,
        "success": result.get("success"),
        "status": result.get("status"),
        "error": result.get("error"),
    })

    return {
        **result,
        "persisted": bool(result.get("success")),
        "state": state if result.get("success") else None,
        "audit_logged": True,
    }


def validate_package_downgrade(payload: Dict[str, Any]) -> Dict[str, Any]:
    current_package = str(payload.get("current_package") or payload.get("package") or "starter").lower()
    target_package = str(payload.get("target_package") or "starter").lower()
    active_agents = _unique(payload.get("active_agents") or [])
    canonical = canonical_validate_package_downgrade(current_package, target_package, active_agents)
    current_limit = PACKAGE_LIMITS.get(current_package, canonical.get("target_package_limit", 3))
    target_limit = canonical.get("target_package_limit")
    blocked = canonical.get("blocked")

    return {
        "success": True,
        "downgrade_allowed": not blocked,
        "blocked": blocked,
        "current_package": current_package,
        "target_package": target_package,
        "current_package_limit": current_limit,
        "target_package_limit": target_limit,
        "active_agent_count": len(active_agents),
        "agents_to_deactivate_required": max(0, len(active_agents) - target_limit),
        "customer_safe_message": (
            "Deactivate agents before downgrading." if blocked else "Downgrade can continue."
        ),
        "secret_exposure": False,
        "entitlement_bypass": False,
        "governance_bypass": False,
        "canonical_downgrade_check": canonical,
    }


def marketplace_audit_history(payload: Dict[str, Any]) -> Dict[str, Any]:
    tenant_id = str(payload.get("tenant_id") or "").strip()
    limit = int(payload.get("limit") or 50)

    events = _read_jsonl(AUDIT_FILE, limit=5000)
    if tenant_id:
        events = [e for e in events if e.get("tenant_id") == tenant_id]

    return {
        "success": True,
        "tenant_id": tenant_id or None,
        "count": len(events[-limit:]),
        "events": events[-limit:],
        "secret_exposure": False,
        "customer_safe_response_mode": True,
    }
