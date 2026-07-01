from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from app.runtime.creative_agent_capability_policy import (
    creative_capability_policy_status,
    effective_allowed_models,
)


CREATIVE_AGENT_IDS: set[str] = {
    "ugc_media_agent",
    "ugc_creative_agent",
    "product_image_agent",
    "ad_creative_agent",
    "creative_rotation_agent",
    "social_media_content_agent",
    "ads_optimisation_agent",
}

CREATIVE_AGENT_ALIASES: dict[str, str] = {
    "paid_ads_agent": "ads_optimisation_agent",
    "social_media_manager_content_creator_agent": "social_media_content_agent",
    "product_video_agent": "ugc_media_agent",
    "product_visual_agent": "product_image_agent",
    "campaign_creative_agent": "ad_creative_agent",
}

VIDEO_MODELS_BY_QUALITY = {
    "720p": {
        "provider": "kling",
        "model": "Kling 3.0 Turbo",
        "model_id": "kling3_0_turbo",
        "quality": "720p",
        "capability": "video_generation",
    },
    "1080p": {
        "provider": "kling",
        "model": "Kling 3.0",
        "model_id": "kling3_0",
        "quality": "1080p",
        "capability": "video_generation",
    },
    "4k": {
        "provider": "kling",
        "model": "Cinema Studio 4K",
        "model_id": "cinematic_studio_3_0",
        "quality": "4K",
        "capability": "video_generation",
    },
}

