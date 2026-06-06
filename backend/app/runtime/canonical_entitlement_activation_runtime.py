from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import psycopg  # type: ignore
except ModuleNotFoundError:
    psycopg = None

from backend.app.core.canonical_billing_state_runtime import owner_admin_bypasses_client_billing


DATA_DIR = Path(__file__).resolve().parents[1] / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
FALLBACK_STORE = DATA_DIR / "canonical_entitlement_activation_state.json"

DATABASE_URL = os.getenv("DATABASE_URL")

PACKAGE_RULES: Dict[str, Dict[str, Any]] = {
    "starter": {"max_selectable_agents": 3, "enterprise_only_allowed": False},
    "growth": {"max_selectable_agents": 7, "enterprise_only_allowed": False},
    "business": {"max_selectable_agents": 10, "enterprise_only_allowed": False},
    "enterprise": {"max_selectable_agents": 27, "enterprise_only_allowed": True},
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalise_package(package: Any) -> str:
    value = str(package or "starter").strip().lower()
    aliases = {"pro": "business", "professional": "business", "premium": "business"}
    value = aliases.get(value, value)
    return value if value in PACKAGE_RULES else "starter"


def unique_agent_ids(values: Any) -> List[str]:
    if not isinstance(values, list):
        return []
    result: List[str] = []
    for item in values:
        value = str(item or "").strip().lower()
        if value and value not in result:
            result.append(value)
    return result


def _load_fallback() -> Dict[str, Any]:
    if not FALLBACK_STORE.exists():
        return {"version": "canonical_entitlement_activation_v1", "entitlements": {}, "events": []}
    try:
        data = json.loads(FALLBACK_STORE.read_text(encoding="utf-8"))
    except Exception:
        data = {"version": "canonical_entitlement_activation_v1", "entitlements": {}, "events": []}
    data.setdefault("entitlements", {})
    data.setdefault("events", [])
    return data


def _save_fallback(data: Dict[str, Any]) -> None:
    data["updated_at"] = utc_now_iso()
    FALLBACK_STORE.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def _db_available() -> bool:
    return bool(DATABASE_URL and psycopg is not None)


def _connect():
    if not DATABASE_URL or psycopg is None:
        raise RuntimeError("DATABASE_URL_missing")
    return psycopg.connect(DATABASE_URL)


def initialise_canonical_entitlement_tables() -> Dict[str, Any]:
    if not _db_available():
        return {"success": False, "database_available": False, "fallback_store": str(FALLBACK_STORE)}

    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS client_entitlements (
                    tenant_id TEXT PRIMARY KEY,
                    package_name TEXT NOT NULL,
                    selected_agents TEXT NOT NULL,
                    active_agents TEXT NOT NULL,
                    purchased_agents TEXT NOT NULL,
                    activation_status TEXT NOT NULL,
                    activation_locked BOOLEAN NOT NULL DEFAULT TRUE,
                    activation_version INTEGER NOT NULL DEFAULT 1,
                    source TEXT,
                    created_at TIMESTAMPTZ NOT NULL,
                    activated_at TIMESTAMPTZ,
                    updated_at TIMESTAMPTZ NOT NULL
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS client_entitlement_events (
                    id SERIAL PRIMARY KEY,
                    tenant_id TEXT,
                    event_type TEXT NOT NULL,
                    actor_role TEXT,
                    source TEXT,
                    payload TEXT NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL
                )
                """
            )
        conn.commit()

    return {"success": True, "database_available": True}


ENTITLEMENT_STARTUP_STATUS = initialise_canonical_entitlement_tables()


def _normalise_record(row: Any) -> Dict[str, Any]:
    return {
        "tenant_id": row[0],
        "package": row[1],
        "package_name": row[1],
        "selected_agents": json.loads(row[2] or "[]"),
        "active_agents": json.loads(row[3] or "[]"),
        "purchased_agents": json.loads(row[4] or "[]"),
        "activation_status": row[5],
        "activation_locked": bool(row[6]),
        "activation_version": int(row[7] or 1),
        "source": row[8],
        "created_at": row[9].isoformat() if row[9] else None,
        "activated_at": row[10].isoformat() if row[10] else None,
        "updated_at": row[11].isoformat() if row[11] else None,
    }


def _record_event(tenant_id: str, event_type: str, actor_role: str, source: str, payload: Dict[str, Any]) -> None:
    event = {
        "tenant_id": tenant_id,
        "event_type": event_type,
        "actor_role": actor_role,
        "source": source,
        "payload": payload,
        "created_at": utc_now_iso(),
    }

    if _db_available():
        try:
            with _connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO client_entitlement_events (tenant_id, event_type, actor_role, source, payload, created_at)
                        VALUES (%s,%s,%s,%s,%s,%s)
                        """,
                        (tenant_id, event_type, actor_role, source, json.dumps(payload), datetime.now(timezone.utc)),
                    )
                conn.commit()
                return
        except Exception:
            pass

    data = _load_fallback()
    data.setdefault("events", []).append(event)
    data["events"] = data["events"][-500:]
    _save_fallback(data)


def get_package_rules(package: Any = None) -> Dict[str, Any]:
    if package is None:
        return {
            "success": True,
            "canonical_package_rules": PACKAGE_RULES,
            "source": "canonical_entitlement_activation_runtime",
        }
    package_name = normalise_package(package)
    return {
        "success": True,
        "package": package_name,
        "rules": PACKAGE_RULES[package_name],
        "source": "canonical_entitlement_activation_runtime",
    }


def _agent_allowed_by_catalogue(agent_id: str, package_name: str) -> Dict[str, Any]:
    try:
        from backend.app.runtime.real_agent_component_catalogue import get_catalogue_component_by_key

        found = get_catalogue_component_by_key(agent_id)
        if not found.get("found") or found.get("component_type") != "client_facing_agent":
            return {"allowed": False, "reason": "invalid_agent"}
        component = found.get("component") or {}
        if component.get("enterprise_only") and not PACKAGE_RULES[package_name]["enterprise_only_allowed"]:
            return {"allowed": False, "reason": "enterprise_only_agent"}
        if component.get("internal_only"):
            return {"allowed": False, "reason": "internal_agent_not_selectable"}
    except Exception:
        pass
    return {"allowed": True, "reason": "allowed"}


def validate_agent_selection(package: Any, selected_agents: Any) -> Dict[str, Any]:
    package_name = normalise_package(package)
    selected = unique_agent_ids(selected_agents)
    rules = PACKAGE_RULES[package_name]
    invalid: List[str] = []
    enterprise_blocked: List[str] = []

    for agent_id in selected:
        allowed = _agent_allowed_by_catalogue(agent_id, package_name)
        if allowed["reason"] == "enterprise_only_agent":
            enterprise_blocked.append(agent_id)
        elif not allowed["allowed"]:
            invalid.append(agent_id)

    over_limit = len(selected) > int(rules["max_selectable_agents"])
    activation_allowed = not invalid and not enterprise_blocked and not over_limit

    return {
        "success": True,
        "valid": activation_allowed,
        "package": package_name,
        "plan": package_name,
        "selected_agents": selected,
        "selected_count": len(selected),
        "max_selectable_agents": rules["max_selectable_agents"],
        "invalid_agent_keys": invalid,
        "enterprise_blocked_agent_keys": enterprise_blocked,
        "over_limit": over_limit,
        "activation_allowed": activation_allowed,
        "selection_locked_after_activation": True,
        "owner_admin_required_for_changes": True,
        "canonical_source": "canonical_entitlement_activation_runtime",
    }


def build_activation_packet(package: Any, selected_agents: Any) -> Dict[str, Any]:
    validation = validate_agent_selection(package, selected_agents)
    active_agents = validation["selected_agents"] if validation["activation_allowed"] else []
    return {
        "success": True,
        "status": "activation_packet_ready" if validation["activation_allowed"] else "activation_packet_blocked",
        "plan": validation["package"],
        "package": validation["package"],
        "activation_allowed": validation["activation_allowed"],
        "active_agents": active_agents,
        "selected_agents": validation["selected_agents"],
        "client_visible_agents": active_agents,
        "hidden_unpurchased_agents": [],
        "client_hidden_agents_count": 0,
        "validation": validation,
        "full_catalogue_installed_for_owner_admin": True,
        "client_access_limited_to_paid_selected_agents": True,
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def get_entitlement(tenant_id: str) -> Dict[str, Any]:
    tenant_id = str(tenant_id or "").strip()
    if not tenant_id:
        return {"success": False, "error": "tenant_id_required"}

    if _db_available():
        try:
            with _connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT tenant_id, package_name, selected_agents, active_agents, purchased_agents,
                               activation_status, activation_locked, activation_version, source,
                               created_at, activated_at, updated_at
                        FROM client_entitlements
                        WHERE tenant_id = %s
                        """,
                        (tenant_id,),
                    )
                    row = cur.fetchone()
            if row:
                return {"success": True, "entitlement": _normalise_record(row), "canonical_storage": "postgres"}
        except Exception:
            pass

    data = _load_fallback()
    record = data.get("entitlements", {}).get(tenant_id)
    if not record:
        return {"success": False, "error": "entitlement_not_found", "tenant_id": tenant_id}
    return {"success": True, "entitlement": record, "canonical_storage": "file_fallback"}


def _persist_entitlement(record: Dict[str, Any], actor_role: str, source: str, event_type: str) -> Dict[str, Any]:
    tenant_id = record["tenant_id"]
    now = datetime.now(timezone.utc)

    if _db_available():
        try:
            with _connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO client_entitlements (
                            tenant_id, package_name, selected_agents, active_agents, purchased_agents,
                            activation_status, activation_locked, activation_version, source,
                            created_at, activated_at, updated_at
                        )
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                        ON CONFLICT (tenant_id)
                        DO UPDATE SET
                            package_name = EXCLUDED.package_name,
                            selected_agents = EXCLUDED.selected_agents,
                            active_agents = EXCLUDED.active_agents,
                            purchased_agents = EXCLUDED.purchased_agents,
                            activation_status = EXCLUDED.activation_status,
                            activation_locked = EXCLUDED.activation_locked,
                            activation_version = client_entitlements.activation_version + 1,
                            source = EXCLUDED.source,
                            activated_at = COALESCE(client_entitlements.activated_at, EXCLUDED.activated_at),
                            updated_at = EXCLUDED.updated_at
                        RETURNING tenant_id, package_name, selected_agents, active_agents, purchased_agents,
                                  activation_status, activation_locked, activation_version, source,
                                  created_at, activated_at, updated_at
                        """,
                        (
                            tenant_id,
                            record["package"],
                            json.dumps(record["selected_agents"]),
                            json.dumps(record["active_agents"]),
                            json.dumps(record["purchased_agents"]),
                            record["activation_status"],
                            bool(record["activation_locked"]),
                            int(record.get("activation_version") or 1),
                            source,
                            now,
                            now if record["activation_status"] == "activated" else None,
                            now,
                        ),
                    )
                    row = cur.fetchone()
                conn.commit()
            persisted = _normalise_record(row)
            _record_event(tenant_id, event_type, actor_role, source, persisted)
            return {"success": True, "entitlement": persisted, "canonical_storage": "postgres"}
        except Exception:
            pass

    data = _load_fallback()
    existing = data["entitlements"].get(tenant_id, {})
    fallback_record = {
        **existing,
        **record,
        "activation_version": int(existing.get("activation_version") or 0) + 1,
        "source": source,
        "created_at": existing.get("created_at") or utc_now_iso(),
        "activated_at": existing.get("activated_at") or (utc_now_iso() if record["activation_status"] == "activated" else None),
        "updated_at": utc_now_iso(),
    }
    data["entitlements"][tenant_id] = fallback_record
    _save_fallback(data)
    _record_event(tenant_id, event_type, actor_role, source, fallback_record)
    return {"success": True, "entitlement": fallback_record, "canonical_storage": "file_fallback"}


def activate_entitlement_once(
    *,
    tenant_id: str,
    package: Any,
    selected_agents: Any,
    actor_role: str = "client",
    source: str = "activation",
) -> Dict[str, Any]:
    tenant_id = str(tenant_id or "").strip()
    existing = get_entitlement(tenant_id)
    if (
        existing.get("success")
        and existing.get("entitlement", {}).get("activation_locked") is True
        and not owner_admin_bypasses_client_billing(actor_role)
    ):
        return {
            "success": False,
            "status": "blocked",
            "reason": "activation_locked",
            "tenant_id": tenant_id,
            "selection_locked": True,
            "owner_admin_required_for_changes": True,
            "entitlement": existing.get("entitlement"),
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    validation = validate_agent_selection(package, selected_agents)
    if not validation["activation_allowed"]:
        return {
            "success": False,
            "status": "blocked",
            "reason": "package_selection_invalid",
            "validation": validation,
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    record = {
        "tenant_id": tenant_id,
        "package": validation["package"],
        "package_name": validation["package"],
        "selected_agents": validation["selected_agents"],
        "active_agents": validation["selected_agents"],
        "purchased_agents": validation["selected_agents"],
        "activation_status": "activated",
        "activation_locked": True,
        "activation_version": 1,
    }
    result = _persist_entitlement(record, actor_role, source, "entitlement_activated")
    return {
        **result,
        "status": "activated",
        "selection_locked": True,
        "client_can_change_selection": False,
        "owner_admin_required_for_changes": True,
    }


def owner_admin_override_entitlement(
    *,
    tenant_id: str,
    package: Any,
    selected_agents: Any,
    actor_role: str = "owner_admin",
    source: str = "owner_admin_override",
) -> Dict[str, Any]:
    if not owner_admin_bypasses_client_billing(actor_role):
        return {"success": False, "status": "blocked", "error": "owner_admin_required"}
    validation = validate_agent_selection(package, selected_agents)
    if not validation["activation_allowed"]:
        return {"success": False, "status": "blocked", "reason": "package_selection_invalid", "validation": validation}
    record = {
        "tenant_id": str(tenant_id or "").strip(),
        "package": validation["package"],
        "package_name": validation["package"],
        "selected_agents": validation["selected_agents"],
        "active_agents": validation["selected_agents"],
        "purchased_agents": validation["selected_agents"],
        "activation_status": "activated",
        "activation_locked": True,
        "activation_version": 1,
    }
    result = _persist_entitlement(record, actor_role, source, "entitlement_owner_admin_overridden")
    return {**result, "status": "overridden", "owner_admin_override": True}


def request_entitlement_change(tenant_id: str, requested_agents: Any, reason: str = "", actor_role: str = "client") -> Dict[str, Any]:
    current = get_entitlement(tenant_id)
    payload = {
        "tenant_id": tenant_id,
        "requested_agents": unique_agent_ids(requested_agents),
        "current_agents": (current.get("entitlement") or {}).get("active_agents", []),
        "reason": reason,
        "status": "owner_admin_review_required",
    }
    _record_event(tenant_id, "entitlement_change_requested", actor_role, "canonical_entitlement_activation_runtime", payload)
    return {
        "success": True,
        "status": "owner_admin_review_required",
        "workflow_status": "activation_change_queued",
        "next_stage": "owner_admin_review",
        "change_request": payload,
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def evaluate_execution_entitlement(tenant_id: str, requested_agent: str, actor_role: str = "client") -> Dict[str, Any]:
    if owner_admin_bypasses_client_billing(actor_role):
        return {
            "success": True,
            "execution_allowed": True,
            "status": "owner_admin_unrestricted",
            "tenant_id": tenant_id,
            "requested_agent": requested_agent,
            "entitlement_source": "owner_admin_unrestricted_access",
            "owner_admin_unrestricted": True,
        }

    tenant_id = str(tenant_id or "").strip()
    requested_agent = str(requested_agent or "").strip().lower()
    if not tenant_id:
        return {"success": False, "execution_allowed": False, "error": "missing_tenant_id"}
    if not requested_agent:
        return {"success": False, "execution_allowed": False, "error": "missing_requested_agent", "tenant_id": tenant_id}

    state = get_entitlement(tenant_id)
    if not state.get("success"):
        return {
            "success": False,
            "execution_allowed": False,
            "status": "blocked",
            "error": "entitlement_not_found",
            "tenant_id": tenant_id,
            "requested_agent": requested_agent,
            "entitlement_source": "canonical_entitlement_activation_runtime",
        }

    entitlement = state["entitlement"]
    active_agents = unique_agent_ids(entitlement.get("active_agents"))
    allowed = (
        entitlement.get("activation_status") == "activated"
        and entitlement.get("activation_locked") is True
        and requested_agent in active_agents
    )
    return {
        "success": allowed,
        "execution_allowed": allowed,
        "status": "approved" if allowed else "blocked",
        "error": None if allowed else "requested_agent_not_activated",
        "tenant_id": tenant_id,
        "requested_agent": requested_agent,
        "active_agents": active_agents,
        "activation_locked": bool(entitlement.get("activation_locked")),
        "entitlement_source": "canonical_entitlement_activation_runtime",
        "entitlement": entitlement,
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def validate_package_downgrade(current_package: Any, target_package: Any, active_agents: Any) -> Dict[str, Any]:
    current = normalise_package(current_package)
    target = normalise_package(target_package)
    active = unique_agent_ids(active_agents)
    target_limit = int(PACKAGE_RULES[target]["max_selectable_agents"])
    blocked = target != "enterprise" and len(active) > target_limit
    return {
        "success": True,
        "downgrade_allowed": not blocked,
        "blocked": blocked,
        "current_package": current,
        "target_package": target,
        "target_package_limit": target_limit,
        "active_agent_count": len(active),
        "agents_to_deactivate_required": max(0, len(active) - target_limit),
        "canonical_source": "canonical_entitlement_activation_runtime",
    }


def canonical_entitlement_activation_status() -> Dict[str, Any]:
    return {
        "success": True,
        "canonical_entitlement_activation_ready": True,
        "startup_status": ENTITLEMENT_STARTUP_STATUS,
        "package_rules": PACKAGE_RULES,
        "owner_admin_unrestricted_access_preserved": True,
        "activation_lock_enforced": True,
        "execution_entitlement_authority": "canonical_entitlement_activation_runtime",
        "credential_values_exposed": False,
        "customer_safe": True,
    }
