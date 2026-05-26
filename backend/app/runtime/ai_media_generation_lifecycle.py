from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


DATA_DIR = Path("data/ai_media_generation_lifecycle")
JOBS_FILE = DATA_DIR / "generation_jobs.jsonl"
EVENTS_FILE = DATA_DIR / "generation_events.jsonl"
ASSETS_FILE = DATA_DIR / "generated_assets.jsonl"
DELIVERY_FILE = DATA_DIR / "delivery_packets.jsonl"


JOB_TERMINAL_STATES = {"completed", "failed", "cancelled", "manual_review_required"}
JOB_ACTIVE_STATES = {"queued", "submitted", "polling", "retry_scheduled", "processing"}


def _ensure_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _append_jsonl(path: Path, payload: Dict[str, Any]) -> None:
    _ensure_dirs()
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")


def _read_jsonl(path: Path, limit: int = 100) -> List[Dict[str, Any]]:
    if not path.exists():
        return []

    rows: List[Dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except Exception:
            continue

    return rows[-limit:]


def _safe_text(value: Any, fallback: str = "") -> str:
    if value is None:
        return fallback
    return str(value).strip() or fallback


def _new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:16]}"


def generation_lifecycle_readiness() -> Dict[str, Any]:
    _ensure_dirs()
    return {
        "success": True,
        "runtime": "ai_media_generation_lifecycle",
        "status": "ready",
        "capabilities": [
            "async_generation_job_runtime",
            "provider_polling_engine",
            "asset_persistence_runtime",
            "execution_history_linkage",
            "failure_retry_orchestration",
            "provider_timeout_handling",
            "generated_asset_delivery_packets",
            "runtime_safe_generation_event_logging",
        ],
        "storage": {
            "jobs_file": str(JOBS_FILE),
            "events_file": str(EVENTS_FILE),
            "assets_file": str(ASSETS_FILE),
            "delivery_file": str(DELIVERY_FILE),
        },
        "governance_preserved": True,
        "secret_exposure": False,
        "layout_changes": False,
    }


