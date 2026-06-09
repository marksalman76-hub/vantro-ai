
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4
import json
import os
import threading

ROOT = Path(__file__).resolve().parents[3]
STORE = ROOT / "runtime_outputs" / "media_jobs"
STORE.mkdir(parents=True, exist_ok=True)

CREATIVE_MEDIA_GENERATION_QUEUE = "creative_media_generation_queue"
TRIGGER_ALL_DEFAULT_SCHEDULE_LIMIT = 3
FAST_PACKET_LIST_LIMIT = 2

_LOCK = threading.Lock()

TERMINAL_MEDIA_JOB_STATUSES = {"completed", "provider_unavailable", "blocked", "failed"}

PROVIDER_UNAVAILABLE_STATUSES = {
    "provider_key_missing",
    "prepared_no_live_provider_configured",
    "live_provider_ready_endpoint_missing",
    "endpoint_missing",
    "blocked_live_dispatch_not_enabled",
}

PROVIDER_BLOCKED_STATUSES = {
    "blocked_by_orchestration",
    "blocked_owner_approval_required",
    "blocked_by_safety_policy",
    "safety_blocked",
    "policy_blocked",
}

PROVIDER_FAILED_STATUSES = {
    "invalid_provider_packet",
    "unsupported_provider",
    "provider_execution_failed",
    "provider_http_error",
    "provider_execution_attempted_no_asset_url",
    "provider_job_created_or_attempted",
    "no_playable_or_metadata_asset_result",
    "no_playable_provider_asset_result",
}

SAFE_PROVIDER_UNAVAILABLE_REASON = "Provider execution is not currently available. No credentials or provider secrets were exposed."
SAFE_PROVIDER_BLOCKED_REASON = "Provider execution was blocked by governance or provider safety controls. No credentials or provider secrets were exposed."
SAFE_PROVIDER_FAILED_REASON = "Provider execution was attempted but did not complete safely. No credentials or provider secrets were exposed."
SAFE_PROVIDER_PROCESSING_REASON = "Provider execution is still processing. No playable media asset is available yet."


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _job_path(job_id: str) -> Path:
    return STORE / f"{job_id}.json"


def media_job_store_context() -> Dict[str, Any]:
    return {
        "canonical_store": "backend:runtime_outputs/media_jobs",
        "store_path": "runtime_outputs/media_jobs",
        "environment_context": "backend_processor",
        "store_paths_match": True,
        "credential_values_exposed": False,
    }


def _safe_job_id(value: Any) -> str:
    raw = str(value or "").strip()
    safe = "".join(ch for ch in raw if ch.isalnum() or ch in {"_", "-", "."})
    return safe[:160]


def _asset_media_job_id(asset: Dict[str, Any]) -> str:
    return _safe_job_id(asset.get("media_job_id") or asset.get("job_id") or asset.get("asset_id") or asset.get("id"))


def _is_visible_queued_media_asset(asset: Dict[str, Any]) -> bool:
    if not isinstance(asset, dict):
        return False
    job_id = _asset_media_job_id(asset)
    status = str(asset.get("status") or asset.get("media_job_status") or asset.get("delivery_status") or "").lower()
    provider = str(asset.get("provider") or asset.get("provider_key") or "").lower()
    asset_type = str(asset.get("asset_type") or asset.get("media_type") or asset.get("type") or "").lower()
    return bool(
        job_id
        and "queued" in status
        and (
            provider == "creative_media_queue"
            or asset_type == "creative_media_job_evidence"
            or job_id.startswith("media_job_")
        )
    )


def _job_from_visible_asset(asset: Dict[str, Any]) -> Dict[str, Any]:
    now = _now()
    job_id = _asset_media_job_id(asset)
    return {
        "success": True,
        "job_id": job_id,
        "status": "queued",
        "task": asset.get("task") or asset.get("summary") or asset.get("content") or asset.get("title") or "Create a premium creative media asset.",
        "agent_id": asset.get("agent_id") or asset.get("agent_key") or asset.get("requested_agent") or "creative_media_agent",
        "tenant_id": asset.get("tenant_id") or "owner_admin",
        "include_image": True,
        "include_audio": True,
        "include_video": True,
        "include_avatar": False,
        "lifecycle": "queued",
        "media_asset_count": 0,
        "real_media_asset_count": 0,
        "persisted_asset_count": 0,
        "preview_ready_count": 0,
        "download_ready_count": 0,
        "final_asset_ids": [],
        "final_assets": [],
        "reconciled_from_visible_asset": True,
        "source_runtime": "creative_asset_registry_visible_queue_reconciliation",
        "created_at": asset.get("created_at") or now,
        "updated_at": now,
        "credential_values_exposed": False,
    }


