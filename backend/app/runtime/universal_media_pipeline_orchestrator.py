
from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[3]
STORE = ROOT / "runtime_outputs" / "universal_complete_media_jobs"
EVENTS = STORE / "events"
ASSETS = ROOT / "runtime_outputs" / "universal_complete_media_assets"

STORE.mkdir(parents=True, exist_ok=True)
EVENTS.mkdir(parents=True, exist_ok=True)
ASSETS.mkdir(parents=True, exist_ok=True)

TERMINAL_STATUSES = {
    "completed",
    "failed",
    "blocked",
    "blocked_missing_prompt",
    "blocked_owner_approval_required",
    "media_script_ready",
    "media_script_failed",
    "universal_complete_media_preflight_blocked",
    "universal_complete_media_preflight_dry_run",
    "provider_unavailable",
    "provider_not_ready",
    "universal_complete_media_visual_failed",
    "universal_complete_media_audio_failed",
    "universal_complete_media_composition_failed",
    "synchronised_composition_exception",
    "synchronised_composition_output_missing",
}

SAFE_PUBLIC_KEYS = {
    "success",
    "accepted",
    "job_id",
    "parent_job_id",
    "status",
    "stage",
    "message",
    "prompt_summary",
    "output_type",
    "platform",
    "duration_seconds",
    "aspect_ratio",
    "media_type",
    "asset_type",
    "provider",
    "video_provider",
    "audio_provider",
    "universal_complete_media_workflow",
    "one_prompt_complete_media",
    "requested_from",
    "portal",
    "created_at",
    "updated_at",
    "started_at",
    "completed_at",
    "failed_at",
    "polling_required",
    "playable",
    "preview_ready",
    "download_ready",
    "preview_url",
    "signed_preview_url",
    "download_url",
    "final_media_type",
    "final_duration_seconds",
    "child_jobs",
    "failed_provider_attempts",
    "selected_video_job_id",
    "selected_video_provider",
    "visual_attempt_count",
    "provider_attempt_count",
    "support_failure_message",
    "progress",
    "current_child_job_id",
    "video_job_id",
    "audio_job_id",
    "composition_job_id",
    "video_status",
    "audio_status",
    "composition_status",
    "quality_requirements",
    "media_script_preview",
    "script_ready",
    "script_approval_required",
    "script_approved",
    "voiceover_estimated_duration_seconds",
    "script_duration_fit",
    "customer_safe",
    "credential_values_exposed",
    "internal_config_exposed",
}

ADMIN_EXTRA_KEYS = {
    "timed_plan",
    "provider_status",
    "provider_result_status",
    "video_error",
    "audio_error",
    "composition_error",
    "error",
    "reason",
    "provider_visual_prompt_character_count",
    "provider_voice_prompt_character_count",
    "provider_visual_prompt_limit",
    "provider_visual_prompt_truncated",
    "visual_prompt_character_count",
    "voice_prompt_character_count",
    "voice_prompt_words",
    "raw_provider_status",
    "direct_provider_snapshot",
    "media_script_packet",
    "lead_scripting_agent",
    "contributing_scripting_agents",
    "preflight",
    "failed_preflight_checks",
    "blocked_provider_calls",
    "estimated_duration_seconds",
    "requested_duration_seconds",
    "estimated_credit_risk",
    "executable_visual_providers",
    "non_executable_visual_providers",
    "executable_audio_providers",
    "composition_path_available",
    "composition_tool",
    "selected_visual_provider_order",
    "selected_audio_provider",
    "estimated_stages",
    "dry_run",
    "smoke_test_mode",
    "smoke_test_label",
    "paid_provider_calls_started",
    "safe_provider_diagnostics",
    "admin_provider_diagnostics",
    "runway_key_diagnostics",
    "orchestrator_events",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_id(prefix: str = "universal_complete_media_job") -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


def _safe_job_id(value: Any) -> str:
    return "".join(ch for ch in str(value or "") if ch.isalnum() or ch in {"_", "-", "."})[:160]


def _job_path(job_id: str) -> Path:
    return STORE / f"{_safe_job_id(job_id)}.json"


def _event_path(job_id: str) -> Path:
    return EVENTS / f"{_safe_job_id(job_id)}.jsonl"


def _read_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _write_json_atomic(path: Path, payload: Dict[str, Any]) -> Dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    tmp.replace(path)
    return payload


def _append_event(job_id: str, event: Dict[str, Any]) -> None:
    row = {
        "job_id": job_id,
        "event_at": _now(),
        **dict(event or {}),
        "customer_safe": True,
        "credential_values_exposed": False,
    }
    with _event_path(job_id).open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, sort_keys=True) + "\n")


