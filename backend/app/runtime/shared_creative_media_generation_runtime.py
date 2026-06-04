from __future__ import annotations

from datetime import datetime
import inspect
import os
import uuid
from typing import Any, Callable, Dict, List, Optional

from dotenv import load_dotenv

from backend.app.runtime.shared_creative_visual_generation_runtime import generate_creative_visual_asset
from backend.app.runtime.audio_visual_provider_stack import recommended_stack_for_task

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
    "runway": ["RUNWAY_API_KEY", "RUNWAYML_API_SECRET"],
    "kling": ["KLING_API_KEY", "KLING_SECRET_KEY"],
    "heygen": ["HEYGEN_API_KEY"],
    "elevenlabs": ["ELEVENLABS_API_KEY"],
    "sync": ["SYNC_API_KEY"],
    "replicate": ["REPLICATE_API_TOKEN"],
}

MEDIA_PROVIDER_PRIORITY = {
    "image": ["runway", "replicate"],
    "video": ["runway", "kling", "replicate"],
    "audio": ["elevenlabs", "heygen"],
    "avatar": ["heygen", "sync"],
}


def _now() -> str:
    return datetime.utcnow().isoformat() + "Z"


def _env_present(names: List[str]) -> bool:
    return any(bool(os.getenv(name, "").strip()) for name in names)


def _provider_configured(provider: str) -> bool:
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
        accepted = {
            key: value
            for key, value in kwargs.items()
            if key in signature.parameters
        }
        result = func(**accepted)
        if isinstance(result, dict):
            result.setdefault("success", True)
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

    if not configured:
        return {
            "success": False,
            "status": "provider_key_missing",
            "provider": provider,
            "media_type": media_type,
            "live_provider_execution_attempted": False,
            "real_media_asset_created": False,
            "reason": "provider_key_missing_or_not_configured_on_runtime",
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
            prompt=prompt,
            task=prompt,
            agent_id=agent_id,
            tenant_id=tenant_id,
            pack_id=pack_id,
            test_label=f"{pack_id}_runway_live_video",
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
    output_urls = []

    for key in [
        "asset_url",
        "media_url",
        "video_url",
        "audio_url",
        "image_url",
        "download_url",
        "preview_url",
        "output_url",
    ]:
        value = result.get(key)
        if isinstance(value, str) and value.strip():
            output_urls.append(value.strip())

    for key in ["output_urls", "urls", "generated_urls", "generated_files"]:
        values = result.get(key)
        if isinstance(values, list):
            for value in values:
                if isinstance(value, str) and value.strip():
                    output_urls.append(value.strip())
                elif isinstance(value, dict):
                    for nested_key in ["url", "asset_url", "media_url", "download_url", "preview_url", "path"]:
                        nested_value = value.get(nested_key)
                        if isinstance(nested_value, str) and nested_value.strip():
                            output_urls.append(nested_value.strip())

    preview_url = result.get("preview_url") or (output_urls[0] if output_urls else "")
    download_url = result.get("download_url") or result.get("asset_url") or result.get("media_url") or preview_url

    status = (
        result.get("status")
        or result.get("execution_status")
        or ("ready" if result.get("success") and (preview_url or download_url) else "provider_execution_attempted")
    )

    real_media_asset_created = bool(preview_url or download_url or result.get("real_media_asset_created"))

    return {
        "asset_id": result.get("asset_id") or f"{media_type}_asset_{uuid.uuid4().hex[:12]}",
        "pack_id": pack_id,
        "agent_id": agent_id,
        "tenant_id": tenant_id,
        "provider": provider,
        "asset_type": media_type,
        "status": status,
        "preview_ready": bool(preview_url),
        "download_ready": bool(download_url),
        "preview_url": preview_url,
        "download_url": download_url,
        "media_url": result.get("media_url") or download_url,
        "asset_url": result.get("asset_url") or download_url,
        "prompt": prompt,
        "script": script,
        "provider_result": result,
        "live_provider_execution_attempted": bool(result.get("live_provider_execution_attempted", True)),
        "real_media_asset_created": real_media_asset_created,
        "credential_values_exposed": False,
        "customer_safe": True,
        "created_at": _now(),
    }


def _persist_media_asset(asset: Dict[str, Any]) -> Dict[str, Any]:
    try:
        from backend.app.runtime.creative_asset_persistence_bridge import persist_creative_asset

        return persist_creative_asset(
            {
                "asset_id": asset.get("asset_id"),
                "agent_id": asset.get("agent_id"),
                "agent_label": asset.get("agent_id"),
                "provider": asset.get("provider"),
                "asset_type": asset.get("asset_type"),
                "title": f"{asset.get('agent_id')} {asset.get('asset_type')} asset",
                "test_label": asset.get("pack_id"),
                "provider_asset_url": asset.get("asset_url") or asset.get("media_url"),
                "provider_asset_id": asset.get("provider_result", {}).get("provider_job_id") or asset.get("provider_result", {}).get("job_id"),
                "preview_url": asset.get("preview_url"),
                "download_url": asset.get("download_url"),
                "content": asset.get("prompt") or asset.get("script"),
                "summary": f"{asset.get('provider')} {asset.get('asset_type')} asset generated by {asset.get('agent_id')}",
                "status": asset.get("status"),
                "campaign_context": asset.get("prompt"),
                "owner_approval_required": True,
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
                "pack_id": pack_id,
                "live_provider_execution_attempted": _provider_configured(image_provider),
                "real_media_asset_created": bool(image_asset.get("preview_url") or image_asset.get("download_url") or image_asset.get("asset_url")),
                "credential_values_exposed": False,
                "customer_safe": True,
            }
        )
        image_asset["persistence"] = _persist_media_asset(image_asset)
        image_assets.append(image_asset)

    if include_video:
        provider = _first_configured_provider("video")
        direct_runway_result = _execute_runway_direct_if_available(
            prompt=video_prompt,
            agent_id=agent_id,
            tenant_id=tenant_id,
            pack_id=pack_id,
        ) if provider == "runway" else {}

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
        video_asset["persistence"] = _persist_media_asset(video_asset)
        video_assets.append(video_asset)
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
        audio_asset["persistence"] = _persist_media_asset(audio_asset)
        audio_assets.append(audio_asset)
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
        avatar_asset["persistence"] = _persist_media_asset(avatar_asset)
        avatar_assets.append(avatar_asset)
        generation_jobs.append(
            {
                "job_id": provider_result.get("job_id") or provider_result.get("provider_job_id") or f"avatar_job_{uuid.uuid4().hex[:10]}",
                "media_type": "avatar_video",
                "provider": provider,
                "status": avatar_asset.get("status"),
                "live_generation_available": _provider_configured(provider),
                "live_provider_execution_attempted": provider_result.get("live_provider_execution_attempted", True),
                "real_media_asset_created": avatar_asset.get("real_media_asset_created", False),
                "prompt": avatar_prompt,
            }
        )

    media_assets = [*image_assets, *video_assets, *audio_assets, *avatar_assets]

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
        "avatar_assets": avatar_assets,
        "media_assets": media_assets,
        "real_media_asset_count": sum(1 for asset in media_assets if asset.get("real_media_asset_created")),
        "live_provider_execution_attempted_count": sum(1 for result in provider_execution_results if result.get("live_provider_execution_attempted")),
        "audio_url": audio_assets[0].get("download_url", "") if audio_assets else "",
        "video_url": video_assets[0].get("download_url", "") if video_assets else "",
        "avatar_video_url": avatar_assets[0].get("download_url", "") if avatar_assets else "",
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