def reconcile_visible_queued_media_asset_jobs(limit: int = 100) -> Dict[str, Any]:
    reconciled = 0
    skipped_reasons: Dict[str, int] = {}
    job_ids: List[str] = []

    try:
        from backend.app.runtime.creative_asset_persistence_bridge import get_persisted_creative_assets

        registry = get_persisted_creative_assets(limit=max(int(limit or 100), 1))
        assets = registry.get("assets", []) if isinstance(registry, dict) else []
    except Exception as exc:
        return {
            **media_job_store_context(),
            "success": False,
            "status": "reconciliation_unavailable",
            "reconciled_job_count": 0,
            "skipped_reasons": {"asset_registry_unavailable": 1},
            "error": str(exc)[:500],
            "credential_values_exposed": False,
        }

    with _LOCK:
        STORE.mkdir(parents=True, exist_ok=True)
        for asset in assets:
            if not isinstance(asset, dict):
                skipped_reasons["invalid_asset_record"] = skipped_reasons.get("invalid_asset_record", 0) + 1
                continue
            if not _is_visible_queued_media_asset(asset):
                continue

            job_id = _asset_media_job_id(asset)
            if not job_id:
                skipped_reasons["missing_media_job_id"] = skipped_reasons.get("missing_media_job_id", 0) + 1
                continue

            path = _job_path(job_id)
            if path.exists():
                skipped_reasons["job_already_in_processor_store"] = skipped_reasons.get("job_already_in_processor_store", 0) + 1
                continue

            path.write_text(json.dumps(_job_from_visible_asset(asset), indent=2), encoding="utf-8")
            reconciled += 1
            job_ids.append(job_id)

    return {
        **media_job_store_context(),
        "success": True,
        "status": "reconciled",
        "reconciled_job_count": reconciled,
        "reconciled_job_ids": job_ids,
        "skipped_reasons": skipped_reasons,
        "credential_values_exposed": False,
    }


def _scrub_sensitive(value: Any) -> Any:
    if isinstance(value, list):
        return [_scrub_sensitive(item) for item in value]
    if not isinstance(value, dict):
        return value
    safe: Dict[str, Any] = {}
    for key, item in value.items():
        lowered = str(key).lower()
        if any(marker in lowered for marker in ("token", "secret", "password", "api_key", "authorization", "credential", "debug", "raw", "internal_prompt", "provider_response", "provider_result", "provider_payload")):
            continue
        safe[str(key)] = _scrub_sensitive(item)
    safe["credential_values_exposed"] = False
    return safe


def _safe_bool(value: Any) -> bool:
    return bool(value)


FAST_PACKET_BLOCKED_MARKERS = (
    "you are executing as",
    "platform standard",
    "output quality requirement",
    "agent-specific behaviour",
    "agent specific behaviour",
    "required structure",
    "system prompt",
    "developer prompt",
    "internal prompt",
    "backend execution",
    "governance",
    "raw provider",
    "provider payload",
    "run delegated workforce",
    "wait for generated media assets",
    "create operational execution task",
)

CREATIVE_SOURCE_FIELDS = (
    "customer_creative_brief",
    "creative_brief",
    "user_creative_brief",
    "campaign_brief",
    "product_brief",
    "asset_brief",
    "customer_request",
    "user_request",
    "creative_request",
    "product_description",
    "brand_description",
    "campaign_context",
    "task",
)


def _compact_text(value: Any, max_len: int = 1000) -> str:
    text = " ".join(str(value or "").replace("\r", " ").replace("\n", " ").split())
    return text[:max_len].strip()


def _blocked_fast_packet_text(value: str) -> bool:
    lowered = str(value or "").lower()
    return any(marker in lowered for marker in FAST_PACKET_BLOCKED_MARKERS) or any(
        marker in lowered
        for marker in ("token", "secret", "password", "api_key", "authorization", "credential")
    )


def _customer_safe_creative_source(job: Dict[str, Any]) -> str:
    for field in CREATIVE_SOURCE_FIELDS:
        raw_value = str(job.get(field) or "")
        candidates = []
        for raw_line in raw_value.replace("\r", "\n").split("\n"):
            line = _compact_text(raw_line, 1200)
            if not line:
                continue
            lowered = line.lower()
            for prefix in (
                "user task:",
                "customer task:",
                "creative request:",
                "customer request:",
                "task:",
                "request:",
            ):
                if lowered.startswith(prefix):
                    line = line[len(prefix):].strip()
                    lowered = line.lower()
            candidates.append(line)
        if not candidates:
            candidates = [_compact_text(raw_value, 1200)]
        for value in candidates:
            if not value or _blocked_fast_packet_text(value):
                continue
            if len(value) < 8:
                continue
            return value
    return ""


def _safe_task_summary(job: Dict[str, Any]) -> str:
    source = _customer_safe_creative_source(job)
    if source:
        return source[:500]
    return "Creative media generation is queued for async final render."


def _status_safe_job(job: Dict[str, Any]) -> Dict[str, Any]:
    safe = _scrub_sensitive(job if isinstance(job, dict) else {})
    summary = _safe_task_summary(job if isinstance(job, dict) else {})
    safe["task"] = summary
    safe["task_summary"] = summary
    safe["customer_task"] = summary
    fast_packet = build_fast_creative_output_packet(job if isinstance(job, dict) else {})
    safe["fast_output_packet"] = fast_packet
    safe["fast_output_packet_available"] = bool(fast_packet.get("fast_output_packet_available"))
    safe["credential_values_exposed"] = False
    return safe


def _trigger_all_schedule_limit(limit: int) -> int:
    try:
        configured = int(os.getenv("CREATIVE_MEDIA_TRIGGER_MAX_JOBS", str(TRIGGER_ALL_DEFAULT_SCHEDULE_LIMIT)))
    except Exception:
        configured = TRIGGER_ALL_DEFAULT_SCHEDULE_LIMIT
    return max(1, min(int(limit or TRIGGER_ALL_DEFAULT_SCHEDULE_LIMIT), configured, 10))


