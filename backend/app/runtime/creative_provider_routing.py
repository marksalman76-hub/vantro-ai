from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional


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
        "provider": "higgsfield",
        "model": "Kling 3.0 Turbo",
        "quality": "720p",
        "capability": "video_generation",
    },
    "1080p": {
        "provider": "higgsfield",
        "model": "Kling 3.0",
        "quality": "1080p",
        "capability": "video_generation",
    },
    "4k": {
        "provider": "higgsfield",
        "model": "Cinema Studio 4K",
        "quality": "4K",
        "capability": "video_generation",
    },
}

IMAGE_MODELS_BY_TIER = {
    "standard": {
        "provider": "nano_banana",
        "model": "Nano Banana 2",
        "tier": "standard",
        "capability": "image_generation",
    },
    "production": {
        "provider": "nano_banana",
        "model": "Nano Banana 2",
        "tier": "production",
        "capability": "image_generation",
    },
    "premium": {
        "provider": "nano_banana",
        "model": "Nano Banana Pro",
        "tier": "premium",
        "capability": "image_generation",
    },
    "pro": {
        "provider": "nano_banana",
        "model": "Nano Banana Pro",
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

    selected_media_types = _media_types(media_type or _context_value(request_context, "media_type", "type"))
    if not selected_media_types:
        return {
            "success": False,
            "agent_id": agent_id,
            "canonical_agent_id": canonical_agent_id,
            "reason": "unsupported_media_type",
            "credential_values_exposed": False,
        }

    route: Dict[str, Any] = {
        "success": True,
        "agent_id": agent_id,
        "canonical_agent_id": canonical_agent_id,
        "media_types": sorted(selected_media_types),
        "owner_governed_execution_required": True,
        "credential_values_exposed": False,
        "created_at": _now_iso(),
    }

    if "video" in selected_media_types:
        quality = normalize_video_quality(video_quality or _context_value(request_context, "video_quality", "quality"))
        route["video"] = dict(VIDEO_MODELS_BY_QUALITY[quality])

    if "image" in selected_media_types:
        tier = normalize_image_tier(image_tier or _context_value(request_context, "image_tier", "image_quality", "quality"))
        route["image"] = dict(IMAGE_MODELS_BY_TIER[tier])

    return route


def creative_provider_status() -> Dict[str, Any]:
    return {
        "success": True,
        "creative_agent_ids": sorted(CREATIVE_AGENT_IDS),
        "aliases": dict(CREATIVE_AGENT_ALIASES),
        "providers": {
            "higgsfield": {
                "display_name": "Higgsfield",
                "capabilities": ["video_generation"],
                "models": ["Kling 3.0 Turbo", "Kling 3.0", "Cinema Studio 4K"],
                "credential_values_exposed": False,
            },
            "nano_banana": {
                "display_name": "Nano Banana",
                "capabilities": ["image_generation"],
                "models": ["Nano Banana 2", "Nano Banana Pro"],
                "credential_values_exposed": False,
            },
        },
        "credential_values_exposed": False,
        "created_at": _now_iso(),
    }