IMAGE_MODELS_BY_TIER = {
    "standard": {
        "provider": "openai_dalle",
        "model": "DALL-E 3",
        "model_id": "dall-e-3",
        "quality": "standard",
        "tier": "standard",
        "capability": "image_generation",
    },
    "production": {
        "provider": "openai_dalle",
        "model": "DALL-E 3",
        "model_id": "dall-e-3",
        "quality": "standard",
        "tier": "production",
        "capability": "image_generation",
    },
    "premium": {
        "provider": "openai_dalle",
        "model": "DALL-E 3 HD",
        "model_id": "dall-e-3",
        "quality": "hd",
        "tier": "premium",
        "capability": "image_generation",
    },
    "pro": {
        "provider": "openai_dalle",
        "model": "DALL-E 3 HD",
        "model_id": "dall-e-3",
        "quality": "hd",
        "tier": "pro",
        "capability": "image_generation",
    },
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_creative_agent_id(agent_id: str) -> str:
    raw = str(agent_id or "").strip()
    return CREATIVE_AGENT_ALIASES.get(raw, raw)


def is_creative_agent(agent_id: str) -> bool:
    return normalize_creative_agent_id(agent_id) in CREATIVE_AGENT_IDS


def normalize_video_quality(value: Any) -> str:
    raw = str(value or "").strip().lower().replace(" ", "")
    if raw in {"720", "720p", "hd"}:
        return "720p"
    if raw in {"4k", "2160", "2160p", "uhd"}:
        return "4k"
    return "1080p"


def normalize_image_tier(value: Any) -> str:
    raw = str(value or "").strip().lower().replace(" ", "_")
    if raw in {"premium", "pro", "professional", "high_end"}:
        return "premium" if raw != "pro" else "pro"
    if raw in {"production", "prod"}:
        return "production"
    return "standard"


def _media_types(media_type: str) -> set[str]:
    raw = str(media_type or "both").strip().lower()
    if raw in {"video", "image"}:
        return {raw}
    if raw in {
        "product_demo",
        "service_promo",
        "social_ad",
        "brand_story",
        "testimonial",
        "explainer",
        "campaign",
    }:
        return {"video"}
    if raw in {"image_graphic", "graphic", "static_image", "banner"}:
        return {"image"}
    if raw in {"script", "script_only"}:
        return {"video"}
    if raw in {"both", "media", "creative", "video_image", "image_video"}:
        return {"video", "image"}
    return set()


def _context_value(request_context: Optional[Dict[str, Any]], *keys: str) -> Any:
    context = request_context or {}
    media_request = context.get("media_request") if isinstance(context.get("media_request"), dict) else {}
    for key in keys:
        if key in context and context[key] not in (None, ""):
            return context[key]
        if key in media_request and media_request[key] not in (None, ""):
            return media_request[key]
    return ""


def resolve_creative_provider_route(
    agent_id: str,
    media_type: str = "both",
    video_quality: str = "",
    image_tier: str = "",
    package_tier: str = "enterprise",
    admin_override: bool = False,
    request_context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    canonical_agent_id = normalize_creative_agent_id(agent_id)
    if canonical_agent_id not in CREATIVE_AGENT_IDS:
        return {
            "success": False,
            "agent_id": agent_id,
            "canonical_agent_id": canonical_agent_id,
            "reason": "unknown_creative_agent",
            "credential_values_exposed": False,
        }

    requested_media_type = str(media_type or "").strip()
    if requested_media_type.lower() in {"", "both"}:
        requested_media_type = _context_value(request_context, "media_type", "type") or "both"

    selected_media_types = _media_types(requested_media_type)
    if not selected_media_types:
        return {
            "success": False,
            "agent_id": agent_id,
            "canonical_agent_id": canonical_agent_id,
            "reason": "unsupported_media_type",
            "credential_values_exposed": False,
        }

    entitlement = effective_allowed_models(
        canonical_agent_id,
        package_tier,
        admin_override=admin_override,
    )
    allowed_models = entitlement["effective"]
    for selected_media_type in sorted(selected_media_types):
        if not entitlement["agent_allowed"].get(selected_media_type):
            return {
                "success": False,
                "agent_id": agent_id,
                "canonical_agent_id": canonical_agent_id,
                "reason": "media_type_not_allowed_for_agent",
                "blocked_media_type": selected_media_type,
                "allowed_models": allowed_models,
                "entitlement": entitlement,
                "credential_values_exposed": False,
            }
        if not allowed_models.get(selected_media_type):
            return {
                "success": False,
                "agent_id": agent_id,
                "canonical_agent_id": canonical_agent_id,
                "reason": "media_type_not_allowed_for_package",
                "blocked_media_type": selected_media_type,
                "allowed_models": allowed_models,
                "entitlement": entitlement,
                "credential_values_exposed": False,
            }

    route: Dict[str, Any] = {
        "success": True,
        "agent_id": agent_id,
        "canonical_agent_id": canonical_agent_id,
        "media_types": sorted(selected_media_types),
        "allowed_models": allowed_models,
        "entitlement": entitlement,
        "owner_governed_execution_required": True,
        "credential_values_exposed": False,
        "created_at": _now_iso(),
    }

    if "video" in selected_media_types:
        quality = normalize_video_quality(video_quality or _context_value(request_context, "video_quality", "quality"))
        selected_video = dict(VIDEO_MODELS_BY_QUALITY[quality])
        selected_video_model = selected_video["model"]
        if selected_video_model not in entitlement["agent_allowed"]["video"]:
            return {
                "success": False,
                "agent_id": agent_id,
                "canonical_agent_id": canonical_agent_id,
                "reason": "model_not_allowed_for_agent",
                "blocked_media_type": "video",
                "blocked_model": selected_video_model,
                "allowed_models": allowed_models,
                "entitlement": entitlement,
                "credential_values_exposed": False,
            }
        if selected_video_model not in entitlement["package_allowed"]["video"]:
            return {
                "success": False,
                "agent_id": agent_id,
                "canonical_agent_id": canonical_agent_id,
                "reason": "model_not_allowed_for_package",
                "blocked_media_type": "video",
                "blocked_model": selected_video_model,
                "allowed_models": allowed_models,
                "entitlement": entitlement,
                "credential_values_exposed": False,
            }
        route["video"] = selected_video

    if "image" in selected_media_types:
        tier = normalize_image_tier(image_tier or _context_value(request_context, "image_tier", "image_quality", "quality"))
        selected_image = dict(IMAGE_MODELS_BY_TIER[tier])
        selected_image_model = selected_image["model"]
        if selected_image_model not in entitlement["agent_allowed"]["image"]:
            return {
                "success": False,
                "agent_id": agent_id,
                "canonical_agent_id": canonical_agent_id,
                "reason": "model_not_allowed_for_agent",
                "blocked_media_type": "image",
                "blocked_model": selected_image_model,
                "allowed_models": allowed_models,
                "entitlement": entitlement,
                "credential_values_exposed": False,
            }
        if selected_image_model not in entitlement["package_allowed"]["image"]:
            return {
                "success": False,
                "agent_id": agent_id,
                "canonical_agent_id": canonical_agent_id,
                "reason": "model_not_allowed_for_package",
                "blocked_media_type": "image",
                "blocked_model": selected_image_model,
                "allowed_models": allowed_models,
                "entitlement": entitlement,
                "credential_values_exposed": False,
            }
        route["image"] = selected_image

    return route


def creative_provider_status() -> Dict[str, Any]:
    return {
        "success": True,
        "creative_agent_ids": sorted(CREATIVE_AGENT_IDS),
        "aliases": dict(CREATIVE_AGENT_ALIASES),
        "providers": {
            "kling": {
                "display_name": "Kling",
                "capabilities": ["video_generation"],
                "models": ["Kling 3.0 Turbo", "Kling 3.0", "Cinema Studio 4K"],
                "model_ids": ["kling3_0_turbo", "kling3_0", "cinematic_studio_3_0"],
                "api_models": ["kling-v1-5 (std)", "kling-v1-5 (pro)", "kling-v2-master (pro)"],
                "execution_surface": "kling_direct",
                "voiceover": "elevenlabs",
                "credential_values_exposed": False,
            },
            "openai_dalle": {
                "display_name": "AI Image Generation",
                "capabilities": ["image_generation"],
                "models": ["DALL-E 3", "DALL-E 3 HD"],
                "model_ids": ["dall-e-3", "dall-e-3"],
                "execution_surface": "dalle_direct",
                "credential_values_exposed": False,
            },
        },
        "capability_policy": creative_capability_policy_status(),
        "credential_values_exposed": False,
        "created_at": _now_iso(),
    }