def _durable_media_queue_payload(job: Dict[str, Any]) -> Dict[str, Any]:
    job_id = str(job.get("job_id") or job.get("media_job_id") or "").strip()
    safe_task = _safe_task_summary(job)
    return {
        "job_id": job_id,
        "media_job_id": job_id,
        "queue_name": CREATIVE_MEDIA_GENERATION_QUEUE,
        "creative_media_job_type": str(job.get("creative_media_job_type") or job.get("asset_type") or "creative_media_job"),
        "agent_id": str(job.get("agent_id") or job.get("requested_agent") or "creative_media_agent"),
        "tenant_id": str(job.get("tenant_id") or "owner_admin"),
        "task": safe_task[:1000],
        "task_summary": safe_task[:1000],
        "customer_task": safe_task[:1000],
        "include_image": _safe_bool(job.get("include_image")),
        "include_audio": _safe_bool(job.get("include_audio")),
        "include_video": _safe_bool(job.get("include_video")),
        "include_avatar": _safe_bool(job.get("include_avatar")),
        "source_runtime": "async_media_job_foundation",
        "credential_values_exposed": False,
    }


def build_fast_creative_output_packet(job: Dict[str, Any]) -> Dict[str, Any]:
    agent_id = str(job.get("agent_id") or job.get("requested_agent") or "creative_media_agent").strip()
    include_image = _safe_bool(job.get("include_image"))
    include_audio = _safe_bool(job.get("include_audio"))
    include_video = _safe_bool(job.get("include_video"))
    include_avatar = _safe_bool(job.get("include_avatar"))
    requested_assets = [
        label
        for label, enabled in [
            ("image", include_image),
            ("audio", include_audio),
            ("video", include_video),
            ("avatar_video", include_avatar),
        ]
        if enabled
    ]
    creative_source = _customer_safe_creative_source(job)
    if not creative_source:
        return {
            "packet_type": "fast_creative_media_status_packet",
            "fast_output_packet_available": False,
            "timing_stage": "stage_1_fast_status_response",
            "target_response_seconds": "under_3",
            "final_provider_media_stage": "stage_2_async_final_render",
            "final_asset_status": str(job.get("status") or "queued"),
            "job_status": str(job.get("status") or "queued"),
            "agent_id": agent_id,
            "status_summary": "Creative media generation is queued. Final provider-rendered media will appear after async worker completion.",
            "media_generation_plan": {
                "requested_assets": requested_assets,
                "provider_generation_queued": True,
                "async_final_render_required": bool(requested_assets),
                "final_media_completion_claimed": False,
            },
            "asset_requirements": {
                "image": include_image,
                "audio": include_audio,
                "video": include_video,
                "avatar_video": include_avatar,
            },
            "preview_evidence_status": "queued",
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    hook = f"Lead with the clearest customer benefit, then show proof for: {creative_source[:160]}"
    return {
        "packet_type": "fast_creative_media_output_packet",
        "fast_output_packet_available": True,
        "timing_stage": "stage_1_fast_creative_response",
        "target_response_seconds": "3-10",
        "final_provider_media_stage": "stage_2_async_final_render",
        "final_asset_status": str(job.get("status") or "queued"),
        "job_status": str(job.get("status") or "queued"),
        "agent_id": agent_id,
        "creative_brief": creative_source[:1000],
        "hook": hook,
        "caption": f"{hook} Final media render is queued and will appear when provider output is ready.",
        "scene_directions": [
            "Open with a direct product or offer reveal.",
            "Show the main benefit in one clear visual moment.",
            "Close with a concise call to action and brand-safe proof point.",
        ],
        "media_generation_plan": {
            "requested_assets": requested_assets,
            "provider_generation_queued": True,
            "async_final_render_required": bool(requested_assets),
            "final_media_completion_claimed": False,
        },
        "asset_requirements": {
            "image": include_image,
            "audio": include_audio,
            "video": include_video,
            "avatar_video": include_avatar,
        },
        "preview_evidence_status": "queued",
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def _mark_job_durable_queue_scheduled(job: Dict[str, Any], queue_result: Dict[str, Any]) -> None:
    if not isinstance(job, dict) or not job.get("job_id"):
        return
    updated = dict(job)
    updated["durable_queue_name"] = CREATIVE_MEDIA_GENERATION_QUEUE
    updated["durable_queue_scheduled"] = True
    updated["durable_queue_job_id"] = queue_result.get("queue_id") or queue_result.get("job_id")
    updated["durable_queue_storage_mode"] = queue_result.get("storage_mode")
    updated["background_processor_scheduled"] = True
    fast_packet = build_fast_creative_output_packet(updated)
    updated["fast_output_packet"] = fast_packet
    updated["fast_output_packet_available"] = bool(fast_packet.get("fast_output_packet_available"))
    updated["updated_at"] = _now()
    updated["credential_values_exposed"] = False
    _write_job(updated)


def enqueue_creative_media_job_for_worker(job: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enqueue an existing creative media job for the dedicated worker.

    This is intentionally queue-only. It must not call media processors, provider
    adapters, local binaries, or persistence routines from a web request path.
    """
    safe_job = _scrub_sensitive(job if isinstance(job, dict) else {})
    job_id = str(safe_job.get("job_id") or safe_job.get("media_job_id") or "").strip()
    if not job_id:
        return {
            **media_job_store_context(),
            "success": False,
            "status": "missing_media_job_id",
            "triggered": False,
            "background_processor_scheduled": False,
            "queue_name": CREATIVE_MEDIA_GENERATION_QUEUE,
            "credential_values_exposed": False,
        }

    if str(safe_job.get("status") or "").lower() not in {"queued", "retry_scheduled"}:
        return {
            **media_job_store_context(),
            "success": True,
            "status": "job_not_pending",
            "triggered": False,
            "background_processor_scheduled": False,
            "queue_name": CREATIVE_MEDIA_GENERATION_QUEUE,
            "media_job_id": job_id,
            "current_status": safe_job.get("status"),
            "credential_values_exposed": False,
        }

    from backend.app.runtime.durable_execution_queue_runtime import enqueue_execution_job

    payload = _durable_media_queue_payload(safe_job)
    result = enqueue_execution_job(
        queue_name=CREATIVE_MEDIA_GENERATION_QUEUE,
        tenant_id=str(payload.get("tenant_id") or "owner_admin"),
        project_id=str(safe_job.get("project_id") or "creative_media"),
        agent_id=str(payload.get("agent_id") or "creative_media_agent"),
        action_type="creative_media_generation_job",
        payload=payload,
        idempotency_key=f"creative_media_generation:{job_id}",
        max_attempts=3,
    )

    safe_result = _scrub_sensitive(result if isinstance(result, dict) else {})
    scheduled = bool(safe_result.get("success"))
    if scheduled:
        try:
            _mark_job_durable_queue_scheduled(safe_job, safe_result)
        except Exception:
            scheduled = bool(safe_result.get("success"))

    fast_packet = build_fast_creative_output_packet(safe_job)
    return {
        **media_job_store_context(),
        "success": bool(safe_result.get("success")),
        "status": safe_result.get("status") or ("queued" if scheduled else "durable_queue_unavailable"),
        "triggered": scheduled,
        "background_processor_scheduled": scheduled,
        "queue_name": CREATIVE_MEDIA_GENERATION_QUEUE,
        "media_job_id": job_id,
        "fast_output_packet_available": bool(fast_packet.get("fast_output_packet_available")),
        "fast_output_packet": fast_packet,
        "timing_stage": "stage_1_fast_creative_response",
        "final_provider_media_stage": "stage_2_async_final_render",
        "final_media_completion_claimed": False,
        "durable_queue_job_id": safe_result.get("queue_id") or safe_result.get("job_id"),
        "durable_queue_storage_mode": safe_result.get("storage_mode"),
        "idempotent_replay": bool(safe_result.get("idempotent_replay")),
        "request_path_safe": True,
        "processor_invoked": False,
        "credential_values_exposed": False,
    }


def enqueue_media_job(*, task: str, agent_id: str, tenant_id: str, include_image: bool = True, include_audio: bool = True, include_video: bool = True, include_avatar: bool = False) -> Dict[str, Any]:
    job_id = f"media_job_{uuid4().hex[:12]}"
    job = {
        "success": True,
        "job_id": job_id,
        "status": "queued",
        "task": task,
        "agent_id": agent_id,
        "tenant_id": tenant_id,
        "include_image": include_image,
        "include_audio": include_audio,
        "include_video": include_video,
        "include_avatar": include_avatar,
        "lifecycle": "queued",
        "media_asset_count": 0,
        "real_media_asset_count": 0,
        "persisted_asset_count": 0,
        "preview_ready_count": 0,
        "download_ready_count": 0,
        "final_asset_ids": [],
        "final_assets": [],
        "created_at": _now(),
        "updated_at": _now(),
        "credential_values_exposed": False,
    }
    fast_packet = build_fast_creative_output_packet(job)
    job["fast_output_packet"] = fast_packet
    job["fast_output_packet_available"] = bool(fast_packet.get("fast_output_packet_available"))
    with _LOCK:
        _job_path(job_id).write_text(json.dumps(job, indent=2), encoding="utf-8")
    return job


def read_media_job(job_id: str, *, include_internal: bool = False) -> Dict[str, Any]:
    path = _job_path(job_id)
    if not path.exists():
        return {"success": False, "job_id": job_id, "status": "not_found", "credential_values_exposed": False}
    job = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(job, dict):
        job["credential_values_exposed"] = False
    if include_internal:
        return _scrub_sensitive(job)
    return _status_safe_job(job)


def _latest_durable_media_status_by_job_id(jobs: List[Dict[str, Any]], limit: int = 10) -> Dict[str, Dict[str, Any]]:
    relevant = [
        job
        for job in jobs
        if isinstance(job, dict)
        and job.get("durable_queue_job_id")
        and str(job.get("status") or "").lower() in {"queued", "retry_scheduled", "processing"}
    ][: max(0, min(int(limit or 10), 10))]
    if not relevant:
        return {}
    try:
        from backend.app.runtime.durable_execution_queue_runtime import get_latest_execution_job_event, list_execution_jobs

        queue = list_execution_jobs(queue_name=CREATIVE_MEDIA_GENERATION_QUEUE, limit=100)
    except Exception:
        return {}
    if not isinstance(queue, dict) or not queue.get("success"):
        return {}
    durable_by_id = {
        str(item.get("job_id") or item.get("queue_id") or ""): item
        for item in queue.get("jobs", [])
        if isinstance(item, dict)
    }
    overlays: Dict[str, Dict[str, Any]] = {}
    for job in relevant:
        media_job_id = str(job.get("job_id") or "")
        durable_id = str(job.get("durable_queue_job_id") or "")
        durable = durable_by_id.get(durable_id)
        if not media_job_id or not durable:
            continue
        durable_status = str(durable.get("status") or "").lower()
        status = ""
        if durable_status == "leased":
            status = "processing"
        elif durable_status in {"retry_scheduled", "dead_letter"}:
            status = durable_status
        elif durable_status == "completed":
            event = get_latest_execution_job_event(durable_id, event_type="job_completed")
            details = event.get("details") if isinstance(event, dict) else {}
            status = str((details or {}).get("media_job_status") or "completed").lower()
        elif durable_status == "queued":
            status = "queued"
        if status:
            overlays[media_job_id] = {
                "durable_queue_status": durable_status,
                "worker_observed_status": status,
                "status": status,
                "background_processor_scheduled": True,
                "credential_values_exposed": False,
            }
    return overlays


def list_media_jobs(limit: int = 50, reconcile_visible_assets: bool = False, include_durable_status: bool = False) -> Dict[str, Any]:
    if reconcile_visible_assets:
        reconcile_visible_queued_media_asset_jobs(limit=max(int(limit or 50), 1))
    jobs = []
    for path in sorted(STORE.glob("media_job_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)[:limit]:
        try:
            jobs.append(json.loads(path.read_text(encoding="utf-8")))
        except Exception:
            continue
    if include_durable_status:
        overlays = _latest_durable_media_status_by_job_id(jobs)
        for job in jobs:
            overlay = overlays.get(str(job.get("job_id") or ""))
            if overlay:
                job.update(overlay)
                job["updated_at"] = _now()
                try:
                    _write_job(job)
                except Exception:
                    pass
    jobs = [_status_safe_job(job) for job in jobs]
    status_counts: Dict[str, int] = {}
    for job in jobs:
        status = str(job.get("status") or "unknown")
        status_counts[status] = status_counts.get(status, 0) + 1
    queued_count = status_counts.get("queued", 0)
    return {
        **media_job_store_context(),
        "success": True,
        "status": "ready",
        "job_count": len(jobs),
        "queued_job_count": queued_count,
        "visible_queued_job_count": queued_count,
        "processor_queued_job_count": queued_count,
        "status_counts": status_counts,
        "jobs": jobs,
        "credential_values_exposed": False,
    }


def _write_job(job: Dict[str, Any]) -> None:
    _job_path(str(job["job_id"])).write_text(json.dumps(job, indent=2), encoding="utf-8")


def _label(value: Any, fallback: str = "") -> str:
    text = str(value or fallback).strip()
    if not text:
        return fallback
    return " ".join(part.capitalize() for part in text.replace("_", " ").split())


def _safe_blocked_reason(job: Dict[str, Any]) -> str:
    raw = str(job.get("error") or job.get("blocked_reason") or "").strip()
    if raw:
        lowered = raw.lower()
        if any(marker in lowered for marker in ("token", "secret", "password", "api_key", "authorization", "credential")):
            return "Provider execution is not configured for this media job. Connect the required provider credentials or run it again once provider dispatch is ready."
        if raw in {"no_playable_or_metadata_asset_result", "no_playable_provider_asset_result"}:
            return "Provider execution did not return a playable media asset. Connect or enable a supported media provider, then rerun the media job."
        return raw[:260]
    status = str(job.get("status") or "").lower()
    if status == "queued":
        return "Media generation is queued and waiting for delegated workforce processing."
    if status == "provider_unavailable":
        return SAFE_PROVIDER_UNAVAILABLE_REASON
    if status in {"processing", "running"}:
        return "Media generation is running. Refresh assets shortly."
    if status == "blocked":
        return SAFE_PROVIDER_BLOCKED_REASON
    if status == "failed":
        return "Provider execution could not complete. Check provider readiness and rerun the media job."
    return "Media job evidence is available, but no playable generated asset is attached yet."


def media_job_to_visible_asset_evidence(job: Dict[str, Any], *, audience: str = "admin") -> Dict[str, Any]:
    job_id = str(job.get("job_id") or job.get("media_job_id") or "").strip()
    status = str(job.get("status") or job.get("media_job_status") or "queued").strip()
    agent_id = str(job.get("agent_id") or job.get("requested_agent") or "creative_media_agent").strip()
    final_assets = [asset for asset in job.get("final_assets", []) if isinstance(asset, dict)]
    playable_count = sum(1 for asset in final_assets if asset.get("playable") or asset.get("preview_ready"))
    generated_count = int(job.get("media_asset_count") or job.get("real_media_asset_count") or len(final_assets) or 0)
    blocked_reason = _safe_blocked_reason(job)
    provider_readiness = "ready" if playable_count else ("blocked" if status.lower() == "blocked" else status.lower() or "queued")
    preview_ready = any(asset.get("preview_ready") for asset in final_assets)
    download_ready = any(asset.get("download_ready") for asset in final_assets)
    title = f"Creative media job {_label(status, 'Queued').lower()}"

    return {
        "asset_id": job_id,
        "id": job_id,
        "job_id": job_id,
        "media_job_id": job_id,
        "task_id": job_id,
        "tenant_id": job.get("tenant_id") or "owner_admin",
        "agent_id": agent_id,
        "agent_label": _label(agent_id, "Creative Media Agent"),
        "provider": "creative_media_queue",
        "provider_key": "creative_media_queue",
        "provider_readiness": provider_readiness,
        "asset_type": "creative_media_job_evidence",
        "media_type": "creative_media_job_evidence",
        "title": title,
        "test_label": f"{title}: {_label(agent_id, 'Creative Media Agent')}",
        "file_name": job_id,
        "status": status,
        "delivery_status": "final_asset_ready" if playable_count else provider_readiness,
        "lifecycle_status": "preview_ready" if playable_count else "pending",
        "summary": (
            f"Creative media job {job_id} is {_label(status, 'queued').lower()}. "
            f"Generated assets: {generated_count}. Playable assets: {playable_count}."
        ),
        "blocked_reason": "" if playable_count else blocked_reason,
        "not_playable_reason": "" if playable_count else blocked_reason,
        "preview_ready": bool(preview_ready),
        "download_ready": bool(download_ready),
        "playable": bool(playable_count),
        "metadata_only": not bool(playable_count),
        "media_asset_count": generated_count,
        "real_media_asset_count": int(job.get("real_media_asset_count") or 0),
        "playable_asset_count": playable_count,
        "final_assets": final_assets if audience == "admin" else [],
        "owner_approval_required": False,
        "governed": True,
        "customer_safe": True,
        "client_safe": True,
        "credential_values_exposed": False,
        "created_at": job.get("created_at"),
        "updated_at": job.get("updated_at"),
    }


def _asset_delivery_summary(asset: Dict[str, Any]) -> Dict[str, Any]:
    persistence = asset.get("persistence") if isinstance(asset.get("persistence"), dict) else {}
    return {
        "asset_id": persistence.get("asset_id") or asset.get("asset_id"),
        "media_type": asset.get("media_type") or asset.get("asset_type"),
        "asset_type": asset.get("asset_type") or asset.get("media_type"),
        "status": asset.get("status"),
        "preview_ready": bool(persistence.get("preview_ready") or asset.get("preview_ready")),
        "download_ready": bool(persistence.get("download_ready") or asset.get("download_ready")),
        "playable": bool(persistence.get("playable") or asset.get("playable")),
        "storage_provider": persistence.get("storage_provider"),
    }


def _status_texts(media_pack: Dict[str, Any]) -> List[str]:
    texts: List[str] = []
    for collection_name in ("provider_execution_results", "generation_jobs", "media_assets"):
        collection = media_pack.get(collection_name, [])
        if not isinstance(collection, list):
            continue
        for item in collection:
            if not isinstance(item, dict):
                continue
            for key in ("status", "execution_status", "reason", "error"):
                value = item.get(key)
                if value:
                    texts.append(str(value).strip().lower())
    return texts


def _resolve_no_playable_terminal_state(media_pack: Dict[str, Any]) -> Dict[str, str]:
    statuses = _status_texts(media_pack)
    generation_jobs = [item for item in media_pack.get("generation_jobs", []) if isinstance(item, dict)]
    provider_results = [item for item in media_pack.get("provider_execution_results", []) if isinstance(item, dict)]
    live_generation_available = any(bool(item.get("live_generation_available")) for item in generation_jobs)
    live_execution_attempted = any(bool(item.get("live_provider_execution_attempted")) for item in provider_results + generation_jobs)
    live_attempted_count = int(media_pack.get("live_provider_execution_attempted_count") or 0)

    if any(
        status in {"polling_provider", "processing", "provider_processing"}
        for status in statuses
    ) or any(bool(item.get("provider_polling_required")) for item in provider_results):
        return {
            "status": "processing",
            "lifecycle": "polling_provider",
            "reason": SAFE_PROVIDER_PROCESSING_REASON,
        }

    if any(status in PROVIDER_BLOCKED_STATUSES or "safety" in status for status in statuses):
        return {
            "status": "blocked",
            "lifecycle": "provider_safety_blocked",
            "reason": SAFE_PROVIDER_BLOCKED_REASON,
        }

    if (
        any(status in PROVIDER_UNAVAILABLE_STATUSES for status in statuses)
        or (generation_jobs and not live_generation_available)
        or (provider_results and not live_execution_attempted and live_attempted_count == 0)
        or not provider_results
    ):
        return {
            "status": "provider_unavailable",
            "lifecycle": "provider_unavailable",
            "reason": SAFE_PROVIDER_UNAVAILABLE_REASON,
        }

    if any(status in PROVIDER_FAILED_STATUSES or "failed" in status or "http_error" in status for status in statuses):
        return {
            "status": "failed",
            "lifecycle": "provider_execution_failed",
            "reason": SAFE_PROVIDER_FAILED_REASON,
        }

    return {
        "status": "failed" if live_execution_attempted or live_attempted_count else "provider_unavailable",
        "lifecycle": "provider_execution_failed" if live_execution_attempted or live_attempted_count else "provider_unavailable",
        "reason": SAFE_PROVIDER_FAILED_REASON if live_execution_attempted or live_attempted_count else SAFE_PROVIDER_UNAVAILABLE_REASON,
    }


def _provider_diagnostics_from_media_pack(media_pack: Dict[str, Any], *, default_provider: str = "") -> Dict[str, Any]:
    provider_results = [item for item in media_pack.get("provider_execution_results", []) if isinstance(item, dict)]
    first = provider_results[0] if provider_results else {}
    generation_jobs = [item for item in media_pack.get("generation_jobs", []) if isinstance(item, dict)]
    first_job = generation_jobs[0] if generation_jobs else {}

    provider_selected = str(
        first.get("provider")
        or first_job.get("provider")
        or default_provider
        or ""
    ).strip()

    live_external_calls_enabled = bool(first.get("live_external_calls_enabled"))
    owner_approved_live_activation = bool(first.get("owner_approved_live_activation"))
    real_provider_http_dispatch_enabled = bool(first.get("real_provider_http_dispatch_enabled"))

    return {
        "provider_key_selected": provider_selected,
        "provider_configured": bool(first.get("provider_configured") or first_job.get("live_generation_available")),
        "provider_dispatch_enabled": bool(
            first.get("provider_dispatch_enabled")
            or (
                live_external_calls_enabled
                and owner_approved_live_activation
                and real_provider_http_dispatch_enabled
            )
        ),
        "live_external_calls_enabled": live_external_calls_enabled,
        "owner_approved_live_activation": owner_approved_live_activation,
        "real_provider_http_dispatch_enabled": real_provider_http_dispatch_enabled,
        "provider_unavailable_reason": str(first.get("reason") or first.get("error") or "").strip()[:260],
    }


def process_media_job(job: Dict[str, Any]) -> Dict[str, Any]:
    job_id = str(job.get("job_id") or "")
    if not job_id:
        return {
            "success": False,
            "processed": False,
            "status": "invalid_job",
            "error": "missing_job_id",
            "credential_values_exposed": False,
        }

    try:
        with _LOCK:
            current = read_media_job(job_id, include_internal=True)
            current_status = str(current.get("status") or "").lower()
            if current_status in {"processing", *TERMINAL_MEDIA_JOB_STATUSES}:
                return {
                    "success": True,
                    "processed": False,
                    "status": current_status,
                    "reason": "job_not_queued",
                    "job": current,
                    "credential_values_exposed": False,
                }
            job = current if current.get("success", True) is not False else job
            job["status"] = "processing"
            job["lifecycle"] = "processing"
            job["started_at"] = job.get("started_at") or _now()
            job["updated_at"] = _now()
            _write_job(job)

        from backend.app.runtime.shared_creative_media_generation_runtime import generate_creative_media_pack

        media_pack = generate_creative_media_pack(
            task=job.get("task") or "Create a premium creative media asset.",
            agent_id=job.get("agent_id") or "creative_agent",
            tenant_id=job.get("tenant_id") or "owner_admin",
            include_image=bool(job.get("include_image")),
            include_audio=bool(job.get("include_audio")),
            include_video=bool(job.get("include_video")),
            include_avatar=bool(job.get("include_avatar")),
        )

        final_assets = [
            _asset_delivery_summary(asset)
            for asset in media_pack.get("media_assets", [])
            if isinstance(asset, dict)
        ]
        playable_assets = [asset for asset in final_assets if asset.get("playable") or asset.get("preview_ready") or asset.get("download_ready")]
        provider_diag = _provider_diagnostics_from_media_pack(media_pack)

        if not playable_assets:
            terminal_state = _resolve_no_playable_terminal_state(media_pack)
            job["status"] = terminal_state["status"]
            job["lifecycle"] = terminal_state["lifecycle"]
            job["blocked_reason"] = terminal_state["reason"]
            job["safe_visible_reason"] = terminal_state["reason"]
            job["media_pack_id"] = media_pack.get("media_pack_id")
            job["media_asset_count"] = len(media_pack.get("media_assets", []))
            job["real_media_asset_count"] = media_pack.get("real_media_asset_count", 0)
            job["persisted_asset_count"] = media_pack.get("persisted_asset_count", 0)
            job["final_asset_ids"] = [
                asset.get("asset_id")
                for asset in final_assets
                if asset.get("asset_id")
            ]
            job["final_assets"] = final_assets
            job["preview_ready_count"] = 0
            job["download_ready_count"] = 0
            job["playable_asset_created"] = False
            job["signed_delivery_created"] = False
            job["metadata_only"] = True
            job.update(provider_diag)
            job["provider_unavailable_reason"] = job.get("provider_unavailable_reason") or terminal_state["reason"]
            job[f"{terminal_state['status']}_at"] = _now()
            job["updated_at"] = _now()
            job["credential_values_exposed"] = False
            _write_job(job)
            return {
                "success": True,
                "processed": True,
                "status": terminal_state["status"],
                "job": job,
                "blocked_reason": job["blocked_reason"],
                "safe_visible_reason": job["safe_visible_reason"],
                "credential_values_exposed": False,
            }

        job["status"] = "completed"
        job["lifecycle"] = "final_asset_ready"
        job["media_pack_id"] = media_pack.get("media_pack_id")
        job["media_asset_count"] = len(media_pack.get("media_assets", []))
        job["real_media_asset_count"] = media_pack.get("real_media_asset_count", 0)
        job["persisted_asset_count"] = media_pack.get("persisted_asset_count", 0)
        job["final_asset_ids"] = [
            asset.get("asset_id")
            for asset in final_assets
            if asset.get("asset_id")
        ]
        job["final_assets"] = final_assets
        job["preview_ready_count"] = sum(1 for asset in playable_assets if asset.get("preview_ready"))
        job["download_ready_count"] = sum(1 for asset in playable_assets if asset.get("download_ready"))
        job["playable_asset_created"] = True
        job["signed_delivery_created"] = bool(job["preview_ready_count"] or job["download_ready_count"])
        job["metadata_only"] = False
        job.update(provider_diag)
        job["provider_unavailable_reason"] = ""
        job["completed_at"] = _now()
        job["updated_at"] = _now()
        job["credential_values_exposed"] = False
        _write_job(job)

        return {"success": True, "processed": True, "job": job, "credential_values_exposed": False}
    except Exception as exc:
        job["status"] = "failed"
        job["lifecycle"] = "provider_execution_failed"
        job["blocked_reason"] = SAFE_PROVIDER_FAILED_REASON
        job["safe_visible_reason"] = SAFE_PROVIDER_FAILED_REASON
        job["failed_at"] = _now()
        job["updated_at"] = _now()
        job["credential_values_exposed"] = False
        _write_job(job)
        return {
            "success": True,
            "processed": True,
            "status": "failed",
            "job": job,
            "blocked_reason": job["blocked_reason"],
            "credential_values_exposed": False,
        }


def run_next_media_job() -> Dict[str, Any]:
    queued = [j for j in list_media_jobs(200).get("jobs", []) if j.get("status") == "queued"]
    if not queued:
        return {"success": True, "status": "empty", "processed": False}

    job = queued[-1]
    return process_media_job(job)


def run_all_media_jobs(limit: int = 25) -> Dict[str, Any]:
    return process_queued_creative_media_jobs(limit=limit)


def trigger_next_creative_media_job() -> Dict[str, Any]:
    jobs_result = list_media_jobs(limit=25)
    jobs = [j for j in jobs_result.get("jobs", []) if isinstance(j, dict) and j.get("status") == "queued"]
    if not jobs:
        return {
            **media_job_store_context(),
            "success": True,
            "status": "empty",
            "triggered": True,
            "background_processor_scheduled": False,
            "queue_name": CREATIVE_MEDIA_GENERATION_QUEUE,
            "queued_job_count": 0,
            "request_path_safe": True,
            "processor_invoked": False,
            "credential_values_exposed": False,
        }

    result = enqueue_creative_media_job_for_worker(jobs[-1])
    return {
        **result,
        "success": bool(result.get("success")),
        "triggered": True,
        "background_processor_scheduled": bool(result.get("background_processor_scheduled")),
        "queue_name": CREATIVE_MEDIA_GENERATION_QUEUE,
        "queued_job_count": len(jobs),
        "fast_output_packet_available": bool(result.get("fast_output_packet_available")),
        "timing_stage": "stage_1_fast_creative_response",
        "final_provider_media_stage": "stage_2_async_final_render",
        "final_media_completion_claimed": False,
        "request_path_safe": True,
        "processor_invoked": False,
        "credential_values_exposed": False,
    }


def trigger_all_creative_media_jobs(limit: int = 25) -> Dict[str, Any]:
    safe_limit = _trigger_all_schedule_limit(limit)
    jobs_result = list_media_jobs(limit=max(safe_limit, 25))
    queued = [j for j in jobs_result.get("jobs", []) if isinstance(j, dict) and j.get("status") == "queued"]
    selected = queued[:safe_limit]
    results: List[Dict[str, Any]] = []
    scheduled_count = 0
    skipped_reasons: Dict[str, int] = {}

    for job in selected:
        result = enqueue_creative_media_job_for_worker(job)
        results.append(result)
        if result.get("background_processor_scheduled"):
            scheduled_count += 1
        else:
            reason = str(result.get("status") or "not_scheduled")
            skipped_reasons[reason] = skipped_reasons.get(reason, 0) + 1

    return {
        **media_job_store_context(),
        "success": True,
        "status": "triggered" if scheduled_count else ("empty" if not queued else "not_scheduled"),
        "triggered": True,
        "background_processor_scheduled": bool(scheduled_count),
        "queue_name": CREATIVE_MEDIA_GENERATION_QUEUE,
        "queued_job_count": len(queued),
        "scheduled_job_count": scheduled_count,
        "triggered_job_count": len(results),
        "request_schedule_limit": safe_limit,
        "bounded_trigger": True,
        "fast_output_packet_available": any(bool(result.get("fast_output_packet_available")) for result in results if isinstance(result, dict)),
        "fast_output_packets": [
            result.get("fast_output_packet")
            for result in results
            if isinstance(result, dict) and isinstance(result.get("fast_output_packet"), dict)
        ][:FAST_PACKET_LIST_LIMIT],
        "timing_stage": "stage_1_fast_creative_response",
        "final_provider_media_stage": "stage_2_async_final_render",
        "final_media_completion_claimed": False,
        "durable_queue_results": results,
        "request_path_safe": True,
        "processor_invoked": False,
        "processed_job_count": 0,
        "skipped_reasons": skipped_reasons,
        "credential_values_exposed": False,
    }


def process_queued_creative_media_jobs(limit: int = 25) -> Dict[str, Any]:
    reconciliation = reconcile_visible_queued_media_asset_jobs(limit=max(int(limit or 25), 1))
    results: List[Dict[str, Any]] = []
    processed = 0

    for _ in range(max(int(limit or 25), 1)):
        result = run_next_media_job()
        results.append(result)
        if not result.get("processed"):
            break
        processed += 1
        if result.get("success") is False:
            break

    return {
        **media_job_store_context(),
        "success": True,
        "status": "completed" if processed else "empty",
        "processed_count": processed,
        "reconciliation": reconciliation,
        "results": results,
        "credential_values_exposed": False,
    }
