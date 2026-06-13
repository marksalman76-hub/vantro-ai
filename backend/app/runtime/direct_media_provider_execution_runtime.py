from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict
import hashlib
import json
import os
import re
import uuid
import subprocess
import shutil
import threading


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


def runway_safe_key_diagnostics() -> Dict[str, Any]:
    candidate_names = [
        "RUNWAYML_API_SECRET",
        "RUNWAY_API_KEY",
        "RUNWAYML_API_KEY",
        "RUNWAY_TOKEN",
        "RUNWAYML_TOKEN",
        "RUNWAY_API_TOKEN",
    ]

    used_env_name = ""
    keys = []
    for name in candidate_names:
        value = str(os.getenv(name) or "").strip()
        if value and not used_env_name:
            used_env_name = name

        item: Dict[str, Any] = {
            "env_name": name,
            "present": bool(value),
            "length": len(value) if value else 0,
        }
        if value:
            item["sha256_prefix"] = hashlib.sha256(value.encode("utf-8")).hexdigest()[:12]
        keys.append(item)

    return {
        "success": True,
        "status": "runway_key_metadata_only",
        "provider": "runway",
        "candidate_env_names": candidate_names,
        "used_env_name": used_env_name,
        "configured": bool(used_env_name),
        "keys": keys,
        "note": "No credential values are exposed. Use env_name, length, and sha256_prefix to compare the backend key with the intended Runway API key.",
        "customer_safe": True,
        "credential_values_exposed": False,
        "internal_config_exposed": False,
    }


def provider_readiness(provider: str) -> Dict[str, Any]:
    key = str(provider or "").strip().lower()

    if key == "runway":
        configured = _env_present(["RUNWAYML_API_SECRET", "RUNWAY_API_KEY", "RUNWAYML_API_KEY"])
        return {
            "provider": "runway",
            "configured": configured,
            "env_names": ["RUNWAYML_API_SECRET", "RUNWAY_API_KEY", "RUNWAYML_API_KEY"],
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
        "env_names": ["RUNWAYML_API_SECRET", "RUNWAY_API_KEY", "RUNWAYML_API_KEY"],
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
        "admin_provider_diagnostics": {
            "runway": runway_safe_key_diagnostics(),
        },
        "external_action_requires_owner_approval": True,
        "credential_values_exposed": False,
        "customer_safe": True,
    }



# DIRECT_MEDIA_COMPOSITION_RUNTIME_V1
def _safe_runtime_asset_path(value: str) -> Path | None:
    if not value:
        return None

    try:
        asset_path = Path(str(value)).resolve()
        allowed_root = Path("/opt/render/project/src/runtime_outputs").resolve()
        asset_path.relative_to(allowed_root)
        if asset_path.exists() and asset_path.is_file():
            return asset_path
    except Exception:
        return None

    return None


def _first_existing_asset_path(job: Dict[str, Any], media_type: str) -> Path | None:
    provider_result = job.get("provider_result") if isinstance(job.get("provider_result"), dict) else {}

    candidates = [
        job.get("asset_path"),
        job.get("download_url"),
        provider_result.get("audio_path"),
        provider_result.get("video_path"),
    ]

    if media_type == "video":
        candidates = [
            provider_result.get("video_path"),
            job.get("asset_path"),
            job.get("download_url"),
        ]

    if media_type == "audio":
        candidates = [
            provider_result.get("audio_path"),
            job.get("asset_path"),
            job.get("download_url"),
        ]

    for value in candidates:
        path = _safe_runtime_asset_path(str(value or ""))
        if path:
            return path

    return None


def compose_direct_media_video_audio(payload: Dict[str, Any]) -> Dict[str, Any]:
    safe_payload = dict(payload or {})
    video_job_id = str(safe_payload.get("video_job_id") or safe_payload.get("videoJobId") or "").strip()
    audio_job_id = str(safe_payload.get("audio_job_id") or safe_payload.get("audioJobId") or "").strip()
    owner_approved = bool(safe_payload.get("owner_approved") or safe_payload.get("owner_approval_granted"))

    composition_job_id = str(safe_payload.get("composition_job_id") or _safe_id("direct_media_composition"))

    base = {
        "success": False,
        "job_id": composition_job_id,
        "composition_job_id": composition_job_id,
        "video_job_id": video_job_id,
        "audio_job_id": audio_job_id,
        "provider": "internal_composer",
        "media_type": "video",
        "asset_type": "video",
        "direct_media_composition": True,
        "owner_approved": owner_approved,
        "created_at": _now(),
        "customer_safe": True,
        "credential_values_exposed": False,
        "internal_config_exposed": False,
    }

    _write_job({**base, "status": "received"})

    if not owner_approved:
        return _write_job({
            **base,
            "status": "blocked_owner_approval_required",
            "reason": "Direct media composition requires owner approval.",
        })

    if not video_job_id or not audio_job_id:
        return _write_job({
            **base,
            "status": "blocked_missing_source_jobs",
            "reason": "video_job_id and audio_job_id are required.",
        })

    video_job = get_direct_media_provider_job_status(video_job_id)
    audio_job = get_direct_media_provider_job_status(audio_job_id)

    if video_job.get("status") != "completed" or not video_job.get("playable"):
        return _write_job({
            **base,
            "status": "blocked_video_not_ready",
            "reason": "Video source job must be completed and playable.",
            "video_status": video_job.get("status"),
            "video_playable": bool(video_job.get("playable")),
        })

    if audio_job.get("status") != "completed" or not audio_job.get("playable"):
        return _write_job({
            **base,
            "status": "blocked_audio_not_ready",
            "reason": "Audio source job must be completed and playable.",
            "audio_status": audio_job.get("status"),
            "audio_playable": bool(audio_job.get("playable")),
        })

    video_path = _first_existing_asset_path(video_job, "video")
    audio_path = _first_existing_asset_path(audio_job, "audio")

    if not video_path:
        return _write_job({
            **base,
            "status": "blocked_video_asset_missing",
            "reason": "Video source file is missing from runtime asset storage.",
        })

    if not audio_path:
        return _write_job({
            **base,
            "status": "blocked_audio_asset_missing",
            "reason": "Audio source file is missing from runtime asset storage.",
        })

    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        return _write_job({
            **base,
            "status": "blocked_ffmpeg_missing",
            "reason": "ffmpeg is not available in the runtime environment.",
            "video_asset_path": str(video_path),
            "audio_asset_path": str(audio_path),
        })

    out_dir = DIRECT_JOB_DIR / "composed_assets"
    out_dir.mkdir(parents=True, exist_ok=True)
    output_path = out_dir / f"{composition_job_id}.mp4"

    command = [
        ffmpeg,
        "-y",
        "-i",
        str(video_path),
        "-i",
        str(audio_path),
        "-map",
        "0:v:0",
        "-map",
        "1:a:0",
        "-c:v",
        "copy",
        "-c:a",
        "aac",
        "-shortest",
        str(output_path),
    ]

    running = _write_job({
        **base,
        "status": "running",
        "video_asset_path": str(video_path),
        "audio_asset_path": str(audio_path),
        "output_path": str(output_path),
        "started_at": _now(),
    })

    try:
        completed = subprocess.run(command, capture_output=True, text=True, timeout=180)

        if completed.returncode != 0:
            return _write_job({
                **running,
                "success": False,
                "status": "composition_failed",
                "error": (completed.stderr or completed.stdout or "ffmpeg failed")[-1200:],
                "customer_safe": True,
                "credential_values_exposed": False,
            })

        if not output_path.exists() or output_path.stat().st_size <= 0:
            return _write_job({
                **running,
                "success": False,
                "status": "composition_output_missing",
                "error": "ffmpeg completed but output file was not created.",
                "customer_safe": True,
                "credential_values_exposed": False,
            })

        return _write_job({
            **running,
            "success": True,
            "status": "completed",
            "provider_status": "video_audio_composed",
            "provider_result_status": "video_audio_composed",
            "playable": True,
            "preview_ready": True,
            "download_ready": True,
            "asset_path": str(output_path),
            "download_url": str(output_path),
            "preview_url": f"/api/admin-direct-media-provider-asset?job_id={composition_job_id}",
            "signed_preview_url": f"/api/admin-direct-media-provider-asset?job_id={composition_job_id}",
            "video_job_id": video_job_id,
            "audio_job_id": audio_job_id,
            "video_size_bytes": output_path.stat().st_size,
            "completed_at": _now(),
            "customer_safe": True,
            "credential_values_exposed": False,
        })

    except Exception as error:
        return _write_job({
            **running,
            "success": False,
            "status": "composition_exception",
            "error": str(error)[:1200],
            "customer_safe": True,
            "credential_values_exposed": False,
        })