def log_generation_event(
    *,
    job_id: str,
    tenant_id: str,
    event_type: str,
    status: str,
    details: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    event = {
        "event_id": _new_id("media_event"),
        "job_id": job_id,
        "tenant_id": tenant_id,
        "event_type": event_type,
        "status": status,
        "details": details or {},
        "created_at": _now(),
        "secret_exposure": False,
    }
    _append_jsonl(EVENTS_FILE, event)
    return event


def create_generation_job(
    *,
    tenant_id: str,
    provider_ready_packet: Dict[str, Any],
    provider_route: Optional[Dict[str, Any]] = None,
    source_run_id: Optional[str] = None,
    requested_by: str = "owner_admin",
    max_attempts: int = 3,
    timeout_seconds: int = 300,
) -> Dict[str, Any]:
    if not isinstance(provider_ready_packet, dict):
        raise ValueError("provider_ready_packet must be a dictionary")

    job_id = _new_id("media_job")

    job = {
        "job_id": job_id,
        "tenant_id": _safe_text(tenant_id, "tenant_unknown"),
        "source_run_id": source_run_id,
        "requested_by": requested_by,
        "status": "queued",
        "attempt_count": 0,
        "max_attempts": max(1, int(max_attempts or 3)),
        "timeout_seconds": max(30, int(timeout_seconds or 300)),
        "provider_id": (provider_route or {}).get("selected_provider"),
        "provider_route": provider_route or {},
        "provider_ready_packet": provider_ready_packet,
        "execution_history": [],
        "asset_ids": [],
        "delivery_packet_id": None,
        "failure_reason": None,
        "manual_review_required": False,
        "created_at": _now(),
        "updated_at": _now(),
        "governance_preserved": True,
        "secret_exposure": False,
        "layout_changes": False,
    }

    _append_jsonl(JOBS_FILE, job)
    log_generation_event(
        job_id=job_id,
        tenant_id=job["tenant_id"],
        event_type="generation_job_created",
        status="queued",
        details={
            "source_run_id": source_run_id,
            "provider_id": job.get("provider_id"),
            "media_type": provider_ready_packet.get("media_type"),
            "platform": provider_ready_packet.get("platform"),
        },
    )

    return {
        "success": True,
        "runtime": "ai_media_generation_lifecycle",
        "job": job,
    }


def schedule_provider_submission(job: Dict[str, Any]) -> Dict[str, Any]:
    updated = dict(job)
    updated["status"] = "submitted"
    updated["attempt_count"] = int(updated.get("attempt_count") or 0) + 1
    updated["updated_at"] = _now()

    history_item = {
        "event": "provider_submission_scheduled",
        "attempt": updated["attempt_count"],
        "provider_id": updated.get("provider_id"),
        "created_at": _now(),
    }
    updated.setdefault("execution_history", []).append(history_item)

    _append_jsonl(JOBS_FILE, updated)
    log_generation_event(
        job_id=updated["job_id"],
        tenant_id=updated["tenant_id"],
        event_type="provider_submission_scheduled",
        status="submitted",
        details=history_item,
    )

    return {
        "success": True,
        "job": updated,
    }


def build_polling_plan(job: Dict[str, Any]) -> Dict[str, Any]:
    timeout_seconds = int(job.get("timeout_seconds") or 300)
    return {
        "success": True,
        "job_id": job.get("job_id"),
        "provider_id": job.get("provider_id"),
        "polling_enabled": True,
        "poll_interval_seconds": 10,
        "max_poll_seconds": timeout_seconds,
        "max_poll_attempts": max(3, timeout_seconds // 10),
        "terminal_states": sorted(JOB_TERMINAL_STATES),
        "active_states": sorted(JOB_ACTIVE_STATES),
        "timeout_policy": {
            "timeout_seconds": timeout_seconds,
            "on_timeout": "schedule_retry_or_manual_review",
            "provider_timeout_handling_enabled": True,
        },
        "secret_exposure": False,
    }


def classify_generation_failure(
    *,
    provider_error: Optional[str] = None,
    status_code: Optional[int] = None,
    attempt_count: int = 0,
    max_attempts: int = 3,
) -> Dict[str, Any]:
    error_text = _safe_text(provider_error).lower()

    if "timeout" in error_text:
        failure_type = "provider_timeout"
        retryable = True
    elif status_code and int(status_code) >= 500:
        failure_type = "provider_server_error"
        retryable = True
    elif status_code and int(status_code) in {401, 403}:
        failure_type = "provider_auth_or_permission_error"
        retryable = False
    elif "quality" in error_text or "brand" in error_text or "face" in error_text:
        failure_type = "quality_or_consistency_failure"
        retryable = True
    else:
        failure_type = "provider_execution_failure"
        retryable = True

    attempts_remaining = int(attempt_count) < int(max_attempts)

    return {
        "failure_type": failure_type,
        "retryable": retryable,
        "attempts_remaining": attempts_remaining,
        "retry_recommended": bool(retryable and attempts_remaining),
        "manual_review_required": bool(not retryable or not attempts_remaining),
        "safe_error": _safe_text(provider_error, "provider_error"),
        "status_code": status_code,
        "secret_exposure": False,
    }


def schedule_retry_or_review(
    *,
    job: Dict[str, Any],
    provider_error: Optional[str] = None,
    status_code: Optional[int] = None,
) -> Dict[str, Any]:
    classification = classify_generation_failure(
        provider_error=provider_error,
        status_code=status_code,
        attempt_count=int(job.get("attempt_count") or 0),
        max_attempts=int(job.get("max_attempts") or 3),
    )

    updated = dict(job)
    updated["failure_reason"] = classification["failure_type"]
    updated["manual_review_required"] = classification["manual_review_required"]
    updated["status"] = "retry_scheduled" if classification["retry_recommended"] else "manual_review_required"
    updated["updated_at"] = _now()
    updated.setdefault("execution_history", []).append({
        "event": "failure_classified",
        "classification": classification,
        "created_at": _now(),
    })

    _append_jsonl(JOBS_FILE, updated)
    log_generation_event(
        job_id=updated["job_id"],
        tenant_id=updated["tenant_id"],
        event_type="generation_failure_classified",
        status=updated["status"],
        details=classification,
    )

    return {
        "success": True,
        "job": updated,
        "classification": classification,
    }


def persist_generated_asset(
    *,
    job_id: str,
    tenant_id: str,
    provider_id: str,
    asset_type: str,
    asset_url: Optional[str] = None,
    storage_uri: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    asset_id = _new_id("media_asset")

    asset = {
        "asset_id": asset_id,
        "job_id": job_id,
        "tenant_id": tenant_id,
        "provider_id": provider_id,
        "asset_type": asset_type,
        "asset_url": asset_url,
        "storage_uri": storage_uri,
        "metadata": metadata or {},
        "created_at": _now(),
        "governance_preserved": True,
        "tenant_isolation_required": True,
        "secret_exposure": False,
    }

    _append_jsonl(ASSETS_FILE, asset)
    log_generation_event(
        job_id=job_id,
        tenant_id=tenant_id,
        event_type="generated_asset_persisted",
        status="asset_recorded",
        details={
            "asset_id": asset_id,
            "asset_type": asset_type,
            "provider_id": provider_id,
        },
    )

    return {
        "success": True,
        "asset": asset,
    }


def build_delivery_packet(
    *,
    job: Dict[str, Any],
    assets: List[Dict[str, Any]],
    delivery_status: str = "ready_for_review",
) -> Dict[str, Any]:
    delivery_packet_id = _new_id("media_delivery")

    packet = {
        "delivery_packet_id": delivery_packet_id,
        "job_id": job.get("job_id"),
        "tenant_id": job.get("tenant_id"),
        "status": delivery_status,
        "asset_count": len(assets),
        "assets": assets,
        "source_run_id": job.get("source_run_id"),
        "provider_id": job.get("provider_id"),
        "media_type": job.get("provider_ready_packet", {}).get("media_type"),
        "platform": job.get("provider_ready_packet", {}).get("platform"),
        "governance": {
            "do_not_publish_without_governance": True,
            "owner_review_required_for_spend_or_campaign_scaling": True,
            "client_safe_output_only": True,
            "internal_rules_hidden_from_client": True,
        },
        "quality_controls": job.get("provider_ready_packet", {}).get("quality_controls", {}),
        "continuity_controls": job.get("provider_ready_packet", {}).get("continuity_controls", {}),
        "multilingual_controls": job.get("provider_ready_packet", {}).get("multilingual_controls", {}),
        "created_at": _now(),
        "secret_exposure": False,
        "layout_changes": False,
    }

    _append_jsonl(DELIVERY_FILE, packet)
    log_generation_event(
        job_id=str(job.get("job_id")),
        tenant_id=str(job.get("tenant_id")),
        event_type="delivery_packet_created",
        status=delivery_status,
        details={
            "delivery_packet_id": delivery_packet_id,
            "asset_count": len(assets),
        },
    )

    return {
        "success": True,
        "delivery_packet": packet,
    }


def list_generation_jobs(limit: int = 25) -> Dict[str, Any]:
    return {
        "success": True,
        "jobs": list(reversed(_read_jsonl(JOBS_FILE, limit=limit))),
        "limit": limit,
    }


def list_generation_events(limit: int = 50) -> Dict[str, Any]:
    return {
        "success": True,
        "events": list(reversed(_read_jsonl(EVENTS_FILE, limit=limit))),
        "limit": limit,
    }
