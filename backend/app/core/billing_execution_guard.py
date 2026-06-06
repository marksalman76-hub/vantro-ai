from __future__ import annotations

import json
from typing import Any, Dict, Optional

from backend.app.core.canonical_billing_state_runtime import (
    OWNER_ADMIN_ROLES,
    evaluate_billing_execution_entitlement,
    normalise_actor_role,
    owner_admin_bypasses_client_billing,
)


def _normalise_role(actor_role: Optional[str]) -> str:
    return normalise_actor_role(actor_role)


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
    return evaluate_billing_execution_entitlement(
        tenant_id=tenant_id,
        actor_role=actor_role,
    )


def parse_json_body_safely(body: bytes) -> Dict[str, Any]:
    if not body:
        return {}

    try:
        parsed = json.loads(body.decode("utf-8"))
        return parsed if isinstance(parsed, dict) else {}
    except Exception:
        return {}
