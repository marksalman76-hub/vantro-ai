from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

from backend.app.runtime.durable_execution_history_evidence_runtime import list_execution_evidence


GLOBAL_EXECUTION_EVIDENCE_PROFILE = "global_execution_evidence_layer_v1"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_action_summary(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action") if isinstance(payload.get("action"), dict) else payload
    return {
        "type": action.get("type") or payload.get("action_type"),
        "status": action.get("status") or payload.get("action_status"),
        "provider": action.get("provider") or payload.get("provider"),
        "tenant_id": payload.get("tenant_id"),
        "credential_exposed": False,
    }


def build_execution_evidence_packet(
    *,
    tenant_id: str | None = None,
    limit: int = 25,
    actor_role: str = "client",
) -> Dict[str, Any]:
    admin_view = actor_role in {"owner_admin", "admin", "owner"}
    records_result = list_execution_evidence(tenant_id=tenant_id or "", limit=limit)
    evidence_records = records_result.get("evidence_items", []) if records_result.get("success") else []

    evidence_items: List[Dict[str, Any]] = []
    for item in evidence_records:
        payload = item.get("payload") if isinstance(item.get("payload"), dict) else {}
        base = {
            "record_id": item.get("evidence_id"),
            "evidence_id": item.get("evidence_id"),
            "tenant_id": item.get("tenant_id"),
            "project_id": item.get("project_id"),
            "execution_id": item.get("execution_id"),
            "packet_id": payload.get("packet_id"),
            "assigned_agent": payload.get("assigned_agent") or payload.get("agent_id"),
            "adapter": payload.get("adapter"),
            "action_type": payload.get("action_type") or item.get("evidence_type"),
            "action_status": payload.get("action_status") or item.get("status"),
            "provider": payload.get("provider"),
            "deliverable_id": payload.get("deliverable_id"),
            "evidence_type": item.get("evidence_type"),
            "title": item.get("title"),
            "summary": item.get("summary"),
            "customer_safe": True,
            "credential_values_exposed": False,
            "created_at": item.get("created_at"),
            "action_summary": _safe_action_summary(payload),
        }

        if admin_view:
            base["admin_evidence"] = {
                "provider_reference_id": payload.get("provider_reference_id"),
                "raw_action_safe": payload.get("action") or payload,
                "source_type": item.get("source_type"),
                "source_id": item.get("source_id"),
                "replay_diagnostic": {
                    "can_replay": False,
                    "reason": "Live external actions require a fresh owner-approved execution request.",
                },
            }
        else:
            base["client_evidence"] = {
                "summary": item.get("summary") or f"{base.get('action_type')} via {base.get('provider')}",
                "status": base.get("action_status"),
                "provider": base.get("provider"),
            }

        evidence_items.append(base)

    return {
        "success": bool(records_result.get("success", True)),
        "profile": GLOBAL_EXECUTION_EVIDENCE_PROFILE,
        "canonical_runtime": "durable_execution_history_evidence_runtime",
        "actor_role": actor_role,
        "admin_view": admin_view,
        "tenant_id": tenant_id,
        "count": len(evidence_items),
        "evidence_items": evidence_items,
        "storage_mode": records_result.get("storage_mode"),
        "durable": records_result.get("durable", False),
        "dev_only": records_result.get("dev_only", False),
        "customer_safe": True,
        "credential_values_exposed": False,
        "created_at": _now(),
    }