def _summarise_prompt(prompt: str, limit: int = 220) -> str:
    text = " ".join(str(prompt or "").split())
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def _public_record(record: Dict[str, Any], *, audience: str = "client") -> Dict[str, Any]:
    allowed = set(SAFE_PUBLIC_KEYS)
    if audience in {"admin", "owner", "owner_admin"}:
        allowed |= ADMIN_EXTRA_KEYS

    clean = {k: v for k, v in dict(record or {}).items() if k in allowed}
    clean["customer_safe"] = True
    clean["credential_values_exposed"] = False
    if audience not in {"admin", "owner", "owner_admin"}:
        clean["internal_config_exposed"] = False
    return clean


def _merge_status(parent: Dict[str, Any], direct: Dict[str, Any]) -> Dict[str, Any]:
    merged = dict(parent or {})
    if not direct or direct.get("status") == "not_found":
        return merged

    for key in [
        "success",
        "accepted",
        "status",
        "provider_status",
        "provider_result_status",
        "playable",
        "preview_ready",
        "download_ready",
        "asset_path",
        "download_url",
        "preview_url",
        "signed_preview_url",
        "final_media_type",
        "final_duration_seconds",
        "video_job_id",
        "audio_job_id",
        "composition_job_id",
        "video_status",
        "audio_status",
        "composition_status",
        "video_error",
        "audio_error",
        "composition_error",
        "error",
        "reason",
        "timed_plan",
        "quality_requirements",
        "completed_at",
        "failed_at",
        "failed_provider_attempts",
        "selected_video_job_id",
        "selected_video_provider",
        "visual_attempt_count",
        "provider_attempt_count",
        "safe_provider_diagnostics",
        "admin_provider_diagnostics",
        "runway_key_diagnostics",
        "support_failure_message",
        "progress",
        "preflight",
        "failed_preflight_checks",
        "blocked_provider_calls",
        "estimated_duration_seconds",
        "requested_duration_seconds",
        "estimated_credit_risk",
        "executable_visual_providers",
        "non_executable_visual_providers",
        "executable_audio_providers",
        "composition_path_available",
        "composition_tool",
        "selected_visual_provider_order",
        "selected_audio_provider",
        "estimated_stages",
        "dry_run",
        "smoke_test_mode",
        "smoke_test_label",
        "paid_provider_calls_started",
        "media_script_packet",
        "media_script_preview",
        "script_ready",
        "script_approval_required",
        "script_approved",
        "lead_scripting_agent",
        "contributing_scripting_agents",
        "voiceover_estimated_duration_seconds",
        "script_duration_fit",
    ]:
        if key in direct and direct.get(key) not in [None, ""]:
            merged[key] = direct.get(key)

    child_jobs = dict(merged.get("child_jobs") or {})
    direct_child_jobs = direct.get("child_jobs") if isinstance(direct.get("child_jobs"), dict) else {}
    for key, value in direct_child_jobs.items():
        child_jobs[key] = value

    for child_key, child_id_key, status_key in [
        ("video", "video_job_id", "video_status"),
        ("audio", "audio_job_id", "audio_status"),
        ("composition", "composition_job_id", "composition_status"),
    ]:
        child_id = merged.get(child_id_key) or direct.get(child_id_key)
        if child_id:
            child_jobs[child_key] = {
                **dict(child_jobs.get(child_key) or {}),
                "job_id": child_id,
                "status": merged.get(status_key) or direct.get(status_key) or "linked",
            }

    if child_jobs:
        merged["child_jobs"] = child_jobs

    status = str(merged.get("status") or "").strip()
    merged["polling_required"] = status not in TERMINAL_STATUSES
    merged["updated_at"] = _now()

    if status in TERMINAL_STATUSES and status != "completed":
        merged.setdefault("failed_at", _now())

    return merged


def _read_direct_status(job_id: str) -> Dict[str, Any]:
    try:
        from backend.app.runtime.direct_media_provider_execution_runtime import get_direct_media_provider_job_status

        return get_direct_media_provider_job_status(job_id)
    except Exception as error:
        return {
            "success": False,
            "status": "direct_status_lookup_failed",
            "job_id": job_id,
            "error": str(error)[:800],
            "customer_safe": True,
            "credential_values_exposed": False,
        }


def write_universal_parent_job(record: Dict[str, Any]) -> Dict[str, Any]:
    job_id = _safe_job_id(record.get("job_id") or record.get("parent_job_id") or _safe_id())
    existing = _read_json(_job_path(job_id))
    merged = {
        **existing,
        **dict(record or {}),
        "job_id": job_id,
        "parent_job_id": job_id,
        "universal_complete_media_workflow": True,
        "one_prompt_complete_media": True,
        "customer_safe": True,
        "credential_values_exposed": False,
        "internal_config_exposed": False,
        "updated_at": _now(),
    }
    if not merged.get("created_at"):
        merged["created_at"] = _now()

    _write_json_atomic(_job_path(job_id), merged)
    _append_event(job_id, {"event": "parent_job_updated", "status": merged.get("status")})
    return merged


