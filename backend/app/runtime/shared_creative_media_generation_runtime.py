from __future__ import annotations

from datetime import datetime
import inspect
import os
import re
import uuid
from typing import Any, Callable, Dict, List, Optional

from dotenv import load_dotenv

from backend.app.runtime.audio_visual_provider_stack import recommended_stack_for_task
from backend.app.runtime.shared_creative_visual_generation_runtime import generate_creative_visual_asset

load_dotenv(".env.local")


CREATIVE_MEDIA_AGENTS = {
    "ugc_creative_agent",
    "paid_ads_agent",
    "product_image_agent",
    "social_media_manager_content_creator_agent",
    "brand_strategy_agent",
    "marketing_specialist_agent",
    "website_landing_apps_agent",
    "influencer_collaboration_agent",
    "creative_rotation_agent",
    "product_development_agent",
    "ecommerce_agent",
}

PROVIDER_ENV_KEYS = {
    # Render/project env compatibility.
    "runway": ["RUNWAYML_API_SECRET", "RUNWAY_API_KEY", "RUNWAY_CREATE_JOB_URL"],
    "kling": ["KLING_API_KEY", "KLING_ACCESS_KEY", "KLING_SECRET_KEY", "KLING_CREATE_JOB_URL"],
    "heygen": ["HEYGEN_API_KEY", "HEYGEN_CREATE_JOB_URL"],
    "elevenlabs": ["ELEVENLABS_API_KEY"],
    "sync": ["SYNC_API_KEY", "HEYGEN_API_KEY", "HEYGEN_CREATE_JOB_URL"],
    "replicate": ["REPLICATE_API_TOKEN", "REPLICATE_API_KEY"],
}

MEDIA_PROVIDER_PRIORITY = {
    "image": ["runway", "replicate"],
    "video": ["runway", "kling", "replicate"],
    "audio": ["elevenlabs", "heygen"],
    "avatar": ["heygen", "sync"],
}

METADATA_ONLY_STATUSES = {
    "provider_job_created_or_attempted",
    "live_provider_ready_endpoint_missing",
    "metadata_fallback",
    "endpoint_missing",
    "blocked_owner_approval_required",
    "provider_execution_attempted",
}


def _now() -> str:
    return datetime.utcnow().isoformat() + "Z"


def _env_present(names: List[str]) -> bool:
    return any(bool(os.getenv(name, "").strip()) for name in names)


def _env_flag_enabled(name: str) -> bool:
    return str(os.getenv(name, "")).strip().lower() in {"1", "true", "yes", "on", "enabled"}


def _provider_dispatch_diagnostics() -> Dict[str, bool]:
    live_external_calls_enabled = _env_flag_enabled("LIVE_EXTERNAL_CALLS_ENABLED")
    owner_approved_live_activation = _env_flag_enabled("OWNER_APPROVED_LIVE_ACTIVATION")
    real_provider_http_dispatch_enabled = _env_flag_enabled("REAL_PROVIDER_HTTP_DISPATCH_ENABLED")
    return {
        "provider_dispatch_enabled": bool(
            live_external_calls_enabled
            and owner_approved_live_activation
            and real_provider_http_dispatch_enabled
        ),
        "live_external_calls_enabled": live_external_calls_enabled,
        "owner_approved_live_activation": owner_approved_live_activation,
        "real_provider_http_dispatch_enabled": real_provider_http_dispatch_enabled,
    }


def _provider_configured(provider: str) -> bool:
    provider = str(provider or "").strip().lower()

    if provider == "kling":
        # Kling may be configured as one key or an access/secret pair.
        return bool(os.getenv("KLING_API_KEY", "").strip()) or (
            bool(os.getenv("KLING_ACCESS_KEY", "").strip())
            and bool(os.getenv("KLING_SECRET_KEY", "").strip())
        )

    return _env_present(PROVIDER_ENV_KEYS.get(provider, []))


def _first_configured_provider(media_type: str) -> str:
    for provider in MEDIA_PROVIDER_PRIORITY.get(media_type, []):
        if _provider_configured(provider):
            return provider
    return MEDIA_PROVIDER_PRIORITY.get(media_type, ["internal"])[0]


