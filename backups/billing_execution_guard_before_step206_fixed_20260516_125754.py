from __future__ import annotations

import json
from typing import Any, Dict, Optional

from backend.app.core.durable_billing_state_store import get_billing_runtime_state


OWNER_ADMIN_ROLES = {"owner", "admin", "system"}


def _normalise_role(actor_role: Optional[str]) -> str:
    return (actor_role or "").strip().lower()


def owner_admin_bypasses_client_billing(actor_role: Optional[str]) -> bool:
    return _normalise_role(actor_role) in OWNER_ADMIN_ROLES


def extract_tenant_id_from_request(
    header_tenant_id: Optional[str],
    payload: Optional[Dict[str, Any]],
) -> Optional[str]:
    if header_tenant_id:
        return header_tenant_id

    if not isinstance(payload, dict):
        return None

    for key in ("tenant_id", "client_id", "workspace_id"):
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()

    nested = payload.get("payload")
    if isinstance(nested, dict):
        for key in ("tenant_id", "client_id", "workspace_id"):
            value = nested.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()

    return None


def check_billing_execution_allowed(
    tenant_id: Optional[str],
    actor_role: Optional[str],
) -> Dict[str, Any]:
    if owner_admin_bypasses_client_billing(actor_role):
        return {
            "allowed": True,
            "reason": "owner_admin_billing_bypass",
            "tenant_id": tenant_id,
            "actor_role": actor_role,
            "billing_guard_applied": True,
            "owner_admin_access_unaffected": True,
        }

    if not tenant_id:
        return {
            "allowed": False,
            "reason": "tenant_id_required_for_client_execution",
            "tenant_id": tenant_id,
            "actor_role": actor_role,
            "billing_guard_applied": True,
        }

    state_result = get_billing_runtime_state(tenant_id=tenant_id)
    state = state_result.get("state")

    if not state:
        return {
            "allowed": True,
            "reason": "no_durable_billing_block_found",
            "tenant_id": tenant_id,
            "actor_role": actor_role,
            "billing_guard_applied": True,
            "state": None,
        }

    subscription_status = state.get("subscription_status")
    client_execution_allowed = state.get("client_execution_allowed")
    credit_state = state.get("credit_state")
    execution_block_reason = state.get("execution_block_reason")

    if client_execution_allowed is False or subscription_status in {"past_due", "cancelled", "canceled", "unpaid"} or credit_state == "blocked":
        return {
            "allowed": False,
            "reason": execution_block_reason or subscription_status or "billing_execution_blocked",
            "tenant_id": tenant_id,
            "actor_role": actor_role,
            "billing_guard_applied": True,
            "subscription_status": subscription_status,
            "credit_state": credit_state,
            "client_execution_allowed": client_execution_allowed,
            "state": state,
        }

    return {
        "allowed": True,
        "reason": "billing_state_allows_execution",
        "tenant_id": tenant_id,
        "actor_role": actor_role,
        "billing_guard_applied": True,
        "subscription_status": subscription_status,
        "credit_state": credit_state,
        "client_execution_allowed": client_execution_allowed,
    }


def parse_json_body_safely(body: bytes) -> Dict[str, Any]:
    if not body:
        return {}

    try:
        parsed = json.loads(body.decode("utf-8"))
        return parsed if isinstance(parsed, dict) else {}
    except Exception:
        return {}