def accept_universal_media_pipeline_job(payload: Dict[str, Any], *, portal: str = "admin") -> Dict[str, Any]:
    safe_payload = dict(payload or {})
    job_id = _safe_job_id(safe_payload.get("job_id") or _safe_id())
    prompt = (
        safe_payload.get("prompt")
        or safe_payload.get("task")
        or safe_payload.get("creative_brief")
        or safe_payload.get("user_prompt")
        or (safe_payload.get("complete_media_config") or {}).get("prompt")
        or ""
    )

    parent = write_universal_parent_job({
        "success": True,
        "accepted": True,
        "job_id": job_id,
        "status": "accepted",
        "stage": "accepted",
        "portal": portal,
        "requested_from": safe_payload.get("requested_from") or safe_payload.get("source") or portal,
        "prompt_summary": _summarise_prompt(prompt),
        "output_type": safe_payload.get("output_type") or (safe_payload.get("complete_media_config") or {}).get("output_type") or "Complete video with voiceover",
        "platform": safe_payload.get("platform") or (safe_payload.get("complete_media_config") or {}).get("platform") or "General",
        "duration_seconds": safe_payload.get("duration_seconds") or (safe_payload.get("complete_media_config") or {}).get("duration_seconds"),
        "aspect_ratio": safe_payload.get("aspect_ratio") or (safe_payload.get("complete_media_config") or {}).get("aspect_ratio"),
        "media_type": "complete_video",
        "asset_type": "video",
        "provider": "universal_complete_media_workflow",
        "video_provider": safe_payload.get("video_provider") or (safe_payload.get("complete_media_config") or {}).get("video_provider") or "runway",
        "audio_provider": safe_payload.get("audio_provider") or (safe_payload.get("complete_media_config") or {}).get("audio_provider") or "elevenlabs",
        "child_jobs": {},
        "polling_required": True,
    })

    _append_event(job_id, {"event": "universal_parent_job_accepted", "portal": portal})

    try:
        from backend.app.runtime.direct_media_provider_execution_runtime import start_universal_complete_media_workflow

        execution_payload = {
            **safe_payload,
            "job_id": job_id,
            "parent_job_id": job_id,
            "owner_approved": True if portal in {"admin", "owner_admin"} else bool(safe_payload.get("owner_approved") or safe_payload.get("owner_approval_granted")),
            "owner_approval_granted": True if portal in {"admin", "owner_admin"} else bool(safe_payload.get("owner_approved") or safe_payload.get("owner_approval_granted")),
            "universal_parent_job_orchestrated": True,
        }
        result = start_universal_complete_media_workflow(execution_payload)
        status = result.get("status") or "queued"
        parent = write_universal_parent_job(_merge_status(parent, {
            **result,
            "job_id": job_id,
            "status": status,
            "accepted": True,
        }))
        _append_event(job_id, {"event": "legacy_universal_workflow_started", "status": status})
    except Exception as error:
        parent = write_universal_parent_job({
            **parent,
            "success": False,
            "status": "universal_workflow_start_failed",
            "stage": "accepted",
            "error": str(error)[:1000],
            "polling_required": False,
            "failed_at": _now(),
        })
        _append_event(job_id, {"event": "universal_workflow_start_failed", "error": str(error)[:500]})

    return {
        **_public_record(parent, audience="admin" if portal in {"admin", "owner_admin"} else "client"),
        "universal_media_pipeline_orchestrated": True,
        "durable_parent_job": True,
    }


def get_universal_media_pipeline_status(job_id: str, *, audience: str = "client") -> Dict[str, Any]:
    safe_job_id = _safe_job_id(job_id)
    parent = _read_json(_job_path(safe_job_id))

    direct = _read_direct_status(safe_job_id)
    if parent:
        merged = _merge_status(parent, direct)
        write_universal_parent_job(merged)
        return {
            **_public_record(merged, audience=audience),
            "success": merged.get("success", True),
            "universal_media_pipeline_orchestrated": True,
            "durable_parent_job": True,
            "status_source": "universal_parent_store",
        }

    return {
        "success": False,
        "status": "durable_parent_job_missing",
        "job_id": safe_job_id,
        "message": "Universal complete media job status was not found in the durable parent store.",
        "polling_required": True,
        "universal_media_pipeline_orchestrated": True,
        "durable_parent_job": True,
        "customer_safe": True,
        "credential_values_exposed": False,
    }


def list_universal_media_pipeline_jobs(limit: int = 50, *, audience: str = "admin") -> Dict[str, Any]:
    rows = []
    for path in sorted(STORE.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)[: max(1, min(int(limit or 50), 200))]:
        row = _read_json(path)
        if row:
            rows.append(_public_record(row, audience=audience))

    return {
        "success": True,
        "status": "universal_media_pipeline_jobs_listed",
        "jobs": rows,
        "job_count": len(rows),
        "store": "runtime_outputs/universal_complete_media_jobs",
        "customer_safe": True,
        "credential_values_exposed": False,
    }