def direct_media_composition_status() -> Dict[str, Any]:
    return {
        "success": True,
        "direct_media_composition_ready": bool(shutil.which("ffmpeg")),
        "ffmpeg_available": bool(shutil.which("ffmpeg")),
        "supported_composition": ["video_plus_audio_to_mp4"],
        "credential_values_exposed": False,
        "customer_safe": True,
    }


CLIENT_PREFLIGHT_MESSAGE = "Media generation is not ready to run yet. Please contact support or choose a shorter smoke test."


# UNIVERSAL_COMPLETE_MEDIA_WORKFLOW_V1
def _ucm_text(value: Any, default: str = "") -> str:
    return str(value or default).strip()


def _ucm_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "on", "approved"}
    return bool(value)


def _ucm_duration_float(value: Any, default: float = 5.0) -> float:
    try:
        return max(1.0, min(float(str(value or default).replace("s", "").strip()), 120.0))
    except Exception:
        return default


def _ucm_controls(payload: Dict[str, Any]) -> Dict[str, Any]:
    safe = dict(payload or {})

    controls = {
        "prompt": _ucm_text(safe.get("prompt") or safe.get("task") or safe.get("media_brief")),
        "agent_id": _ucm_text(
            safe.get("agent_id")
            or safe.get("assigned_agent")
            or safe.get("requested_agent")
            or "social_media_manager_content_creator_agent"
        ),
        "output_type": _ucm_text(safe.get("output_type") or safe.get("media_output_type") or "complete_video"),
        "industry": _ucm_text(safe.get("industry") or safe.get("niche")),
        "target_audience": _ucm_text(safe.get("target_audience")),
        "platform": _ucm_text(safe.get("platform") or "general"),
        "duration_seconds": _ucm_text(safe.get("duration_seconds") or safe.get("duration") or "5"),
        "aspect_ratio": _ucm_text(safe.get("aspect_ratio") or "9:16"),
        "language": _ucm_text(safe.get("language") or "English"),
        "accent": _ucm_text(safe.get("accent")),
        "tone": _ucm_text(safe.get("tone") or "natural, polished, human"),
        "voice_style": _ucm_text(safe.get("voice_style") or "natural conversational voice"),
        "age_range": _ucm_text(safe.get("age_range")),
        "gender_presentation": _ucm_text(safe.get("gender_presentation")),
        "ethnicity_or_cultural_appearance": _ucm_text(
            safe.get("ethnicity_or_cultural_appearance")
            or safe.get("ethnicity")
            or safe.get("cultural_appearance")
        ),
        "avatar_likeness": _ucm_text(safe.get("avatar_likeness") or safe.get("ultra_human_likeness")),
        "face_shape": _ucm_text(safe.get("face_shape")),
        "skin_tone": _ucm_text(safe.get("skin_tone")),
        "facial_features": _ucm_text(safe.get("facial_features")),
        "hair_style": _ucm_text(safe.get("hair_style")),
        "hair_colour": _ucm_text(safe.get("hair_colour") or safe.get("hair_color")),
        "eye_colour": _ucm_text(safe.get("eye_colour") or safe.get("eye_color")),
        "wardrobe": _ucm_text(safe.get("wardrobe") or safe.get("styling")),
        "expressions": _ucm_text(safe.get("expressions") or safe.get("facial_expressions")),
        "emotion": _ucm_text(safe.get("emotion")),
        "eye_contact": _ucm_text(safe.get("eye_contact")),
        "gestures": _ucm_text(safe.get("gestures") or safe.get("hand_gestures")),
        "body_language": _ucm_text(safe.get("body_language")),
        "lip_sync_accuracy": _ucm_text(safe.get("lip_sync_accuracy") or "high when avatar or talking-head output is requested"),
        "speaking_pace": _ucm_text(safe.get("speaking_pace") or "natural, not rushed"),
        "camera_framing": _ucm_text(safe.get("camera_framing")),
        "lighting_style": _ucm_text(safe.get("lighting_style")),
        "background_setting": _ucm_text(safe.get("background_setting") or safe.get("setting")),
        "brand_style": _ucm_text(safe.get("brand_style")),
        "product_or_service_details": _ucm_text(safe.get("product_or_service_details")),
        "offer": _ucm_text(safe.get("offer") or safe.get("promotion")),
        "call_to_action": _ucm_text(safe.get("call_to_action") or safe.get("cta")),
        "captions": _ucm_text(safe.get("captions") or safe.get("subtitles")),
        "music_style": _ucm_text(safe.get("music_style")),
        "sound_effects": _ucm_text(safe.get("sound_effects") or safe.get("sfx")),
        "pacing": _ucm_text(safe.get("pacing") or "smooth, clear, premium"),
        "visual_style": _ucm_text(safe.get("visual_style")),
        "camera_movement": _ucm_text(safe.get("camera_movement")),
        "compliance_notes": _ucm_text(safe.get("compliance_notes")),
        "number_of_variations": _ucm_text(safe.get("number_of_variations") or "1"),
        "final_delivery_format": _ucm_text(safe.get("final_delivery_format") or "mp4"),
        "video_provider": _ucm_text(safe.get("video_provider") or safe.get("provider") or "runway").lower(),
        "audio_provider": _ucm_text(safe.get("audio_provider") or "elevenlabs").lower(),
    }

    return controls


