from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict
import json
import os
import re
import uuid


ROOT = Path(__file__).resolve().parents[3]
DIRECT_JOB_DIR = ROOT / "runtime_outputs" / "direct_media_provider_jobs"
DIRECT_JOB_DIR.mkdir(parents=True, exist_ok=True)
DIRECT_PENDING_JOB_INDEX: Dict[str, Dict[str, Any]] = {}

SUPPORTED_VIDEO_PROVIDERS = {"runway", "kling"}
SUPPORTED_AUDIO_PROVIDERS = {"elevenlabs"}
SUPPORTED_PROVIDERS = SUPPORTED_VIDEO_PROVIDERS | SUPPORTED_AUDIO_PROVIDERS


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def _job_path(job_id: str) -> Path:
    safe = "".join(ch for ch in str(job_id or "") if ch.isalnum() or ch in {"_", "-"})
    return DIRECT_JOB_DIR / f"{safe}.json"


def _write_job(job: Dict[str, Any]) -> Dict[str, Any]:
    job_id = str(job.get("job_id") or _safe_id("direct_media_job"))
    job["job_id"] = job_id
    job["updated_at"] = _now()
    path = _job_path(job_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    DIRECT_PENDING_JOB_INDEX[job_id] = dict(job)

    temp_path = path.with_suffix(path.suffix + ".tmp")
    temp_path.write_text(json.dumps(job, indent=2, default=str), encoding="utf-8")
    temp_path.replace(path)

    return job


def _read_job(job_id: str) -> Dict[str, Any]:
    path = _job_path(job_id)
    if path.exists():
        try:
            job = json.loads(path.read_text(encoding="utf-8"))
            DIRECT_PENDING_JOB_INDEX[str(job_id)] = dict(job)
            return job
        except Exception as error:
            return {
                "success": False,
                "status": "read_failed",
                "job_id": job_id,
                "error": str(error)[:500],
                "customer_safe": True,
                "credential_values_exposed": False,
            }

    cached = DIRECT_PENDING_JOB_INDEX.get(str(job_id))
    if isinstance(cached, dict) and cached:
        return {
            **cached,
            "status": cached.get("status") or "queued",
            "success": bool(cached.get("success", True)),
            "customer_safe": True,
            "credential_values_exposed": False,
        }

    return {
        "success": False,
        "status": "not_found",
        "job_id": job_id,
        "customer_safe": True,
        "credential_values_exposed": False,
    }


def _env_present(names: list[str]) -> bool:
    return any(bool(os.getenv(name, "").strip()) for name in names)


def provider_readiness(provider: str) -> Dict[str, Any]:
    key = str(provider or "").strip().lower()

    if key == "runway":
        configured = _env_present(["RUNWAYML_API_SECRET", "RUNWAY_API_KEY"])
        return {
            "provider": "runway",
            "configured": configured,
            "supports": ["video"],
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    if key == "kling":
        configured = bool(os.getenv("KLING_API_KEY", "").strip()) and bool(os.getenv("KLING_SECRET_KEY", "").strip())
        return {
            "provider": "kling",
            "configured": configured,
            "supports": ["video"],
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    if key == "elevenlabs":
        configured = _env_present(["ELEVENLABS_API_KEY"])
        return {
            "provider": "elevenlabs",
            "configured": configured,
            "supports": ["audio"],
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    return {
        "provider": key or "unknown",
        "configured": False,
        "supports": [],
        "status": "unsupported_provider",
        "credential_values_exposed": False,
        "customer_safe": True,
    }





# DIRECT_MEDIA_SIGNED_PREVIEW_URL_V1
def _extract_signed_provider_url(provider_result: Dict[str, Any]) -> str:
    candidates = []

    for key in ["signed_preview_url", "provider_signed_url", "asset_signed_url", "output_url", "url"]:
        value = provider_result.get(key)
        if isinstance(value, str) and value.startswith("http"):
            candidates.append(value)

    output = provider_result.get("output")
    if isinstance(output, str):
        candidates.extend(re.findall(r"https?://[^\s'\"\]\)]+", output))

    if isinstance(output, list):
        for item in output:
            if isinstance(item, str) and item.startswith("http"):
                candidates.append(item)

    for url in candidates:
        if "_jwt=" in url or "token=" in url or "signature=" in url or "X-Amz-Signature=" in url:
            return url.strip()

    for url in candidates:
        if url.startswith("http"):
            return url.strip()

    return ""


def _normalise_provider_result(
    *,
    job: Dict[str, Any],
    provider_result: Dict[str, Any],
    media_type: str,
) -> Dict[str, Any]:
    success = bool(provider_result.get("success"))
    provider = str(job.get("provider") or provider_result.get("provider") or "").lower()
    status = str(provider_result.get("status") or ("completed" if success else "provider_failed"))

    signed_preview_url = _extract_signed_provider_url(provider_result)
    preview_url = (
        signed_preview_url
        or provider_result.get("preview_url")
        or provider_result.get("video_url_preview")
        or provider_result.get("audio_url_preview")
        or provider_result.get("asset_url")
        or ""
    )
    download_url = (
        provider_result.get("download_url")
        or provider_result.get("video_path")
        or provider_result.get("audio_path")
        or provider_result.get("asset_path")
        or ""
    )

    playable = bool(
        provider_result.get("video_saved")
        or provider_result.get("audio_saved")
        or provider_result.get("video_url_found")
        or preview_url
        or download_url
    )

    completed = {
        **job,
        "success": success,
        "status": "completed" if playable else "provider_failed",
        "provider_status": status,
        "provider_result_status": status,
        "provider_result": {
            key: value
            for key, value in dict(provider_result).items()
            if "key" not in key.lower() and "secret" not in key.lower() and "token" not in key.lower()
        },
        "media_type": media_type,
        "asset_type": media_type,
        "provider": provider,
        "playable": playable,
        "preview_ready": bool(preview_url),
        "download_ready": bool(download_url),
        "preview_url": preview_url,
        "signed_preview_url": signed_preview_url,
        "download_url": download_url,
        "asset_path": download_url,
        "provider_job_id": provider_result.get("task_id") or provider_result.get("job_id") or provider_result.get("provider_job_id") or "",
        "external_action_performed": bool(provider_result.get("external_action_performed")),
        "live_provider_call_triggered": bool(provider_result.get("live_provider_call_triggered")),
        "credential_values_exposed": False,
        "customer_safe": True,
        "completed_at": _now(),
    }

    return _write_job(completed)


def execute_direct_media_provider_job(payload: Dict[str, Any]) -> Dict[str, Any]:
    safe_payload = dict(payload or {})

    agent_id = str(
        safe_payload.get("agent_id")
        or safe_payload.get("assigned_agent")
        or safe_payload.get("requested_agent")
        or ""
    ).strip()

    provider = str(
        safe_payload.get("provider")
        or safe_payload.get("selected_provider")
        or safe_payload.get("selected_video_provider")
        or safe_payload.get("video_provider")
        or safe_payload.get("software")
        or ""
    ).strip().lower()

    media_type = str(safe_payload.get("media_type") or safe_payload.get("asset_type") or "").strip().lower()
    prompt = str(safe_payload.get("prompt") or safe_payload.get("task") or safe_payload.get("text") or "").strip()
    owner_approved = bool(safe_payload.get("owner_approved") or safe_payload.get("owner_approval_granted"))

    job_id = str(safe_payload.get("job_id") or _safe_id("direct_media_job"))

    base_job = {
        "success": False,
        "job_id": job_id,
        "status": "received",
        "agent_id": agent_id,
        "provider": provider,
        "media_type": media_type,
        "asset_type": media_type,
        "prompt_character_count": len(prompt),
        "owner_approved": owner_approved,
        "direct_media_provider_execution": True,
        "created_at": _now(),
        "updated_at": _now(),
        "customer_safe": True,
        "credential_values_exposed": False,
        "internal_config_exposed": False,
    }
    _write_job(base_job)

    if not owner_approved:
        return _write_job({
            **base_job,
            "status": "blocked_owner_approval_required",
            "reason": "Direct live provider execution requires owner approval.",
        })

    if not agent_id:
        return _write_job({
            **base_job,
            "status": "blocked_missing_agent_id",
            "reason": "agent_id is required.",
        })

    if provider not in SUPPORTED_PROVIDERS:
        return _write_job({
            **base_job,
            "status": "blocked_unsupported_provider",
            "reason": "Provider is not supported by the direct media execution lane.",
            "supported_providers": sorted(SUPPORTED_PROVIDERS),
        })

    if media_type == "video" and provider not in SUPPORTED_VIDEO_PROVIDERS:
        return _write_job({
            **base_job,
            "status": "blocked_provider_media_type_mismatch",
            "reason": f"{provider} is not enabled for video in this lane.",
        })

    if media_type == "audio" and provider not in SUPPORTED_AUDIO_PROVIDERS:
        return _write_job({
            **base_job,
            "status": "blocked_provider_media_type_mismatch",
            "reason": f"{provider} is not enabled for audio in this lane.",
        })

    if media_type not in {"video", "audio"}:
        return _write_job({
            **base_job,
            "status": "blocked_unsupported_media_type",
            "reason": "Only video and audio are enabled in the direct lane.",
        })

    if not prompt:
        return _write_job({
            **base_job,
            "status": "blocked_missing_prompt",
            "reason": "prompt is required.",
        })

    readiness = provider_readiness(provider)
    if not readiness.get("configured"):
        return _write_job({
            **base_job,
            "status": "blocked_provider_not_configured",
            "reason": f"{provider} credentials are not configured.",
            "provider_readiness": readiness,
        })

    running_job = _write_job({
        **base_job,
        "success": True,
        "status": "running",
        "provider_readiness": readiness,
        "external_action_performed": False,
        "live_provider_call_triggered": False,
    })

    try:
        if provider == "runway" and media_type == "video":
            from backend.app.runtime.runway_live_video_quality_adapter import run_runway_text_to_video_quality_test

            result = run_runway_text_to_video_quality_test(
                prompt_text=prompt,
                test_label=f"{job_id}_{agent_id}_runway_direct",
                allow_live_execution=True,
            )
            return _normalise_provider_result(job=running_job, provider_result=result, media_type="video")

        if provider == "kling" and media_type == "video":
            from backend.app.runtime.kling_live_video_quality_adapter import run_kling_text_to_video_quality_test

            result = run_kling_text_to_video_quality_test(
                prompt_text=prompt,
                test_label=f"{job_id}_{agent_id}_kling_direct",
                allow_live_execution=True,
                poll_for_completion=True,
            )
            return _normalise_provider_result(job=running_job, provider_result=result, media_type="video")

        if provider == "elevenlabs" and media_type == "audio":
            from backend.app.runtime.elevenlabs_live_tts_quality_adapter import run_elevenlabs_tts_quality_test

            result = run_elevenlabs_tts_quality_test(
                text=prompt,
                test_label=f"{job_id}_{agent_id}_elevenlabs_direct",
                allow_live_execution=True,
            )
            return _normalise_provider_result(job=running_job, provider_result=result, media_type="audio")

    except Exception as error:
        return _write_job({
            **running_job,
            "success": False,
            "status": "provider_execution_exception",
            "error": str(error)[:800],
            "external_action_performed": True,
            "live_provider_call_triggered": True,
            "credential_values_exposed": False,
            "customer_safe": True,
        })

    return _write_job({
        **running_job,
        "success": False,
        "status": "blocked_no_adapter_matched",
        "credential_values_exposed": False,
        "customer_safe": True,
    })


def get_direct_media_provider_job_status(job_id: str) -> Dict[str, Any]:
    job = _read_job(job_id)
    if not job.get("success") and job.get("status") == "not_found":
        return {
            **job,
            "polling_required": False,
            "message": "Direct media job was not found in the active runtime. Submit a new job if this remains after refresh.",
            "direct_media_provider_execution": True,
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    return {
        **job,
        "direct_media_provider_execution": True,
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def direct_media_provider_execution_status() -> Dict[str, Any]:
    return {
        "success": True,
        "direct_media_provider_execution_ready": True,
        "supported_video_providers": sorted(SUPPORTED_VIDEO_PROVIDERS),
        "supported_audio_providers": sorted(SUPPORTED_AUDIO_PROVIDERS),
        "runway": provider_readiness("runway"),
        "kling": provider_readiness("kling"),
        "elevenlabs": provider_readiness("elevenlabs"),
        "external_action_requires_owner_approval": True,
        "credential_values_exposed": False,
        "customer_safe": True,
    }



# ASYNC_DIRECT_MEDIA_PROVIDER_EXECUTION_V1
def start_direct_media_provider_job_async(payload: Dict[str, Any]) -> Dict[str, Any]:
    import threading

    safe_payload = dict(payload or {})
    job_id = str(safe_payload.get("job_id") or _safe_id("direct_media_job"))
    safe_payload["job_id"] = job_id

    agent_id = str(
        safe_payload.get("agent_id")
        or safe_payload.get("assigned_agent")
        or safe_payload.get("requested_agent")
        or ""
    ).strip()

    provider = str(
        safe_payload.get("provider")
        or safe_payload.get("selected_provider")
        or safe_payload.get("selected_video_provider")
        or safe_payload.get("video_provider")
        or safe_payload.get("software")
        or ""
    ).strip().lower()

    media_type = str(safe_payload.get("media_type") or safe_payload.get("asset_type") or "").strip().lower()
    prompt = str(safe_payload.get("prompt") or safe_payload.get("task") or safe_payload.get("text") or "").strip()
    owner_approved = bool(safe_payload.get("owner_approved") or safe_payload.get("owner_approval_granted"))

    queued_job = _write_job({
        "success": True,
        "job_id": job_id,
        "status": "queued",
        "agent_id": agent_id,
        "provider": provider,
        "media_type": media_type,
        "asset_type": media_type,
        "prompt_character_count": len(prompt),
        "owner_approved": owner_approved,
        "direct_media_provider_execution": True,
        "async_direct_media_provider_execution": True,
        "queued_at": _now(),
        "created_at": _now(),
        "customer_safe": True,
        "credential_values_exposed": False,
        "internal_config_exposed": False,
    })

    def _runner() -> None:
        try:
            _write_job({
                **queued_job,
                "status": "running",
                "started_at": _now(),
                "customer_safe": True,
                "credential_values_exposed": False,
            })
            execute_direct_media_provider_job(safe_payload)
        except Exception as error:
            _write_job({
                **queued_job,
                "success": False,
                "status": "async_execution_exception",
                "error": str(error)[:800],
                "failed_at": _now(),
                "customer_safe": True,
                "credential_values_exposed": False,
            })

    thread = threading.Thread(target=_runner, name=f"direct_media_provider_{job_id}", daemon=True)
    thread.start()

    return {
        **queued_job,
        "status": "queued",
        "accepted": True,
        "polling_required": True,
        "message": "Direct media provider job accepted. Poll job status for completion.",
        "customer_safe": True,
        "credential_values_exposed": False,
    }



# DIRECT_MEDIA_FULL_PROVIDER_STACK_VISIBILITY_V1
DIRECT_PROVIDER_STACK = [
    {
        "provider": "runway",
        "name": "Runway",
        "category": "video",
        "supports": ["video"],
        "env_names": ["RUNWAYML_API_SECRET", "RUNWAY_API_KEY"],
        "direct_execution_enabled": True,
        "disabled_reason": "",
    },
    {
        "provider": "kling",
        "name": "Kling",
        "category": "video",
        "supports": ["video"],
        "env_names": ["KLING_API_KEY", "KLING_SECRET_KEY"],
        "direct_execution_enabled": True,
        "disabled_reason": "",
    },
    {
        "provider": "heygen",
        "name": "HeyGen",
        "category": "avatar_video",
        "supports": ["video", "avatar_video"],
        "env_names": ["HEYGEN_API_KEY"],
        "direct_execution_enabled": False,
        "disabled_reason": "Direct adapter pending",
    },
    {
        "provider": "elevenlabs",
        "name": "ElevenLabs",
        "category": "audio",
        "supports": ["audio", "voiceover"],
        "env_names": ["ELEVENLABS_API_KEY"],
        "direct_execution_enabled": True,
        "disabled_reason": "",
    },
    {
        "provider": "replicate",
        "name": "Replicate",
        "category": "image_video",
        "supports": ["image", "video"],
        "env_names": ["REPLICATE_API_TOKEN"],
        "direct_execution_enabled": False,
        "disabled_reason": "Direct adapter pending",
    },
    {
        "provider": "openai",
        "name": "OpenAI",
        "category": "image_text",
        "supports": ["image", "text"],
        "env_names": ["OPENAI_API_KEY"],
        "direct_execution_enabled": False,
        "disabled_reason": "Direct media adapter pending",
    },
    {
        "provider": "sync",
        "name": "Sync / lip-sync",
        "category": "lip_sync",
        "supports": ["lip_sync", "video"],
        "env_names": ["SYNC_API_KEY", "SYNC_LABS_API_KEY"],
        "direct_execution_enabled": False,
        "disabled_reason": "Direct adapter pending",
    },
]


def _provider_stack_item(provider_config: Dict[str, Any]) -> Dict[str, Any]:
    env_names = list(provider_config.get("env_names") or [])
    configured = _env_present(env_names)

    return {
        "provider": provider_config.get("provider"),
        "name": provider_config.get("name"),
        "category": provider_config.get("category"),
        "supports": list(provider_config.get("supports") or []),
        "configured": configured,
        "direct_execution_enabled": bool(provider_config.get("direct_execution_enabled")),
        "disabled_reason": "" if bool(provider_config.get("direct_execution_enabled")) else str(provider_config.get("disabled_reason") or "Adapter pending"),
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def full_direct_media_provider_stack() -> list[Dict[str, Any]]:
    return [_provider_stack_item(item) for item in DIRECT_PROVIDER_STACK]


def provider_readiness(provider: str) -> Dict[str, Any]:
    key = str(provider or "").strip().lower()
    for item in DIRECT_PROVIDER_STACK:
        if item.get("provider") == key:
            return _provider_stack_item(item)

    return {
        "provider": key or "unknown",
        "name": key or "Unknown provider",
        "configured": False,
        "direct_execution_enabled": False,
        "disabled_reason": "Unsupported provider",
        "supports": [],
        "status": "unsupported_provider",
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def direct_media_provider_execution_status() -> Dict[str, Any]:
    provider_stack = full_direct_media_provider_stack()
    provider_map = {item["provider"]: item for item in provider_stack}

    return {
        "success": True,
        "direct_media_provider_execution_ready": True,
        "provider_stack": provider_stack,
        "provider_count": len(provider_stack),
        "configured_provider_count": sum(1 for item in provider_stack if item.get("configured")),
        "direct_execution_provider_count": sum(1 for item in provider_stack if item.get("direct_execution_enabled")),
        "supported_video_providers": sorted(SUPPORTED_VIDEO_PROVIDERS),
        "supported_audio_providers": sorted(SUPPORTED_AUDIO_PROVIDERS),
        "runway": provider_map.get("runway", provider_readiness("runway")),
        "kling": provider_map.get("kling", provider_readiness("kling")),
        "heygen": provider_map.get("heygen", provider_readiness("heygen")),
        "elevenlabs": provider_map.get("elevenlabs", provider_readiness("elevenlabs")),
        "replicate": provider_map.get("replicate", provider_readiness("replicate")),
        "openai": provider_map.get("openai", provider_readiness("openai")),
        "sync": provider_map.get("sync", provider_readiness("sync")),
        "external_action_requires_owner_approval": True,
        "credential_values_exposed": False,
        "customer_safe": True,
    }