def _voiceover_script(task: str, agent_id: str) -> str:
    return f"""Premium voiceover script for {agent_id}

Hook:
Stop scrolling — this is the premium creative your brand has been missing.

Body:
Designed for a polished, conversion-focused campaign, this asset introduces the product with clear visual proof, emotional relevance, and a premium brand feel.

CTA:
Tap to discover the full offer today.

Task context:
{task}
"""


def _video_prompt(task: str, agent_id: str) -> str:
    return f"""Create an actual premium 9:16 short-form video asset for {agent_id}.

Task context:
{task}

Required output:
- vertical 9:16 social ad
- premium lighting
- realistic product/creator framing
- polished commercial pacing
- hook in first 2 seconds
- product or offer reveal
- benefit demonstration
- proof/transformation moment
- CTA end frame

Style:
Premium, realistic, agency-grade, brand-safe, high-conversion.
"""


def _avatar_prompt(task: str, agent_id: str) -> str:
    return f"""Create an actual presenter/avatar video asset for {agent_id}.

Task context:
{task}

Presenter style:
Polished, natural, trustworthy, commercially credible.

Delivery:
Clear voice, natural pacing, lip-sync suitable, brand-safe claims.
"""


def _safe_call(func: Callable[..., Any], **kwargs: Any) -> Dict[str, Any]:
    try:
        signature = inspect.signature(func)
        accepted = {key: value for key, value in kwargs.items() if key in signature.parameters}
        result = func(**accepted)
        if isinstance(result, dict):
            result.setdefault("success", True)
            result.setdefault("credential_values_exposed", False)
            result.setdefault("customer_safe", True)
            return result
        return {
            "success": True,
            "result": result,
            "credential_values_exposed": False,
            "customer_safe": True,
        }
    except Exception as exc:
        return {
            "success": False,
            "status": "provider_execution_failed",
            "error": str(exc)[:800],
            "credential_values_exposed": False,
            "customer_safe": True,
        }