def _ucm_live_adapter_credentials_present(provider: str) -> bool:
    key = str(provider or "").strip().lower()
    if key == "runway":
        return bool(runway_safe_key_diagnostics().get("used_env_name"))
    if key == "kling":
        return bool(os.getenv("KLING_API_KEY", "").strip()) and bool(os.getenv("KLING_SECRET_KEY", "").strip())
    if key == "elevenlabs":
        return bool(os.getenv("ELEVENLABS_API_KEY", "").strip())
    return False


def _ucm_provider_executable(provider: str, media_type: str) -> Dict[str, Any]:
    key = str(provider or "").strip().lower()
    readiness = provider_readiness(key)
    supports = list(readiness.get("supports") or [])
    direct_enabled = bool(readiness.get("direct_execution_enabled", key in SUPPORTED_PROVIDERS))
    supported_for_media = media_type in supports or (media_type == "voiceover" and "audio" in supports)
    live_credentials_present = _ucm_live_adapter_credentials_present(key)
    executable = bool(direct_enabled and supported_for_media and live_credentials_present)

    reasons = []
    if not direct_enabled:
        reasons.append(readiness.get("disabled_reason") or "Direct live adapter is not enabled.")
    if not supported_for_media:
        reasons.append(f"Provider is not enabled for {media_type}.")
    if not live_credentials_present:
        reasons.append("Required live adapter credentials are missing.")

    return {
        "provider": key or "unknown",
        "media_type": media_type,
        "configured": bool(readiness.get("configured")),
        "direct_execution_enabled": direct_enabled,
        "supports": supports,
        "live_adapter_credentials_present": live_credentials_present,
        "executable": executable,
        "blocked_reason": " ".join(str(reason) for reason in reasons if reason).strip(),
        "customer_safe": True,
        "credential_values_exposed": False,
    }


def _ucm_estimated_credit_risk(duration_seconds: float, executable_visual_count: int, *, smoke_test_mode: bool = False) -> Dict[str, Any]:
    if smoke_test_mode:
        level = "low"
    elif duration_seconds <= 5:
        level = "low"
    elif duration_seconds <= 15:
        level = "medium"
    else:
        level = "high"

    return {
        "risk_level": level,
        "duration_seconds": duration_seconds,
        "paid_visual_provider_attempts_possible": executable_visual_count,
        "paid_audio_provider_attempts_possible": 1,
        "acceptable_without_confirmation": level in {"low", "medium"},
        "customer_safe": True,
        "credential_values_exposed": False,
    }


def _ucm_preflight_universal_media_job(payload: Dict[str, Any], plan: Dict[str, Any]) -> Dict[str, Any]:
    safe_payload = dict(payload or {})
    controls = _ucm_controls(safe_payload)
    smoke_test_mode = _ucm_bool(
        safe_payload.get("smoke_test_mode")
        or safe_payload.get("run_smoke_test")
        or safe_payload.get("five_second_smoke_test")
    )
    dry_run_mode = _ucm_bool(
        safe_payload.get("dry_run")
        or safe_payload.get("preflight_only")
        or safe_payload.get("check_readiness")
        or safe_payload.get("universal_media_dry_run")
    )
    credit_risk_acknowledged = _ucm_bool(
        safe_payload.get("credit_risk_acknowledged")
        or safe_payload.get("cost_safety_confirmed")
        or safe_payload.get("paid_provider_risk_confirmed")
    )

    requested_duration = _ucm_duration_float(controls.get("duration_seconds"), 5.0)
    estimated_duration = min(requested_duration, 5.0) if smoke_test_mode else requested_duration

    visual_provider_order = _ucm_video_provider_order(controls.get("video_provider"))
    visual_readiness = [_ucm_provider_executable(provider, "video") for provider in visual_provider_order]
    executable_visual = [item for item in visual_readiness if item.get("executable")]
    non_executable_visual = [item for item in visual_readiness if not item.get("executable")]

    audio_provider = str(controls.get("audio_provider") or "elevenlabs").strip().lower()
    audio_readiness = [_ucm_provider_executable(audio_provider, "audio")]
    executable_audio = [item for item in audio_readiness if item.get("executable")]

    composition_available = bool(shutil.which("ffmpeg"))
    estimated_credit_risk = _ucm_estimated_credit_risk(
        estimated_duration,
        len(executable_visual),
        smoke_test_mode=smoke_test_mode,
    )

    failed_checks: list[Dict[str, Any]] = []
    blocked_provider_calls: list[Dict[str, Any]] = [
        {
            "provider": item.get("provider"),
            "media_type": "video",
            "reason": item.get("blocked_reason") or "Visual provider is not executable.",
        }
        for item in non_executable_visual
    ] + [
        {
            "provider": item.get("provider"),
            "media_type": "audio",
            "reason": item.get("blocked_reason") or "Audio provider is not executable.",
        }
        for item in audio_readiness
        if not item.get("executable")
    ]

    if not controls.get("prompt"):
        failed_checks.append({"check": "prompt", "status": "failed", "reason": "A media prompt is required."})

    if smoke_test_mode and requested_duration > 5:
        failed_checks.append({
            "check": "smoke_test_duration",
            "status": "failed",
            "reason": "Smoke test mode is limited to 5 seconds.",
        })

    if not executable_visual:
        failed_checks.append({
            "check": "visual_provider_readiness",
            "status": "failed",
            "reason": "No executable visual provider is available.",
        })

    if not executable_audio:
        failed_checks.append({
            "check": "audio_provider_readiness",
            "status": "failed",
            "reason": "No executable audio provider is available.",
        })

    if not composition_available:
        failed_checks.append({
            "check": "composition_path",
            "status": "failed",
            "reason": "ffmpeg composition path is not available.",
        })

    if estimated_credit_risk.get("risk_level") == "high" and not credit_risk_acknowledged:
        failed_checks.append({
            "check": "estimated_credit_risk",
            "status": "failed",
            "reason": "Estimated provider credit risk is high and requires explicit confirmation.",
        })

    if smoke_test_mode and not executable_visual:
        failed_checks.append({
            "check": "smoke_test_visual_provider",
            "status": "failed",
            "reason": "Smoke test mode requires at least one executable visual provider.",
        })

    blocked = bool(failed_checks)
    return {
        "success": not blocked,
        "status": "universal_complete_media_preflight_blocked" if blocked else "universal_complete_media_preflight_ready",
        "dry_run": dry_run_mode,
        "smoke_test_mode": smoke_test_mode,
        "smoke_test_label": "5s smoke test" if smoke_test_mode else "",
        "failed_preflight_checks": failed_checks,
        "blocked_provider_calls": blocked_provider_calls,
        "estimated_duration_seconds": estimated_duration,
        "requested_duration_seconds": requested_duration,
        "estimated_credit_risk": estimated_credit_risk,
        "executable_visual_providers": executable_visual,
        "non_executable_visual_providers": non_executable_visual,
        "executable_audio_providers": executable_audio,
        "composition_path_available": composition_available,
        "composition_tool": "ffmpeg" if composition_available else "",
        "selected_visual_provider_order": [item.get("provider") for item in executable_visual],
        "selected_audio_provider": executable_audio[0].get("provider") if executable_audio else "",
        "estimated_stages": [
            "preflight",
            "visual_generation",
            "audio_generation",
            "captions_timing_metadata",
            "composition_stitching",
            "final_asset_delivery",
        ],
        "timed_plan": plan.get("timed_plan"),
        "quality_requirements": plan.get("quality_requirements"),
        "message": CLIENT_PREFLIGHT_MESSAGE if blocked else "Media generation preflight passed.",
        "customer_safe": True,
        "credential_values_exposed": False,
        "internal_config_exposed": False,
    }


