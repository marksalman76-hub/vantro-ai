
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

from backend.app.runtime.durable_external_action_records import list_external_action_records


GLOBAL_EXECUTION_EVIDENCE_PROFILE = "global_execution_evidence_layer_v1"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_action_summary(action: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "type": action.get("type"),
        "status": action.get("status"),
        "provider": action.get("provider"),
        "tenant_id": action.get("tenant_id"),
        "credential_exposed": False,
    }


def build_execution_evidence_packet(
    *,
    tenant_id: str | None = None,
    limit: int = 25,
    actor_role: str = "client",
) -> Dict[str, Any]:
    admin_view = actor_role in {"owner_admin", "admin", "owner"}

    records_result = list_external_action_records(
        tenant_id=tenant_id,
        limit=limit,
    )

    records = records_result.get("records", []) if records_result.get("success") else []

    evidence_items: List[Dict[str, Any]] = []

    for record in records:
        action = record.get("action") or {}
        base = {
            "record_id": record.get("record_id"),
            "tenant_id": record.get("tenant_id"),
            "packet_id": record.get("packet_id"),
            "assigned_agent": record.get("assigned_agent"),
            "adapter": record.get("adapter"),
            "action_type": record.get("action_type"),
            "action_status": record.get("action_status"),
            "provider": record.get("provider"),
            "deliverable_id": record.get("deliverable_id"),
            "customer_safe": True,
            "credential_values_exposed": False,
            "created_at": record.get("created_at"),
            "action_summary": _safe_action_summary(action),
        }

        if admin_view:
            base["admin_evidence"] = {
                "provider_reference_id": record.get("provider_reference_id"),
                "raw_action_safe": action,
                "replay_diagnostic": {
                    "can_replay": False,
                    "reason": "Live external actions require a fresh owner-approved execution request.",
                },
            }
        else:
            base["client_evidence"] = {
                "summary": f"{record.get('action_type')} via {record.get('provider')}",
                "status": record.get("action_status"),
                "provider": record.get("provider"),
            }

        evidence_items.append(base)

    return {
        "success": True,
        "profile": GLOBAL_EXECUTION_EVIDENCE_PROFILE,
        "actor_role": actor_role,
        "admin_view": admin_view,
        "tenant_id": tenant_id,
        "count": len(evidence_items),
        "evidence_items": evidence_items,
        "customer_safe": True,
        "credential_values_exposed": False,
        "created_at": _now(),
    }
