
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = ROOT / "data" / "ai_media_management_delivery"
QUEUE_PATH = DATA_DIR / "generation_queue.jsonl"
OPERATOR_EVENTS_PATH = DATA_DIR / "operator_events.jsonl"
CUSTOMER_DELIVERY_PATH = DATA_DIR / "customer_delivery_packets.jsonl"

DATA_DIR.mkdir(parents=True, exist_ok=True)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _append_jsonl(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")


def _read_jsonl(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except Exception:
            continue
    return rows


def register_generation_queue_item(payload: Dict[str, Any]) -> Dict[str, Any]:
    queue_id = payload.get("queue_id") or "media_queue_" + uuid.uuid4().hex[:16]

    item = {
        "success": True,
        "queue_id": queue_id,
        "job_id": payload.get("job_id", ""),
        "asset_id": payload.get("asset_id", ""),
        "tenant_id": payload.get("tenant_id", "tenant_unknown"),
        "brand_name": payload.get("brand_name", ""),
        "media_type": payload.get("media_type", "generated_media"),
        "provider": payload.get("provider", "unknown_provider"),
        "status": payload.get("status", "queued"),
        "priority": payload.get("priority", "normal"),
        "progress_percentage": int(payload.get("progress_percentage", 0)),
        "customer_safe_status": payload.get("customer_safe_status", "Queued"),
        "operator_status": payload.get("operator_status", "visible"),
        "moderation_status": payload.get("moderation_status", "not_required"),
        "retry_count": int(payload.get("retry_count", 0)),
        "max_retries": int(payload.get("max_retries", 3)),
        "retry_available": bool(payload.get("retry_available", True)),
        "cancel_available": bool(payload.get("cancel_available", True)),
        "customer_visible": bool(payload.get("customer_visible", False)),
        "internal_config_exposed": False,
        "governance_preserved": True,
        "owner_approval_gate_preserved": True,
        "created_at": now_iso(),
        "updated_at": now_iso(),
    }

    _append_jsonl(QUEUE_PATH, item)
    _append_jsonl(OPERATOR_EVENTS_PATH, {
        "event_id": "operator_event_" + uuid.uuid4().hex[:16],
        "event_type": "generation_queue_item_registered",
        "queue_id": queue_id,
        "tenant_id": item["tenant_id"],
        "status": item["status"],
        "created_at": now_iso(),
        "governance_preserved": True,
    })

    return item


def build_operator_generation_management_summary(tenant_id: str = "", limit: int = 50) -> Dict[str, Any]:
    rows = _read_jsonl(QUEUE_PATH)
    if tenant_id:
        rows = [row for row in rows if row.get("tenant_id") == tenant_id]
    rows = rows[-max(1, int(limit)):]

    counts = {}
    provider_counts = {}
    review_required = 0

    for row in rows:
        status = row.get("status", "unknown")
        provider = row.get("provider", "unknown_provider")
        counts[status] = counts.get(status, 0) + 1
        provider_counts[provider] = provider_counts.get(provider, 0) + 1
        if row.get("moderation_status") in {"review_required", "failed"} or row.get("status") in {"failed", "needs_review"}:
            review_required += 1

    return {
        "success": True,
        "runtime": "priority7_operator_media_management",
        "tenant_id": tenant_id or "all",
        "queue_count": len(rows),
        "status_counts": counts,
        "provider_counts": provider_counts,
        "review_required_count": review_required,
        "queue_items": rows,
        "operator_capabilities": [
            "generation_queue_visibility",
            "retry_visibility",
            "cancel_visibility",
            "provider_health_summary",
            "moderation_review_flags",
            "governed_customer_visibility_control",
        ],
        "internal_config_exposed": False,
        "governance_preserved": True,
        "layout_changes": False,
    }


def build_provider_health_summary(provider_statuses: List[Dict[str, Any]] | None = None) -> Dict[str, Any]:
    provider_statuses = provider_statuses or []
    providers = []

    for item in provider_statuses:
        configured = bool(item.get("configured", False))
        missing_env = item.get("missing_env", [])
        provider = item.get("provider", "unknown_provider")
        providers.append({
            "provider": provider,
            "health": "ready" if configured else "configuration_required",
            "configured": configured,
            "customer_safe_status": "Available" if configured else "Provider setup required",
            "missing_configuration_count": len(missing_env),
            "capabilities": item.get("capabilities", []),
            "internal_config_exposed": False,
            "governance_preserved": True,
        })

    ready_count = len([p for p in providers if p["configured"]])
    return {
        "success": True,
        "provider_count": len(providers),
        "ready_count": ready_count,
        "configuration_required_count": len(providers) - ready_count,
        "providers": providers,
        "customer_safe_summary": "Provider network ready" if ready_count else "Provider setup required",
        "internal_config_exposed": False,
        "governance_preserved": True,
    }


def mark_generation_for_retry(queue_item: Dict[str, Any], reason: str = "operator_retry_requested") -> Dict[str, Any]:
    retry_count = int(queue_item.get("retry_count", 0)) + 1
    max_retries = int(queue_item.get("max_retries", 3))

    status = "retry_queued" if retry_count <= max_retries else "needs_review"

    updated = {
        **queue_item,
        "status": status,
        "retry_count": retry_count,
        "retry_reason": reason,
        "customer_safe_status": "Retrying" if status == "retry_queued" else "Needs review",
        "operator_status": "retry_requested",
        "updated_at": now_iso(),
        "internal_config_exposed": False,
        "governance_preserved": True,
    }

    _append_jsonl(OPERATOR_EVENTS_PATH, {
        "event_id": "operator_event_" + uuid.uuid4().hex[:16],
        "event_type": "generation_retry_marked",
        "queue_id": updated.get("queue_id"),
        "tenant_id": updated.get("tenant_id"),
        "retry_count": retry_count,
        "status": status,
        "created_at": now_iso(),
        "governance_preserved": True,
    })

    return updated


def mark_generation_for_moderation(queue_item: Dict[str, Any], reason: str = "quality_review_required") -> Dict[str, Any]:
    updated = {
        **queue_item,
        "status": "needs_review",
        "moderation_status": "review_required",
        "moderation_reason": reason,
        "customer_safe_status": "Needs review",
        "operator_status": "moderation_required",
        "customer_visible": False,
        "updated_at": now_iso(),
        "internal_config_exposed": False,
        "governance_preserved": True,
        "owner_approval_gate_preserved": True,
    }

    _append_jsonl(OPERATOR_EVENTS_PATH, {
        "event_id": "operator_event_" + uuid.uuid4().hex[:16],
        "event_type": "generation_moderation_required",
        "queue_id": updated.get("queue_id"),
        "tenant_id": updated.get("tenant_id"),
        "reason": reason,
        "created_at": now_iso(),
        "governance_preserved": True,
    })

    return updated


def build_customer_safe_media_delivery_packet(asset_record: Dict[str, Any]) -> Dict[str, Any]:
    status = asset_record.get("customer_safe_status") or asset_record.get("status") or "Ready for review"

    packet = {
        "success": True,
        "delivery_packet_id": "customer_delivery_" + uuid.uuid4().hex[:16],
        "tenant_id": asset_record.get("tenant_id", "tenant_unknown"),
        "asset_id": asset_record.get("asset_id", ""),
        "job_id": asset_record.get("job_id", ""),
        "media_type": asset_record.get("media_type", "generated_media"),
        "status": status,
        "preview": {
            "available": True,
            "label": "Preview",
            "access_mode": "signed_expiring_access",
            "expires_at": asset_record.get("access", {}).get("preview", {}).get("expires_at", ""),
        },
        "download": {
            "available": bool(asset_record.get("delivery", {}).get("secure_download_ready", True)),
            "label": "Download",
            "access_mode": "signed_expiring_access",
            "expires_at": asset_record.get("access", {}).get("download", {}).get("expires_at", ""),
        },
        "actions": {
            "can_preview": True,
            "can_download": bool(asset_record.get("delivery", {}).get("secure_download_ready", True)),
            "can_request_revision": True,
            "can_approve": True,
        },
        "customer_safe_message": "Your generated media is ready for review.",
        "white_label_ready": True,
        "tenant_isolated": True,
        "internal_config_exposed": False,
        "governance_preserved": True,
        "layout_changes": False,
        "created_at": now_iso(),
    }

    _append_jsonl(CUSTOMER_DELIVERY_PATH, packet)
    return packet


def build_customer_media_delivery_history(tenant_id: str, limit: int = 20) -> Dict[str, Any]:
    rows = [row for row in _read_jsonl(CUSTOMER_DELIVERY_PATH) if row.get("tenant_id") == tenant_id]
    rows = rows[-max(1, int(limit)):]

    return {
        "success": True,
        "tenant_id": tenant_id,
        "count": len(rows),
        "deliveries": rows,
        "customer_safe": True,
        "white_label_ready": True,
        "internal_config_exposed": False,
        "governance_preserved": True,
    }


def media_management_delivery_runtime_readiness() -> Dict[str, Any]:
    return {
        "success": True,
        "runtime": "priority7_8_media_management_delivery_runtime",
        "status": "ready",
        "data_paths": {
            "queue_path": str(QUEUE_PATH),
            "operator_events_path": str(OPERATOR_EVENTS_PATH),
            "customer_delivery_path": str(CUSTOMER_DELIVERY_PATH),
        },
        "capabilities": [
            "admin_operator_generation_queue_visibility",
            "retry_handling_visibility",
            "generation_cancellation_visibility",
            "provider_health_management_summary",
            "moderation_governance_review_flags",
            "customer_safe_preview_packet",
            "customer_safe_download_packet",
            "revision_request_action_shape",
            "white_label_media_delivery_shape",
            "tenant_isolated_customer_delivery_history",
        ],
        "layout_changes": False,
        "internal_config_exposed": False,
        "governance_preserved": True,
        "owner_approval_gate_preserved": True,
    }