def _ucm_brief_lines(controls: Dict[str, Any]) -> str:
    ordered_keys = [
        "output_type",
        "industry",
        "target_audience",
        "platform",
        "duration_seconds",
        "aspect_ratio",
        "language",
        "accent",
        "tone",
        "voice_style",
        "age_range",
        "gender_presentation",
        "ethnicity_or_cultural_appearance",
        "avatar_likeness",
        "face_shape",
        "skin_tone",
        "facial_features",
        "hair_style",
        "hair_colour",
        "eye_colour",
        "wardrobe",
        "expressions",
        "emotion",
        "eye_contact",
        "gestures",
        "body_language",
        "lip_sync_accuracy",
        "speaking_pace",
        "camera_framing",
        "lighting_style",
        "background_setting",
        "brand_style",
        "product_or_service_details",
        "offer",
        "call_to_action",
        "captions",
        "music_style",
        "sound_effects",
        "pacing",
        "visual_style",
        "camera_movement",
        "compliance_notes",
        "final_delivery_format",
    ]

    lines = []
    for key in ordered_keys:
        value = _ucm_text(controls.get(key))
        if value:
            lines.append(f"{key}: {value}")
    return "\n".join(lines)


def build_universal_complete_media_plan(payload: Dict[str, Any]) -> Dict[str, Any]:
    controls = _ucm_controls(payload)
    prompt = controls["prompt"]
    duration_raw = controls["duration_seconds"]

    try:
        duration = max(3.0, min(float(str(duration_raw).replace("s", "").strip()), 60.0))
    except Exception:
        duration = 5.0

    third = round(duration / 3, 2)
    two_thirds = round(duration * 2 / 3, 2)

    voice_word_limit = max(5, min(int(duration * 2.2), 120))

    visual_prompt = (
        "Create a premium, realistic, globally adaptable media visual based on this brief. "
        "Do not include visible text unless captions or text are explicitly requested. "
        "Keep visuals coherent with the timed plan. "
        "Use any provided age range, gender presentation, ethnicity/cultural appearance, avatar likeness, "
        "facial features, expressions, wardrobe, setting, lighting, camera movement, and brand style strictly as "
        "user-provided creative direction. Do not infer real identity. "
        f"Duration target: {duration} seconds. Aspect ratio: {controls['aspect_ratio']}. "
        f"Original prompt: {prompt}\n\nCreative controls:\n{_ucm_brief_lines(controls)}\n\n"
        f"Timed plan:\n"
        f"0.00s-{third:.2f}s: clear opening visual that establishes the concept.\n"
        f"{third:.2f}s-{two_thirds:.2f}s: main action, presenter/avatar/scene detail, or key visual benefit.\n"
        f"{two_thirds:.2f}s-{duration:.2f}s: clean finish with natural endpoint and optional call-to-action if provided."
    )

    voice_prompt = (
        f"Write and perform a natural {controls['language']} voiceover for a {duration:.1f} second media file. "
        f"Use a {controls['tone']} tone and {controls['voice_style']} style. "
        "The voiceover must sound human, smooth, non-robotic, not choppy, and not rushed. "
        f"Maximum {voice_word_limit} words. "
        "Match the visual timing and avoid long pauses unless the prompt requires it. "
        "If a call-to-action is provided, include it naturally at the end. "
        "Do not read internal labels or field names. "
        f"Original prompt: {prompt}\n\nCreative controls:\n{_ucm_brief_lines(controls)}"
    )

    return {
        "success": True,
        "controls": controls,
        "duration_seconds": duration,
        "voice_word_limit": voice_word_limit,
        "timed_plan": [
            {"start": 0.0, "end": third, "purpose": "opening visual"},
            {"start": third, "end": two_thirds, "purpose": "main visual/audio message"},
            {"start": two_thirds, "end": duration, "purpose": "final beat or call-to-action"},
        ],
        "visual_prompt": visual_prompt,
        "voice_prompt": voice_prompt,
        "quality_requirements": {
            "universal_not_ecommerce_only": True,
            "complete_media_file_from_one_prompt": True,
            "natural_non_robotic_audio": True,
            "audio_video_synchronisation_required": True,
            "avoid_choppy_audio": True,
            "avatar_likeness_controls_supported": True,
            "facial_feature_controls_supported": True,
            "expression_controls_supported": True,
            "language_controls_supported": True,
            "optional_demographic_creative_direction_only": True,
            "do_not_infer_sensitive_attributes": True,
            "customer_safe": True,
            "credential_values_exposed": False,
        },
    }




def _ucm_provider_safe_voice_prompt(prompt: str, duration_seconds: int | float = 5) -> str:
    """
    Keep voiceover close to the target clip duration.
    Approximate spoken English at 2.2 words/sec for clear promo narration.
    """
    clean = " ".join(str(prompt or "").split()).strip()
    duration = max(3.0, float(duration_seconds or 5))
    max_words = max(8, int(duration * 2.2))

    # Prefer quoted voiceover line if present.
    quoted = re.findall(r"[“\"]([^”\"]{8,260})[”\"]", clean)
    if quoted:
        clean = " ".join(quoted).strip()

    words = clean.split()
    if len(words) > max_words:
        clean = " ".join(words[:max_words]).strip()

    return clean