def _execute_ai_media_provider_packet(
    *,
    provider: str,
    media_type: str,
    prompt: str,
    script: str = "",
    agent_id: str,
    tenant_id: str,
    pack_id: str,
) -> Dict[str, Any]:
    configured = _provider_configured(provider)
    dispatch = _provider_dispatch_diagnostics()

    if not configured:
        return {
            "success": False,
            "status": "provider_key_missing",
            "provider": provider,
            "media_type": media_type,
            "live_provider_execution_attempted": False,
            "real_media_asset_created": False,
            "reason": "provider_key_missing_or_not_configured_on_runtime",
            "provider_configured": False,
            "provider_key_selected": provider,
            "provider_unavailable_reason": "provider_key_missing_or_not_configured_on_runtime",
            "playable_asset_created": False,
            "signed_delivery_created": False,
            "metadata_only": True,
            **dispatch,
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    packet = {
        "packet_type": "creative_media_provider_execution_packet",
        "execution_allowed": True,
        "manual_review_required": False,
        "primary_provider_slot": provider,
        "fallback_provider_slots": [
            item for item in MEDIA_PROVIDER_PRIORITY.get(media_type, []) if item != provider
        ],
        "provider_parameters": {
            "provider": provider,
            "media_type": media_type,
            "prompt": prompt,
            "script": script,
            "agent_id": agent_id,
            "tenant_id": tenant_id,
            "pack_id": pack_id,
            "aspect_ratio": "9:16",
            "duration": 5,
            "format": "mp4" if media_type in {"video", "avatar"} else "mp3" if media_type == "audio" else "png",
        },
        "governance_controls": {
            "owner_approved": True,
            "customer_safe": True,
            "credential_values_exposed": False,
        },
        "quality_controls": {
            "requires_preview": True,
            "requires_download": True,
            "requires_customer_safe_asset": True,
        },
    }

    try:
        from backend.app.runtime.ai_media_live_provider_execution import execute_ai_media_provider_ready_packet

        result = execute_ai_media_provider_ready_packet(packet)
        if not isinstance(result, dict):
            result = {"success": True, "result": result}

        result.setdefault("provider", provider)
        result.setdefault("media_type", media_type)
        result.setdefault("live_provider_execution_attempted", True)
        result.setdefault("provider_configured", bool(configured))
        result.setdefault("provider_key_selected", provider)
        result.setdefault("provider_unavailable_reason", "")
        result.setdefault("playable_asset_created", bool(result.get("real_media_asset_created")))
        result.setdefault("signed_delivery_created", False)
        result.setdefault("metadata_only", not bool(result.get("real_media_asset_created")))
        for key, value in dispatch.items():
            result.setdefault(key, value)
        result.setdefault("credential_values_exposed", False)
        result.setdefault("customer_safe", True)
        return result
    except Exception as exc:
        return {
            "success": False,
            "status": "provider_bridge_failed",
            "provider": provider,
            "media_type": media_type,
            "live_provider_execution_attempted": True,
            "real_media_asset_created": False,
            "error": str(exc)[:800],
            "provider_configured": bool(configured),
            "provider_key_selected": provider,
            "provider_unavailable_reason": "provider_bridge_failed",
            "playable_asset_created": False,
            "signed_delivery_created": False,
            "metadata_only": True,
            **dispatch,
            "credential_values_exposed": False,
            "customer_safe": True,
        }


def _execute_runway_direct_if_available(
    *,
    prompt: str,
    agent_id: str,
    tenant_id: str,
    pack_id: str,
) -> Dict[str, Any]:
    if not _provider_configured("runway"):
        return {
            "success": False,
            "status": "provider_key_missing",
            "provider": "runway",
            "media_type": "video",
            "live_provider_execution_attempted": False,
            "real_media_asset_created": False,
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    try:
        from backend.app.runtime.runway_live_video_quality_adapter import run_runway_text_to_video_quality_test

        return _safe_call(
            run_runway_text_to_video_quality_test,
            prompt_text=prompt,
            test_label=f"{pack_id}_runway_live_video",
            model=os.getenv("RUNWAY_MODEL", "").strip() or None,
            ratio="9:16",
            duration=5,
            allow_live_execution=True,
        )
    except Exception as exc:
        return {
            "success": False,
            "status": "runway_adapter_unavailable",
            "provider": "runway",
            "media_type": "video",
            "live_provider_execution_attempted": True,
            "real_media_asset_created": False,
            "error": str(exc)[:800],
            "credential_values_exposed": False,
            "customer_safe": True,
        }


def _extract_candidate_urls(result: Dict[str, Any]) -> List[str]:
    urls: List[str] = []

    for key in [
        "asset_url",
        "media_url",
        "video_url",
        "audio_url",
        "image_url",
        "download_url",
        "preview_url",
        "output_url",
        "video_path",
        "audio_path",
        "image_path",
        "video_url_preview",
    ]:
        value = result.get(key)
        if isinstance(value, str) and value.strip():
            urls.append(value.strip())

    for key in ["output_urls", "urls", "generated_urls", "generated_files", "outputs", "output"]:
        values = result.get(key)
        if isinstance(values, list):
            for value in values:
                if isinstance(value, str) and value.strip():
                    urls.append(value.strip())
                elif isinstance(value, dict):
                    for nested_key in [
                        "url",
                        "asset_url",
                        "media_url",
                        "download_url",
                        "preview_url",
                        "path",
                        "video_path",
                        "audio_path",
                        "image_path",
                        "video_url_preview",
                    ]:
                        nested_value = value.get(nested_key)
                        if isinstance(nested_value, str) and nested_value.strip():
                            urls.append(nested_value.strip())
        elif isinstance(values, dict):
            urls.extend(_extract_candidate_urls(values))
        elif isinstance(values, str):
            urls.extend(re.findall(r"(?:https?://|data:)[^\s'\"\]\)]+", values))

    clean: List[str] = []
    for url in urls:
        candidate = str(url).strip().rstrip("',)]}")
        if candidate and candidate not in clean:
            clean.append(candidate)
    return clean


def _is_media_reference(value: Any) -> bool:
    raw = str(value or "").strip()
    if not raw:
        return False
    lower = raw.lower()
    if raw.startswith("http://") or raw.startswith("https://"):
        return True
    if raw.startswith("data:video") or raw.startswith("data:audio") or raw.startswith("data:image"):
        return True
    if lower.endswith((".mp4", ".mov", ".webm", ".mp3", ".wav", ".m4a", ".png", ".jpg", ".jpeg", ".webp")):
        return True
    if "/runtime_outputs/" in lower or "\\runtime_outputs\\" in lower:
        return True
    return False


def _normalise_asset_from_result(
    *,
    result: Dict[str, Any],
    provider: str,
    media_type: str,
    agent_id: str,
    tenant_id: str,
    pack_id: str,
    prompt: str,
    script: str = "",
) -> Dict[str, Any]:
    output_urls = _extract_candidate_urls(result)

    local_video_path = result.get("video_path") if result.get("video_saved") else ""
    local_audio_path = result.get("audio_path") if result.get("audio_saved") else ""
    local_image_path = result.get("image_path") if result.get("image_saved") else ""
    local_path = local_video_path or local_audio_path or local_image_path

    preview_url = (
        result.get("preview_url")
        or local_path
        or result.get("video_url_preview")
        or (output_urls[0] if output_urls else "")
    )
    download_url = (
        result.get("download_url")
        or result.get("asset_url")
        or result.get("media_url")
        or local_path
        or preview_url
    )

    status = (
        result.get("status")
        or result.get("execution_status")
        or ("ready" if result.get("success") and (preview_url or download_url) else "provider_execution_attempted")
    )

    real_media_asset_created = bool(
        _is_media_reference(preview_url)
        or _is_media_reference(download_url)
        or result.get("real_media_asset_created")
        or result.get("video_saved")
        or result.get("audio_saved")
        or result.get("image_saved")
    )

    # Critical fix: successful local MP4 downloads must not remain metadata-only.
    if real_media_asset_created and str(status or "").lower() in METADATA_ONLY_STATUSES:
        status = "persisted"

    return {
        "asset_id": result.get("asset_id") or f"{media_type}_asset_{uuid.uuid4().hex[:12]}",
        "pack_id": pack_id,
        "agent_id": agent_id,
        "tenant_id": tenant_id,
        "provider": provider,
        "asset_type": media_type,
        "media_type": media_type,
        "status": status,
        "preview_ready": bool(preview_url and real_media_asset_created),
        "download_ready": bool(download_url and real_media_asset_created),
        "preview_url": preview_url if real_media_asset_created else "",
        "download_url": download_url if real_media_asset_created else "",
        "media_url": (result.get("media_url") or download_url) if real_media_asset_created else "",
        "asset_url": (result.get("asset_url") or download_url) if real_media_asset_created else "",
        "prompt": prompt,
        "script": script,
        "provider_result": result,
        "live_provider_execution_attempted": bool(result.get("live_provider_execution_attempted", True)),
        "real_media_asset_created": bool(real_media_asset_created),
        "credential_values_exposed": False,
        "customer_safe": True,
        "created_at": _now(),
    }


def _has_real_media_url(asset: Dict[str, Any]) -> bool:
    values = [
        asset.get("preview_url"),
        asset.get("download_url"),
        asset.get("asset_url"),
        asset.get("media_url"),
        asset.get("video_url"),
        asset.get("audio_url"),
        asset.get("provider_asset_url"),
        asset.get("provider_asset_id"),
    ]
    provider_result = asset.get("provider_result")
    if isinstance(provider_result, dict):
        values.extend(
            [
                provider_result.get("video_path"),
                provider_result.get("audio_path"),
                provider_result.get("image_path"),
                provider_result.get("video_url_preview"),
            ]
        )
    return any(_is_media_reference(value) for value in values) or bool(asset.get("real_media_asset_created"))


def _is_provider_job_metadata_only(asset: Dict[str, Any]) -> bool:
    status = str(asset.get("status") or "").lower()
    if status in METADATA_ONLY_STATUSES or "provider_job_created_or_attempted" in status:
        return not _has_real_media_url(asset)
    if "metadata_fallback" in status:
        return True
    return False


def _compose_video_audio_asset(
    video_assets: List[Dict[str, Any]],
    audio_assets: List[Dict[str, Any]],
    agent_id: str,
    tenant_id: str,
    pack_id: str,
    prompt: str,
) -> Dict[str, Any]:
    if not video_assets or not audio_assets:
        return {}

    video = video_assets[0]
    audio = audio_assets[0]

    video_url = video.get("download_url") or video.get("preview_url") or video.get("asset_url") or video.get("media_url")
    audio_url = audio.get("download_url") or audio.get("preview_url") or audio.get("asset_url") or audio.get("media_url")

    if not video_url or not audio_url:
        return {}

    try:
        from backend.app.runtime.sync_live_lipsync_adapter import compose_lipsync_video

        composed = compose_lipsync_video(
            video_url=video_url,
            audio_url=audio_url,
            script=audio.get("script") or audio.get("prompt") or prompt,
            tenant_id=tenant_id,
            agent_id=agent_id,
        )
    except Exception as exc:
        return {
            "success": False,
            "status": "combined_video_compose_failed",
            "error": str(exc)[:500],
        }

    composed_url = (
        composed.get("composed_video_url")
        or composed.get("final_video_url")
        or composed.get("video_url")
        or composed.get("download_url")
        or composed.get("video_path")
    )

    if not composed_url:
        return {
            "success": False,
            "status": composed.get("status") or "combined_video_not_available",
            "compose_result": composed,
        }

    return {
        "success": True,
        "asset_id": f"combined_video_asset_{uuid.uuid4().hex[:10]}",
        "agent_id": agent_id,
        "tenant_id": tenant_id,
        "pack_id": pack_id,
        "provider": composed.get("provider") or "internal_ffmpeg",
        "asset_type": "combined_video",
        "media_type": "combined_video",
        "status": composed.get("status") or "final_synced_video_persisted",
        "asset_url": composed_url,
        "preview_url": composed_url,
        "download_url": composed_url,
        "prompt": prompt,
        "script": audio.get("script") or audio.get("prompt") or prompt,
        "real_media_asset_created": True,
        "source_video_asset_id": video.get("asset_id"),
        "source_audio_asset_id": audio.get("asset_id"),
        "provider_result": composed,
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def _is_provider_endpoint_placeholder(asset: Dict[str, Any], result: Dict[str, Any]) -> bool:
    status = str(asset.get("status") or asset.get("execution_status") or "").lower()
    result_status = str(result.get("execution_status") or result.get("status") or "").lower()
    return "live_provider_ready_endpoint_missing" in status or "live_provider_ready_endpoint_missing" in result_status


def _persist_media_asset(asset: Dict[str, Any]) -> Dict[str, Any]:
    try:
        from backend.app.runtime.creative_asset_persistence_bridge import persist_creative_asset

        provider_result = asset.get("provider_result") if isinstance(asset.get("provider_result"), dict) else {}
        provider_asset_url = (
            asset.get("asset_url")
            or asset.get("media_url")
            or asset.get("download_url")
            or asset.get("preview_url")
        )

        return persist_creative_asset(
            {
                "asset_id": asset.get("asset_id"),
                "agent_id": asset.get("agent_id"),
                "agent_label": asset.get("agent_id"),
                "provider": asset.get("provider"),
                "provider_key": asset.get("provider"),
                "asset_type": asset.get("asset_type"),
                "media_type": asset.get("media_type") or asset.get("asset_type"),
                "title": f"{asset.get('agent_id')} {asset.get('asset_type')} asset",
                "test_label": asset.get("pack_id"),
                "provider_asset_url": provider_asset_url,
                "provider_asset_id": (
                    provider_result.get("provider_job_id")
                    or provider_result.get("job_id")
                    or provider_result.get("video_path")
                    or provider_result.get("audio_path")
                    or provider_result.get("image_path")
                    or asset.get("asset_id")
                ),
                "preview_url": asset.get("preview_url"),
                "download_url": asset.get("download_url"),
                "content": asset.get("prompt") or asset.get("script"),
                "summary": f"{asset.get('provider')} {asset.get('asset_type')} asset generated by {asset.get('agent_id')}",
                "status": asset.get("status"),
                "campaign_context": asset.get("prompt"),
                "owner_approval_required": True,
                "governed": True,
                "credential_values_exposed": False,
                "customer_safe": True,
            }
        )
    except Exception as exc:
        return {
            "success": False,
            "persisted": False,
            "reason": "creative_asset_persist_failed",
            "error": str(exc)[:800],
            "credential_values_exposed": False,
            "customer_safe": True,
        }


def _append_if_persistable(asset: Dict[str, Any], target: List[Dict[str, Any]]) -> Dict[str, Any]:
    if _is_provider_job_metadata_only(asset):
        asset["persistence"] = {
            "success": False,
            "persisted": False,
            "reason": "metadata_only_asset_not_persisted",
            "credential_values_exposed": False,
            "customer_safe": True,
        }
        asset["playable_asset_created"] = False
        asset["signed_delivery_created"] = False
        asset["metadata_only"] = True
        return asset

    asset["persistence"] = _persist_media_asset(asset)
    persistence = asset["persistence"] if isinstance(asset.get("persistence"), dict) else {}
    if persistence.get("metadata_only") or not persistence.get("playable"):
        asset["preview_ready"] = False
        asset["download_ready"] = False
        asset["real_media_asset_created"] = False
        asset["playable"] = False
        asset["metadata_only"] = True
        asset["playable_asset_created"] = False
        asset["signed_delivery_created"] = False
    else:
        asset["preview_ready"] = bool(persistence.get("preview_ready"))
        asset["download_ready"] = bool(persistence.get("download_ready"))
        asset["playable"] = True
        asset["metadata_only"] = False
        asset["playable_asset_created"] = True
        asset["signed_delivery_created"] = bool(persistence.get("preview_ready") or persistence.get("download_ready"))
    target.append(asset)
    return asset


def generate_creative_media_pack(
    *,
    task: str,
    agent_id: str,
    tenant_id: str = "owner_admin",
    include_image: bool = True,
    include_audio: bool = True,
    include_video: bool = True,
    include_avatar: bool = True,
) -> Dict[str, Any]:
    agent_id = str(agent_id or "").strip() or "creative_agent"
    task = str(task or "").strip()

    pack_id = f"creative_media_pack_{uuid.uuid4().hex[:12]}"

    audio_script = _voiceover_script(task, agent_id) if include_audio else ""
    video_prompt = _video_prompt(task, agent_id) if include_video else ""
    avatar_prompt = _avatar_prompt(task, agent_id) if include_avatar else ""

    provider_stack = recommended_stack_for_task(agent_id, task)

    image_assets: List[Dict[str, Any]] = []
    audio_assets: List[Dict[str, Any]] = []
    video_assets: List[Dict[str, Any]] = []
    avatar_assets: List[Dict[str, Any]] = []
    provider_execution_results: List[Dict[str, Any]] = []
    generation_jobs: List[Dict[str, Any]] = []

    if include_image:
        image_provider = _first_configured_provider("image")
        image_asset = generate_creative_visual_asset(
            prompt=task,
            agent_id=agent_id,
            tenant_id=tenant_id,
            asset_kind=f"{agent_id}_image_asset",
        )
        image_asset = image_asset if isinstance(image_asset, dict) else {"result": image_asset}
        image_asset.update(
            {
                "provider": image_provider if _provider_configured(image_provider) else image_asset.get("provider", "internal"),
                "asset_type": "image",
                "media_type": "image",
                "pack_id": pack_id,
                "agent_id": agent_id,
                "tenant_id": tenant_id,
                "live_provider_execution_attempted": _provider_configured(image_provider),
                "real_media_asset_created": bool(
                    image_asset.get("preview_url")
                    or image_asset.get("download_url")
                    or image_asset.get("asset_url")
                    or image_asset.get("media_url")
                ),
                "credential_values_exposed": False,
                "customer_safe": True,
            }
        )
        # Avoid persisting giant embedded data images that slow the viewer.
        image_url = str(image_asset.get("preview_url") or image_asset.get("download_url") or image_asset.get("asset_url") or "")
        if image_asset.get("real_media_asset_created") and not (image_url.startswith("data:image") and len(image_url) > 250_000):
            _append_if_persistable(image_asset, image_assets)
        elif image_asset.get("real_media_asset_created"):
            image_asset["persistence"] = {
                "success": False,
                "persisted": False,
                "reason": "embedded_image_too_large_for_registry",
                "credential_values_exposed": False,
                "customer_safe": True,
            }
            image_asset["preview_ready"] = False
            image_asset["download_ready"] = False
            image_asset["real_media_asset_created"] = False
            image_asset["playable"] = False
            image_asset["metadata_only"] = True
            image_assets.append(image_asset)

    if include_video:
        provider = _first_configured_provider("video")
        direct_runway_result = (
            _execute_runway_direct_if_available(
                prompt=video_prompt,
                agent_id=agent_id,
                tenant_id=tenant_id,
                pack_id=pack_id,
            )
            if provider == "runway"
            else {}
        )

        if direct_runway_result and direct_runway_result.get("success"):
            provider_result = direct_runway_result
            provider_result["provider"] = "runway"
            provider_result["media_type"] = "video"
        else:
            provider_result = _execute_ai_media_provider_packet(
                provider=provider,
                media_type="video",
                prompt=video_prompt,
                agent_id=agent_id,
                tenant_id=tenant_id,
                pack_id=pack_id,
            )

        provider_execution_results.append(provider_result)
        video_asset = _normalise_asset_from_result(
            result=provider_result,
            provider=provider,
            media_type="video",
            agent_id=agent_id,
            tenant_id=tenant_id,
            pack_id=pack_id,
            prompt=video_prompt,
        )
        _append_if_persistable(video_asset, video_assets)
        generation_jobs.append(
            {
                "job_id": provider_result.get("job_id") or provider_result.get("provider_job_id") or f"video_job_{uuid.uuid4().hex[:10]}",
                "media_type": "video",
                "provider": provider,
                "status": video_asset.get("status"),
                "live_generation_available": _provider_configured(provider),
                "live_provider_execution_attempted": provider_result.get("live_provider_execution_attempted", True),
                "real_media_asset_created": video_asset.get("real_media_asset_created", False),
                "prompt": video_prompt,
            }
        )

    if include_audio:
        provider = _first_configured_provider("audio")
        provider_result = _execute_ai_media_provider_packet(
            provider=provider,
            media_type="audio",
            prompt=audio_script,
            script=audio_script,
            agent_id=agent_id,
            tenant_id=tenant_id,
            pack_id=pack_id,
        )
        provider_execution_results.append(provider_result)
        audio_asset = _normalise_asset_from_result(
            result=provider_result,
            provider=provider,
            media_type="audio",
            agent_id=agent_id,
            tenant_id=tenant_id,
            pack_id=pack_id,
            prompt=audio_script,
            script=audio_script,
        )
        _append_if_persistable(audio_asset, audio_assets)
        generation_jobs.append(
            {
                "job_id": provider_result.get("job_id") or provider_result.get("provider_job_id") or f"audio_job_{uuid.uuid4().hex[:10]}",
                "media_type": "audio",
                "provider": provider,
                "status": audio_asset.get("status"),
                "live_generation_available": _provider_configured(provider),
                "live_provider_execution_attempted": provider_result.get("live_provider_execution_attempted", True),
                "real_media_asset_created": audio_asset.get("real_media_asset_created", False),
                "script": audio_script,
            }
        )

    if include_avatar:
        provider = _first_configured_provider("avatar")
        provider_result = _execute_ai_media_provider_packet(
            provider=provider,
            media_type="avatar",
            prompt=avatar_prompt,
            script=audio_script,
            agent_id=agent_id,
            tenant_id=tenant_id,
            pack_id=pack_id,
        )
        provider_execution_results.append(provider_result)
        avatar_asset = _normalise_asset_from_result(
            result=provider_result,
            provider=provider,
            media_type="avatar_video",
            agent_id=agent_id,
            tenant_id=tenant_id,
            pack_id=pack_id,
            prompt=avatar_prompt,
            script=audio_script,
        )

        if _is_provider_endpoint_placeholder(avatar_asset, provider_result):
            if video_assets:
                source_video = dict(video_assets[0])
                avatar_asset = dict(source_video)
                avatar_asset.update(
                    {
                        "asset_id": f"avatar_video_asset_{uuid.uuid4().hex[:10]}",
                        "asset_type": "avatar_video",
                        "media_type": "avatar_video",
                        "provider": source_video.get("provider") or "runway",
                        "status": "fallback_to_real_video_asset",
                        "prompt": avatar_prompt,
                        "script": audio_script,
                        "fallback_reason": "avatar_provider_endpoint_missing",
                        "fallback_source_asset_id": source_video.get("asset_id"),
                        "real_media_asset_created": bool(
                            source_video.get("preview_url")
                            or source_video.get("download_url")
                            or source_video.get("asset_url")
                            or source_video.get("media_url")
                        ),
                    }
                )
            else:
                avatar_asset["status"] = "avatar_provider_endpoint_missing_no_video_fallback"
                avatar_asset["real_media_asset_created"] = False

        if (
            avatar_asset.get("real_media_asset_created")
            or avatar_asset.get("preview_url")
            or avatar_asset.get("download_url")
            or avatar_asset.get("asset_url")
            or avatar_asset.get("media_url")
        ):
            _append_if_persistable(avatar_asset, avatar_assets)

        generation_jobs.append(
            {
                "job_id": provider_result.get("job_id") or provider_result.get("provider_job_id") or f"avatar_job_{uuid.uuid4().hex[:10]}",
                "media_type": "avatar_video",
                "provider": avatar_asset.get("provider") or provider,
                "status": avatar_asset.get("status"),
                "live_generation_available": _provider_configured(provider),
                "live_provider_execution_attempted": provider_result.get("live_provider_execution_attempted", True),
                "real_media_asset_created": avatar_asset.get("real_media_asset_created", False),
                "prompt": avatar_prompt,
            }
        )

    combined_video_assets: List[Dict[str, Any]] = []
    combined_video_asset = _compose_video_audio_asset(
        video_assets=video_assets,
        audio_assets=audio_assets,
        agent_id=agent_id,
        tenant_id=tenant_id,
        pack_id=pack_id,
        prompt=task,
    )
    if combined_video_asset.get("success") and combined_video_asset.get("real_media_asset_created"):
        _append_if_persistable(combined_video_asset, combined_video_assets)

    media_assets = [*image_assets, *combined_video_assets, *video_assets, *audio_assets, *avatar_assets]
    persisted_asset_records = [
        asset.get("persistence")
        for asset in media_assets
        if isinstance(asset.get("persistence"), dict) and asset.get("persistence", {}).get("success")
    ]
    playable_asset_records = [
        asset.get("persistence")
        for asset in media_assets
        if isinstance(asset.get("persistence"), dict) and asset.get("persistence", {}).get("playable")
    ]
    playable_media_assets = [
        asset
        for asset in media_assets
        if bool(asset.get("playable") or (isinstance(asset.get("persistence"), dict) and asset.get("persistence", {}).get("playable")))
    ]

    return {
        "success": True,
        "media_pack_id": pack_id,
        "agent_id": agent_id,
        "tenant_id": tenant_id,
        "supports_image": include_image,
        "supports_audio": include_audio,
        "supports_video": include_video,
        "supports_avatar_video": include_avatar,
        "image_assets": image_assets,
        "audio_assets": audio_assets,
        "video_assets": video_assets,
        "combined_video_assets": combined_video_assets,
        "avatar_assets": avatar_assets,
        "media_assets": media_assets,
        "real_media_asset_count": len(playable_media_assets),
        "playable_asset_count": len(playable_asset_records),
        "metadata_only_asset_count": sum(1 for asset in media_assets if asset.get("metadata_only")),
        "persisted_asset_count": len(persisted_asset_records),
        "persisted_asset_records": persisted_asset_records,
        "creative_asset_registry_write_attempted": True,
        "live_provider_execution_attempted_count": sum(1 for result in provider_execution_results if result.get("live_provider_execution_attempted")),
        "audio_url": audio_assets[0].get("download_url", "") if audio_assets and audio_assets[0].get("playable") else "",
        "video_url": combined_video_assets[0].get("download_url", "") if combined_video_assets and combined_video_assets[0].get("playable") else (video_assets[0].get("download_url", "") if video_assets and video_assets[0].get("playable") else ""),
        "combined_video_url": combined_video_assets[0].get("download_url", "") if combined_video_assets and combined_video_assets[0].get("playable") else "",
        "avatar_video_url": avatar_assets[0].get("download_url", "") if avatar_assets and avatar_assets[0].get("playable") else "",
        "voiceover_script": audio_script,
        "video_prompt": video_prompt,
        "avatar_prompt": avatar_prompt,
        "generation_jobs": generation_jobs,
        "provider_execution_results": provider_execution_results,
        "provider_stack": provider_stack,
        "provider_chain": provider_stack.get("preferred_providers", []) if isinstance(provider_stack, dict) else [],
        "created_at": _now(),
        "customer_safe": True,
        "credential_values_exposed": False,
    }
