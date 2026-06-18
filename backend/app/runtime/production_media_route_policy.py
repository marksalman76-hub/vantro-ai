"""
Production media route policy.

Purpose:
Keep the full provider registry available, but stop the default paid-client
media path from randomly allocating across every provider.

Launch lanes:
- General/no-human media: Kling + ElevenLabs + internal FFmpeg
- Human/avatar/likeness media: HeyGen + ElevenLabs + Sync + internal FFmpeg
- Cinematic premium: Runway admin-only until API entitlement/workspace is resolved
- Image/thumbnail: OpenAI/Replicate route, not default complete-media video
- Fallback: supportable failure record, not uncontrolled paid-provider fanout
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, List


GENERAL_MEDIA_ROUTE = {
    "route_name": "general_media_default",
    "human_mode": "no_human",
    "visual_provider": "kling",
    "audio_provider": "elevenlabs",
    "lip_sync_provider": None,
    "composition_provider": "internal_ffmpeg_composition",
    "caption_provider": "media_script_caption_plan",
    "fallback_provider": "provider_output_or_failure_record",
    "requires_likeness_consent": False,
    "client_default_enabled": True,
    "admin_override_required": False,
}

HUMAN_LIKENESS_ROUTE = {
    "route_name": "human_likeness_default",
    "human_modes": [
        "generate_new_avatar_person",
        "use_client_uploaded_face_likeness",
        "use_saved_brand_spokesperson_avatar",
    ],
    "avatar_provider": "heygen",
    "visual_provider": "heygen",
    "audio_provider": "elevenlabs",
    "lip_sync_provider": "sync",
    "composition_provider": "internal_ffmpeg_composition",
    "caption_provider": "media_script_caption_plan",
    "fallback_provider": "provider_output_or_failure_record",
    "requires_likeness_consent": True,
    "client_default_enabled": True,
    "admin_override_required": False,
}

PREMIUM_CINEMATIC_ROUTE = {
    "route_name": "premium_cinematic_admin_override",
    "visual_provider": "runway",
    "audio_provider": "elevenlabs",
    "composition_provider": "internal_ffmpeg_composition",
    "requires_owner_or_admin_override": True,
    "client_default_enabled": False,
    "blocked_until": "runway_api_workspace_entitlement_confirmed",
}

IMAGE_THUMBNAIL_ROUTE = {
    "route_name": "image_thumbnail_route",
    "image_providers": ["openai", "replicate"],
    "client_default_complete_media_video_route": False,
}

FALLBACK_ROUTE = {
    "route_name": "supportable_failure_fallback",
    "fallback_provider": "provider_output_or_failure_record",
    "paid_provider_fanout_allowed": False,
    "provider_retry_count_default": 0,
}

VALID_HUMAN_MODES = {
    "no_human",
    "generate_new_avatar_person",
    "use_client_uploaded_face_likeness",
    "use_saved_brand_spokesperson_avatar",
}


def normalize_human_mode(value: Any) -> str:
    raw = str(value or "no_human").strip().lower()
    aliases = {
        "none": "no_human",
        "no human": "no_human",
        "no_human_avatar": "no_human",
        "generate_avatar": "generate_new_avatar_person",
        "generated_avatar": "generate_new_avatar_person",
        "new_avatar": "generate_new_avatar_person",
        "uploaded_likeness": "use_client_uploaded_face_likeness",
        "client_likeness": "use_client_uploaded_face_likeness",
        "saved_avatar": "use_saved_brand_spokesperson_avatar",
        "brand_spokesperson": "use_saved_brand_spokesperson_avatar",
    }
    normalized = aliases.get(raw, raw)
    return normalized if normalized in VALID_HUMAN_MODES else "no_human"


def resolve_production_media_route(payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    payload = payload or {}
    human_mode = normalize_human_mode(
        payload.get("human_mode")
        or payload.get("humanMode")
        or payload.get("avatar_mode")
        or payload.get("avatarMode")
    )

    admin_override = bool(
        payload.get("admin_provider_override")
        or payload.get("owner_provider_override")
        or payload.get("adminOverride")
    )

    requested_visual = str(
        payload.get("video_provider")
        or payload.get("visual_provider")
        or payload.get("selected_visual_provider")
        or ""
    ).strip().lower()

    if admin_override and requested_visual == "runway":
        route = dict(PREMIUM_CINEMATIC_ROUTE)
        route["selected_route_reason"] = "admin_override_runway"
        route["human_mode"] = human_mode
        return route

    if human_mode == "no_human":
        route = dict(GENERAL_MEDIA_ROUTE)
        route["selected_route_reason"] = "default_no_human_general_media"
        return route

    route = dict(HUMAN_LIKENESS_ROUTE)
    route["human_mode"] = human_mode
    route["selected_route_reason"] = "human_likeness_route_required"

    if human_mode in {
        "use_client_uploaded_face_likeness",
        "use_saved_brand_spokesperson_avatar",
    }:
        route["explicit_consent_required"] = True
        route["privacy_safe_likeness_storage_required"] = True
        route["likeness_governance_required"] = True

    return route


def production_media_route_policy_summary() -> Dict[str, Any]:
    return {
        "production_media_route_policy_enabled": True,
        "full_provider_registry_preserved": True,
        "default_general_route": GENERAL_MEDIA_ROUTE,
        "human_likeness_route": HUMAN_LIKENESS_ROUTE,
        "premium_cinematic_route": PREMIUM_CINEMATIC_ROUTE,
        "image_thumbnail_route": IMAGE_THUMBNAIL_ROUTE,
        "fallback_route": FALLBACK_ROUTE,
        "no_uncontrolled_paid_provider_fanout": True,
        "default_client_video_provider": "kling",
        "default_client_audio_provider": "elevenlabs",
        "default_client_composition_provider": "internal_ffmpeg_composition",
        "human_likeness_avatar_provider": "heygen",
        "human_likeness_lip_sync_provider": "sync",
        "runway_default_client_route_enabled": False,
    }