def _ucm_provider_safe_visual_prompt(prompt: str, max_chars: int = 950) -> str:
    """
    Runway promptText currently rejects prompts over 1000 characters.
    Keep universal complete media planning rich internally, but send providers a concise visual prompt.
    This is intentionally broad-media safe and not ecommerce-only.
    """
    clean = " ".join(str(prompt or "").split()).strip()

    if len(clean) <= max_chars:
        return clean

    # Prefer complete sentence boundaries so the provider receives a coherent prompt.
    sentences = re.split(r"(?<=[.!?])\s+", clean)
    selected = []

    for sentence in sentences:
        candidate = " ".join(selected + [sentence]).strip()
        if len(candidate) <= max_chars:
            selected.append(sentence)
        else:
            break

    compressed = " ".join(selected).strip()

    if not compressed:
        compressed = clean[:max_chars].rsplit(" ", 1)[0].strip()

    continuity = (
        " Maintain consistent subjects, hands, props, screens, reflections, lighting, "
        "camera motion, and scene physics. Avoid disappearing objects, warped hands, "
        "mismatched movement, impossible reflections, and sudden scene changes."
    )

    room = max_chars - len(compressed)
    if room > 80 and "Avoid disappearing objects" not in compressed:
        compressed = (compressed + continuity[:room]).strip()

    return compressed[:max_chars].strip()


def _ucm_get_duration_seconds(path_value: str) -> float | None:
    try:
        ffprobe = shutil.which("ffprobe")
        if not ffprobe:
            return None
        path = str(path_value or "").strip()
        if not path:
            return None
        completed = subprocess.run(
            [
                ffprobe,
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                path,
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if completed.returncode != 0:
            return None
        return float((completed.stdout or "").strip())
    except Exception:
        return None


def _ucm_compose_with_sync(video_job: Dict[str, Any], audio_job: Dict[str, Any], composition_job_id: str) -> Dict[str, Any]:
    video_path = _first_existing_asset_path(video_job, "video")
    audio_path = _first_existing_asset_path(audio_job, "audio")

    base = {
        "success": False,
        "job_id": composition_job_id,
        "composition_job_id": composition_job_id,
        "video_job_id": video_job.get("job_id"),
        "audio_job_id": audio_job.get("job_id"),
        "provider": "universal_complete_media_composer",
        "media_type": "complete_video",
        "asset_type": "video",
        "customer_safe": True,
        "credential_values_exposed": False,
        "internal_config_exposed": False,
        "created_at": _now(),
    }

    if not video_path:
        return _write_job({**base, "status": "blocked_video_asset_missing"})
    if not audio_path:
        return _write_job({**base, "status": "blocked_audio_asset_missing"})

    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        return _write_job({
            **base,
            "status": "blocked_ffmpeg_missing",
            "reason": "ffmpeg is not available in the runtime environment.",
        })

    out_dir = DIRECT_JOB_DIR / "universal_complete_media_assets"
    out_dir.mkdir(parents=True, exist_ok=True)
    output_path = out_dir / f"{composition_job_id}.mp4"

    video_duration = _ucm_get_duration_seconds(str(video_path))
    audio_duration = _ucm_get_duration_seconds(str(audio_path))

    command = [
        ffmpeg,
        "-y",
        "-i",
        str(video_path),
        "-i",
        str(audio_path),
        "-map",
        "0:v:0",
        "-map",
        "1:a:0",
        "-c:v",
        "copy",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-ac",
        "2",
        "-ar",
        "44100",
        "-shortest",
        "-movflags",
        "+faststart",
        str(output_path),
    ]

    running = _write_job({
        **base,
        "status": "running_synchronised_composition",
        "video_asset_path": str(video_path),
        "audio_asset_path": str(audio_path),
        "video_duration_seconds": video_duration,
        "audio_duration_seconds": audio_duration,
        "output_path": str(output_path),
        "sync_strategy": "safe_stereo_44100hz_aac_shortest_faststart",
        "started_at": _now(),
    })

    try:
        completed = subprocess.run(command, capture_output=True, text=True, timeout=240)
        if completed.returncode != 0:
            return _write_job({
                **running,
                "success": False,
                "status": "synchronised_composition_failed",
                "error": (completed.stderr or completed.stdout or "ffmpeg failed")[-1200:],
            })

        if not output_path.exists() or output_path.stat().st_size <= 0:
            return _write_job({
                **running,
                "success": False,
                "status": "synchronised_composition_output_missing",
                "error": "ffmpeg completed but output file was not created.",
            })

        final_duration = _ucm_get_duration_seconds(str(output_path))

        return _write_job({
            **running,
            "success": True,
            "status": "completed",
            "provider_status": "universal_complete_media_ready",
            "provider_result_status": "universal_complete_media_ready",
            "playable": True,
            "preview_ready": True,
            "download_ready": True,
            "asset_path": str(output_path),
            "download_url": str(output_path),
            "preview_url": f"/api/admin-direct-media-provider-asset?job_id={composition_job_id}",
            "signed_preview_url": f"/api/admin-direct-media-provider-asset?job_id={composition_job_id}",
            "final_media_type": "synchronised_video_with_audio",
            "final_duration_seconds": final_duration,
            "video_size_bytes": output_path.stat().st_size,
            "completed_at": _now(),
            "quality_requirements": {
                "natural_non_robotic_audio": True,
                "avoid_choppy_audio": True,
                "audio_video_synchronisation_required": True,
                "customer_safe": True,
                "credential_values_exposed": False,
            },
        })

    except Exception as error:
        return _write_job({
            **running,
            "success": False,
            "status": "synchronised_composition_exception",
            "error": str(error)[:1200],
        })


def _ucm_provider_failure_summary(result: Dict[str, Any]) -> str:
    raw = str(
        result.get("error")
        or result.get("reason")
        or result.get("message")
        or result.get("provider_status")
        or result.get("status")
        or "provider_attempt_failed"
    )
    clean = re.sub(r"(?i)(api[_ -]?key|secret|token|bearer)\s*[:=]\s*['\"]?[^,'\"\s}]+", r"\1: [redacted]", raw)
    clean = re.sub(r"sk-[A-Za-z0-9_\-]{12,}", "[redacted]", clean)
    clean = re.sub(r"rw[a-zA-Z0-9_\-]{12,}", "[redacted]", clean)
    return clean[:420]


def _ucm_video_provider_order(requested_provider: str) -> list[str]:
    ordered: list[str] = []
    for provider in [requested_provider, "kling", "replicate", "openai"]:
        key = str(provider or "").strip().lower()
        if key and key not in ordered:
            ordered.append(key)
    return ordered


def _ucm_attempt_record(provider: str, result: Dict[str, Any], attempt_number: int) -> Dict[str, Any]:
    readiness = provider_readiness(provider)
    return {
        "attempt": attempt_number,
        "stage": "visual",
        "provider": provider,
        "job_id": result.get("job_id"),
        "provider_job_id": result.get("provider_job_id"),
        "status": result.get("status") or result.get("provider_status") or "provider_attempt_failed",
        "success": bool(result.get("success") and result.get("status") == "completed" and result.get("playable")),
        "playable": bool(result.get("playable")),
        "configured": bool(readiness.get("configured")),
        "direct_execution_enabled": bool(readiness.get("direct_execution_enabled", provider in SUPPORTED_VIDEO_PROVIDERS)),
        "safe_error_summary": _ucm_provider_failure_summary(result) if not (result.get("success") and result.get("playable")) else "",
        "customer_safe": True,
        "credential_values_exposed": False,
    }


def _ucm_visual_child_jobs(attempts: list[Dict[str, Any]], selected: Dict[str, Any] | None = None) -> Dict[str, Any]:
    return {
        "visual_attempts": attempts,
        "visual": {
            "job_id": (selected or {}).get("job_id") or "",
            "provider": (selected or {}).get("provider") or "",
            "status": (selected or {}).get("status") or "pending",
        },
    }


def start_universal_complete_media_workflow(payload: Dict[str, Any]) -> Dict[str, Any]:
    safe_payload = dict(payload or {})
    smoke_test_mode = _ucm_bool(
        safe_payload.get("smoke_test_mode")
        or safe_payload.get("run_smoke_test")
        or safe_payload.get("five_second_smoke_test")
    )
    if smoke_test_mode:
        safe_payload["duration_seconds"] = 5
        safe_payload["duration"] = 5
        complete_media_config = safe_payload.get("complete_media_config")
        if isinstance(complete_media_config, dict):
            complete_media_config["duration_seconds"] = 5
            complete_media_config["duration"] = 5
    controls = _ucm_controls(safe_payload)
    prompt = controls["prompt"]
    job_id = str(safe_payload.get("job_id") or _safe_id("universal_complete_media_job"))
    owner_approved = _ucm_bool(safe_payload.get("owner_approved") or safe_payload.get("owner_approval_granted"))

    base_job = {
        "success": True,
        "accepted": False,
        "job_id": job_id,
        "status": "received",
        "agent_id": controls["agent_id"],
        "provider": "universal_complete_media_workflow",
        "video_provider": controls["video_provider"],
        "audio_provider": controls["audio_provider"],
        "media_type": "complete_video",
        "asset_type": "video",
        "output_type": controls["output_type"],
        "platform": controls["platform"],
        "language": controls["language"],
        "duration_seconds": controls["duration_seconds"],
        "universal_complete_media_workflow": True,
        "one_prompt_complete_media": True,
        "owner_approved": owner_approved,
        "child_jobs": {"visual_attempts": []},
        "failed_provider_attempts": [],
        "failed_preflight_checks": [],
        "blocked_provider_calls": [],
        "selected_video_job_id": "",
        "selected_video_provider": "",
        "provider_attempt_count": 0,
        "visual_attempt_count": 0,
        "smoke_test_mode": smoke_test_mode,
        "smoke_test_label": "5s smoke test" if smoke_test_mode else "",
        "safe_provider_diagnostics": {"runway": runway_safe_key_diagnostics()},
        "created_at": _now(),
        "customer_safe": True,
        "credential_values_exposed": False,
        "internal_config_exposed": False,
    }

    _write_job(base_job)

    if not owner_approved:
        return _write_job({
            **base_job,
            "success": False,
            "status": "blocked_owner_approval_required",
            "reason": "Universal complete media workflow requires owner/admin approval for live provider execution.",
        })

    plan = build_universal_complete_media_plan(safe_payload)
    preflight = _ucm_preflight_universal_media_job(safe_payload, plan)
    dry_run_mode = bool(preflight.get("dry_run"))

    if dry_run_mode or preflight.get("status") == "universal_complete_media_preflight_blocked":
        status = (
            "universal_complete_media_preflight_blocked"
            if preflight.get("status") == "universal_complete_media_preflight_blocked"
            else "universal_complete_media_preflight_dry_run"
        )
        return _write_job({
            **base_job,
            **preflight,
            "success": preflight.get("status") != "universal_complete_media_preflight_blocked",
            "accepted": True,
            "status": status,
            "stage": "preflight",
            "polling_required": False,
            "paid_provider_calls_started": False,
            "external_action_performed": False,
            "live_provider_call_triggered": False,
            "message": preflight.get("message") or CLIENT_PREFLIGHT_MESSAGE,
            "completed_at": _now(),
        })

    def _runner() -> None:
        try:
            _write_job({
                **base_job,
                "accepted": True,
                "status": "running_visual_generation",
                "preflight": preflight,
                "estimated_duration_seconds": preflight.get("estimated_duration_seconds"),
                "estimated_credit_risk": preflight.get("estimated_credit_risk"),
                "executable_visual_providers": preflight.get("executable_visual_providers"),
                "non_executable_visual_providers": preflight.get("non_executable_visual_providers"),
                "executable_audio_providers": preflight.get("executable_audio_providers"),
                "timed_plan": plan.get("timed_plan"),
                "quality_requirements": plan.get("quality_requirements"),
                "started_at": _now(),
            })

            provider_visual_prompt = _ucm_provider_safe_visual_prompt(plan["visual_prompt"], 950)

            _write_job({
                **base_job,
                "accepted": True,
                "status": "running_visual_generation",
                "timed_plan": plan.get("timed_plan"),
                "quality_requirements": plan.get("quality_requirements"),
                "visual_prompt_character_count": len(plan.get("visual_prompt") or ""),
                "provider_visual_prompt_character_count": len(provider_visual_prompt),
                "provider_visual_prompt_limit": 1000,
                "provider_visual_prompt_truncated": len(plan.get("visual_prompt") or "") > len(provider_visual_prompt),
                "started_at": _now(),
            })

            visual_attempts: list[Dict[str, Any]] = []
            failed_provider_attempts: list[Dict[str, Any]] = []
            video_result: Dict[str, Any] = {}

            executable_visual_provider_order = [
                str(item.get("provider") or "").strip().lower()
                for item in list(preflight.get("executable_visual_providers") or [])
                if item.get("provider")
            ]

            for attempt_number, video_provider in enumerate(executable_visual_provider_order, start=1):
                readiness = provider_readiness(video_provider)

                if video_provider not in SUPPORTED_VIDEO_PROVIDERS or not readiness.get("configured"):
                    skipped_result = {
                        "success": False,
                        "status": "blocked_provider_not_configured",
                        "provider": video_provider,
                        "reason": f"{video_provider} credentials are not configured.",
                    }
                    attempt = _ucm_attempt_record(video_provider, skipped_result, attempt_number)
                    visual_attempts.append(attempt)
                    failed_provider_attempts.append(attempt)
                    _write_job({
                        **base_job,
                        "accepted": True,
                        "status": "running_visual_generation",
                        "child_jobs": _ucm_visual_child_jobs(visual_attempts),
                        "failed_provider_attempts": failed_provider_attempts,
                        "provider_attempt_count": len(visual_attempts),
                        "visual_attempt_count": len(visual_attempts),
                        "non_executable_visual_providers": preflight.get("non_executable_visual_providers"),
                        "safe_provider_diagnostics": {"runway": runway_safe_key_diagnostics()},
                    })
                    continue

                attempt_job_id = _safe_id("direct_media_job")
                current_result = execute_direct_media_provider_job({
                    "job_id": attempt_job_id,
                    "agent_id": controls["agent_id"],
                    "provider": video_provider,
                    "media_type": "video",
                    "prompt": provider_visual_prompt,
                    "owner_approved": True,
                    "owner_approval_granted": True,
                })

                attempt = _ucm_attempt_record(video_provider, current_result, attempt_number)
                visual_attempts.append(attempt)

                if current_result.get("success") and current_result.get("status") == "completed" and current_result.get("playable"):
                    video_result = current_result
                    _write_job({
                        **base_job,
                        "accepted": True,
                        "status": "running_audio_generation",
                        "selected_video_job_id": current_result.get("job_id"),
                        "selected_video_provider": video_provider,
                        "video_provider": video_provider,
                        "video_job_id": current_result.get("job_id"),
                        "video_status": current_result.get("status"),
                        "video_provider_job_id": current_result.get("provider_job_id"),
                        "child_jobs": _ucm_visual_child_jobs(visual_attempts, current_result),
                        "failed_provider_attempts": failed_provider_attempts,
                        "provider_attempt_count": len(visual_attempts),
                        "visual_attempt_count": len(visual_attempts),
                        "non_executable_visual_providers": preflight.get("non_executable_visual_providers"),
                        "safe_provider_diagnostics": {"runway": runway_safe_key_diagnostics()},
                        "timed_plan": plan.get("timed_plan"),
                    })
                    break

                failed_provider_attempts.append(attempt)
                _write_job({
                    **base_job,
                    "accepted": True,
                    "status": "running_visual_generation",
                    "video_job_id": current_result.get("job_id"),
                    "video_status": current_result.get("status"),
                    "video_error": attempt.get("safe_error_summary"),
                    "child_jobs": _ucm_visual_child_jobs(visual_attempts),
                    "failed_provider_attempts": failed_provider_attempts,
                    "provider_attempt_count": len(visual_attempts),
                    "visual_attempt_count": len(visual_attempts),
                    "non_executable_visual_providers": preflight.get("non_executable_visual_providers"),
                    "safe_provider_diagnostics": {"runway": runway_safe_key_diagnostics()},
                })

            if not video_result:
                support_failure_message = (
                    "Video generation could not complete with the configured providers. "
                    "Support can review the linked provider attempts and safe diagnostics."
                )
                _write_job({
                    **base_job,
                    "success": False,
                    "accepted": True,
                    "status": "universal_complete_media_visual_failed",
                    "video_job_id": visual_attempts[-1].get("job_id") if visual_attempts else "",
                    "selected_video_job_id": "",
                    "selected_video_provider": "",
                    "video_status": "visual_failed_all_providers",
                    "video_error": failed_provider_attempts[-1].get("safe_error_summary") if failed_provider_attempts else "No configured video provider was available.",
                    "child_jobs": _ucm_visual_child_jobs(visual_attempts),
                    "failed_provider_attempts": failed_provider_attempts,
                    "provider_attempt_count": len(visual_attempts),
                    "visual_attempt_count": len(visual_attempts),
                    "safe_provider_diagnostics": {"runway": runway_safe_key_diagnostics()},
                    "support_failure_message": support_failure_message,
                    "completed_at": _now(),
                })
                return

            _write_job({
                **base_job,
                "accepted": True,
                "status": "running_audio_generation",
                "video_job_id": video_result.get("job_id"),
                "selected_video_job_id": video_result.get("job_id"),
                "selected_video_provider": video_result.get("provider") or controls["video_provider"],
                "video_provider": video_result.get("provider") or controls["video_provider"],
                "video_provider_job_id": video_result.get("provider_job_id"),
                "child_jobs": _ucm_visual_child_jobs(visual_attempts, video_result),
                "failed_provider_attempts": failed_provider_attempts,
                "provider_attempt_count": len(visual_attempts),
                "visual_attempt_count": len(visual_attempts),
                "safe_provider_diagnostics": {"runway": runway_safe_key_diagnostics()},
                "timed_plan": plan.get("timed_plan"),
            })

            provider_voice_prompt = _ucm_provider_safe_voice_prompt(
                plan["voice_prompt"],
                controls["duration_seconds"],
            )

            _write_job({
                **base_job,
                "accepted": True,
                "status": "running_audio_generation",
                "video_job_id": video_result.get("job_id"),
                "video_provider_job_id": video_result.get("provider_job_id"),
                "timed_plan": plan.get("timed_plan"),
                "voice_prompt_character_count": len(plan.get("voice_prompt") or ""),
                "provider_voice_prompt_character_count": len(provider_voice_prompt),
                "provider_voice_prompt_words": len(provider_voice_prompt.split()),
            })

            audio_result = execute_direct_media_provider_job({
                "agent_id": controls["agent_id"],
                "provider": controls["audio_provider"],
                "media_type": "audio",
                "prompt": provider_voice_prompt,
                "owner_approved": True,
                "owner_approval_granted": True,
            })

            if not audio_result.get("success") or audio_result.get("status") != "completed" or not audio_result.get("playable"):
                _write_job({
                    **base_job,
                    "success": False,
                    "accepted": True,
                    "status": "universal_complete_media_audio_failed",
                    "video_job_id": video_result.get("job_id"),
                    "selected_video_job_id": video_result.get("job_id"),
                    "selected_video_provider": video_result.get("provider") or controls["video_provider"],
                    "audio_job_id": audio_result.get("job_id"),
                    "audio_status": audio_result.get("status"),
                    "audio_error": audio_result.get("error") or audio_result.get("reason") or audio_result.get("message"),
                    "child_jobs": {
                        **_ucm_visual_child_jobs(visual_attempts, video_result),
                        "audio": {
                            "job_id": audio_result.get("job_id"),
                            "provider": controls["audio_provider"],
                            "status": audio_result.get("status"),
                        },
                    },
                    "failed_provider_attempts": failed_provider_attempts,
                    "completed_at": _now(),
                })
                return

            _write_job({
                **base_job,
                "accepted": True,
                "status": "running_synchronised_composition",
                "video_job_id": video_result.get("job_id"),
                "audio_job_id": audio_result.get("job_id"),
                "selected_video_job_id": video_result.get("job_id"),
                "selected_video_provider": video_result.get("provider") or controls["video_provider"],
                "child_jobs": {
                    **_ucm_visual_child_jobs(visual_attempts, video_result),
                    "audio": {
                        "job_id": audio_result.get("job_id"),
                        "provider": controls["audio_provider"],
                        "status": audio_result.get("status"),
                    },
                },
                "failed_provider_attempts": failed_provider_attempts,
            })

            composition_job_id = _safe_id("universal_complete_media_composition")
            composition_result = _ucm_compose_with_sync(video_result, audio_result, composition_job_id)

            if not composition_result.get("success") or composition_result.get("status") != "completed" or not composition_result.get("playable"):
                _write_job({
                    **base_job,
                    "success": False,
                    "accepted": True,
                    "status": "universal_complete_media_composition_failed",
                    "video_job_id": video_result.get("job_id"),
                    "audio_job_id": audio_result.get("job_id"),
                    "composition_job_id": composition_result.get("job_id"),
                    "selected_video_job_id": video_result.get("job_id"),
                    "selected_video_provider": video_result.get("provider") or controls["video_provider"],
                    "composition_status": composition_result.get("status"),
                    "composition_error": composition_result.get("error") or composition_result.get("reason") or composition_result.get("message"),
                    "child_jobs": {
                        **_ucm_visual_child_jobs(visual_attempts, video_result),
                        "audio": {
                            "job_id": audio_result.get("job_id"),
                            "provider": controls["audio_provider"],
                            "status": audio_result.get("status"),
                        },
                        "composition": {
                            "job_id": composition_result.get("job_id"),
                            "provider": "universal_complete_media_composer",
                            "status": composition_result.get("status"),
                        },
                    },
                    "failed_provider_attempts": failed_provider_attempts,
                    "completed_at": _now(),
                })
                return

            _write_job({
                **base_job,
                "success": True,
                "accepted": True,
                "status": "completed",
                "provider_status": "universal_complete_media_ready",
                "provider_result_status": "universal_complete_media_ready",
                "video_job_id": video_result.get("job_id"),
                "audio_job_id": audio_result.get("job_id"),
                "composition_job_id": composition_result.get("job_id"),
                "selected_video_job_id": video_result.get("job_id"),
                "selected_video_provider": video_result.get("provider") or controls["video_provider"],
                "provider_job_id": composition_result.get("job_id"),
                "playable": True,
                "preview_ready": True,
                "download_ready": True,
                "asset_path": composition_result.get("asset_path"),
                "download_url": composition_result.get("download_url"),
                "preview_url": f"/api/admin-direct-media-provider-asset?job_id={composition_result.get('job_id')}",
                "signed_preview_url": f"/api/admin-direct-media-provider-asset?job_id={composition_result.get('job_id')}",
                "final_media_type": "synchronised_video_with_audio",
                "final_duration_seconds": composition_result.get("final_duration_seconds"),
                "timed_plan": plan.get("timed_plan"),
                "quality_requirements": plan.get("quality_requirements"),
                "child_jobs": {
                    **_ucm_visual_child_jobs(visual_attempts, video_result),
                    "audio": {
                        "job_id": audio_result.get("job_id"),
                        "provider": controls["audio_provider"],
                        "status": audio_result.get("status"),
                    },
                    "composition": {
                        "job_id": composition_result.get("job_id"),
                        "provider": "universal_complete_media_composer",
                        "status": composition_result.get("status"),
                    },
                },
                "failed_provider_attempts": failed_provider_attempts,
                "provider_attempt_count": len(visual_attempts),
                "visual_attempt_count": len(visual_attempts),
                "completed_at": _now(),
            })

        except Exception as error:
            _write_job({
                **base_job,
                "success": False,
                "accepted": True,
                "status": "universal_complete_media_exception",
                "error": str(error)[:1200],
                "completed_at": _now(),
            })

    thread = threading.Thread(target=_runner, name=f"universal_complete_media_{job_id}", daemon=True)
    thread.start()

    return {
        **base_job,
        "success": True,
        "accepted": True,
        "polling_required": True,
        "status": "queued",
        "message": "Universal complete media workflow accepted. One prompt will generate visual, natural audio, synchronise, and compose the final playable file.",
        "preflight": preflight,
        "paid_provider_calls_started": False,
        "estimated_duration_seconds": preflight.get("estimated_duration_seconds"),
        "estimated_credit_risk": preflight.get("estimated_credit_risk"),
        "executable_visual_providers": preflight.get("executable_visual_providers"),
        "non_executable_visual_providers": preflight.get("non_executable_visual_providers"),
        "executable_audio_providers": preflight.get("executable_audio_providers"),
        "failed_preflight_checks": [],
        "blocked_provider_calls": [],
        "smoke_test_mode": smoke_test_mode,
        "smoke_test_label": "5s smoke test" if smoke_test_mode else "",
        "timed_plan": plan.get("timed_plan"),
        "quality_requirements": plan.get("quality_requirements"),
        "child_jobs": {"visual_attempts": []},
        "failed_provider_attempts": [],
        "selected_video_job_id": "",
        "selected_video_provider": "",
        "provider_attempt_count": 0,
        "visual_attempt_count": 0,
        "safe_provider_diagnostics": {"runway": runway_safe_key_diagnostics()},
    }


def universal_complete_media_status() -> Dict[str, Any]:
    return {
        "success": True,
        "universal_complete_media_workflow_ready": True,
        "one_prompt_complete_media": True,
        "universal_not_ecommerce_only": True,
        "supported_controls": [
            "prompt",
            "output_type",
            "industry",
            "target_audience",
            "platform",
            "duration",
            "aspect_ratio",
            "language",
            "accent",
            "tone",
            "voice_style",
            "age_range",
            "gender_presentation",
            "ethnicity_or_cultural_appearance",
            "avatar_likeness",
            "face_shape",
            "skin_tone",
            "facial_features",
            "hair_style",
            "hair_colour",
            "eye_colour",
            "wardrobe",
            "expressions",
            "emotion",
            "eye_contact",
            "gestures",
            "body_language",
            "lip_sync_accuracy",
            "speaking_pace",
            "camera_framing",
            "lighting_style",
            "background_setting",
            "brand_style",
            "product_or_service_details",
            "offer",
            "call_to_action",
            "captions",
            "music_style",
            "sound_effects",
            "pacing",
            "visual_style",
            "camera_movement",
            "compliance_notes",
            "number_of_variations",
            "final_delivery_format",
        ],
        "workflow": [
            "interpret_prompt_and_controls",
            "build_timed_media_plan",
            "generate_visual_or_avatar_asset",
            "generate_natural_audio",
            "synchronise_audio_video",
            "compose_final_playable_media_file",
        ],
        "quality_requirements": {
            "complete_synchronicity_required": True,
            "natural_non_robotic_audio": True,
            "avoid_choppy_audio": True,
            "customer_safe": True,
            "credential_values_exposed": False,
        },
        "credential_values_exposed": False,
        "customer_safe": True,
    }
