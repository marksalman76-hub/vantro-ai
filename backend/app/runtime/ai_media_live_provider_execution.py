from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


AI_MEDIA_PROVIDER_ENV_MAP = {
    "openai_image": {
        "env_keys": ["OPENAI_API_KEY"],
        "category": "image",
        "capabilities": ["image_generation", "image_variation", "product_visual"],
        "live_execution_supported": True,
    },
    "runway": {
        "env_keys": ["RUNWAY_API_KEY"],
        "category": "video",
        "capabilities": ["video_generation", "cinematic_generation", "image_to_video"],
        "live_execution_supported": False,
    },
    "kling": {
        "env_keys": ["KLING_API_KEY"],
        "category": "video",
        "capabilities": ["video_generation", "character_motion", "cinematic_video"],
        "live_execution_supported": False,
    },
    "pika": {
        "env_keys": ["PIKA_API_KEY"],
        "category": "video",
        "capabilities": ["video_generation", "short_form_video"],
        "live_execution_supported": False,
    },
    "elevenlabs": {
        "env_keys": ["ELEVENLABS_API_KEY"],
        "category": "voice",
        "capabilities": ["voice_generation", "dubbing", "multilingual_audio"],
        "live_execution_supported": False,
    },
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_text(value: Any, fallback: str = "") -> str:
    if value is None:
        return fallback
    return str(value).strip() or fallback


def _env_present(keys: List[str]) -> bool:
    return any(bool(os.getenv(key, "").strip()) for key in keys)


def detect_ai_media_provider_readiness() -> Dict[str, Any]:
    providers = {}

    for provider_id, config in AI_MEDIA_PROVIDER_ENV_MAP.items():
        env_keys = list(config.get("env_keys", []))
        configured = _env_present(env_keys)
        providers[provider_id] = {
            "provider_id": provider_id,
            "configured": configured,
            "env_keys_checked": env_keys,
            "category": config.get("category"),
            "capabilities": config.get("capabilities", []),
            "live_execution_supported": bool(config.get("live_execution_supported")),
            "credential_values_exposed": False,
        }

    configured_providers = [
        provider_id for provider_id, provider in providers.items()
        if provider.get("configured")
    ]

    live_supported_configured = [
        provider_id for provider_id, provider in providers.items()
        if provider.get("configured") and provider.get("live_execution_supported")
    ]

    return {
        "success": True,
        "runtime": "ai_media_live_provider_execution",
        "status": "ready",
        "provider_detection_enabled": True,
        "configured_provider_count": len(configured_providers),
        "configured_providers": configured_providers,
        "live_supported_configured_providers": live_supported_configured,
        "providers": providers,
        "governance_preserved": True,
        "secret_exposure": False,
        "layout_changes": False,
    }


def select_provider_route(provider_ready_packet: Dict[str, Any]) -> Dict[str, Any]:
    readiness = detect_ai_media_provider_readiness()
    providers = readiness.get("providers", {})

    primary_slot = _safe_text(provider_ready_packet.get("primary_provider_slot"), "multi_modal_generation_provider")
    fallback_slots = provider_ready_packet.get("fallback_provider_slots", []) or []
    media_type = _safe_text(provider_ready_packet.get("media_type"), "").lower()

    if "voice" in media_type or "dub" in media_type:
        preferred = ["elevenlabs"]
    elif "image" in media_type or "product" in media_type:
        preferred = ["openai_image"]
    elif "video" in media_type or "ugc" in media_type:
        preferred = ["runway", "kling", "pika", "openai_image"]
    else:
        preferred = ["openai_image", "runway", "kling", "pika", "elevenlabs"]

    available = [
        provider_id for provider_id in preferred
        if providers.get(provider_id, {}).get("configured")
    ]

    selected_provider = available[0] if available else None

    return {
        "success": True,
        "routing_mode": "configured_provider_first_with_safe_fallback",
        "primary_provider_slot": primary_slot,
        "fallback_provider_slots": fallback_slots,
        "preferred_provider_order": preferred,
        "available_provider_order": available,
        "selected_provider": selected_provider,
        "provider_available": bool(selected_provider),
        "live_execution_supported": bool(
            selected_provider
            and providers.get(selected_provider, {}).get("live_execution_supported")
        ),
        "manual_review_required": not bool(selected_provider),
        "fallback_to_adapter_stub": not bool(selected_provider),
        "secret_exposure": False,
    }


def build_standard_ai_media_provider_result(
    *,
    success: bool,
    provider_id: Optional[str],
    execution_status: str,
    provider_ready_packet: Dict[str, Any],
    provider_response: Optional[Dict[str, Any]] = None,
    error: Optional[str] = None,
) -> Dict[str, Any]:
    return {
        "success": bool(success),
        "runtime": "ai_media_live_provider_execution",
        "execution_status": execution_status,
        "provider_id": provider_id,
        "provider_response": provider_response or {},
        "error": error,
        "packet_type": provider_ready_packet.get("packet_type"),
        "media_type": provider_ready_packet.get("media_type"),
        "platform": provider_ready_packet.get("platform"),
        "brand": provider_ready_packet.get("brand"),
        "product": provider_ready_packet.get("product"),
        "governance_controls": provider_ready_packet.get("governance_controls", {}),
        "quality_controls": provider_ready_packet.get("quality_controls", {}),
        "fallback_controls": provider_ready_packet.get("fallback_controls", {}),
        "continuity_controls": provider_ready_packet.get("continuity_controls", {}),
        "multilingual_controls": provider_ready_packet.get("multilingual_controls", {}),
        "generated_at": _now(),
        "secret_exposure": False,
        "layout_changes": False,
    }


def execute_ai_media_provider_ready_packet(provider_ready_packet: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(provider_ready_packet, dict):
        return build_standard_ai_media_provider_result(
            success=False,
            provider_id=None,
            execution_status="invalid_provider_packet",
            provider_ready_packet={},
            error="provider_ready_packet_required",
        )

    if provider_ready_packet.get("execution_allowed") is False:
        return build_standard_ai_media_provider_result(
            success=False,
            provider_id=None,
            execution_status="blocked_by_orchestration",
            provider_ready_packet=provider_ready_packet,
            error="provider_execution_not_allowed_by_orchestration",
        )

    route = select_provider_route(provider_ready_packet)
    selected_provider = route.get("selected_provider")

    if not selected_provider:
        return build_standard_ai_media_provider_result(
            success=True,
            provider_id=None,
            execution_status="prepared_no_live_provider_configured",
            provider_ready_packet=provider_ready_packet,
            provider_response={
                "route": route,
                "adapter_stub_ready": True,
                "live_generation_attempted": False,
                "reason": "no_configured_ai_media_provider",
            },
        )

    if not route.get("live_execution_supported"):
        return build_standard_ai_media_provider_result(
            success=True,
            provider_id=selected_provider,
            execution_status="prepared_provider_adapter_stub",
            provider_ready_packet=provider_ready_packet,
            provider_response={
                "route": route,
                "adapter_stub_ready": True,
                "live_generation_attempted": False,
                "reason": "provider_configured_but_live_adapter_not_enabled_yet",
            },
        )

    # Foundation stage: do not call external providers yet.
    # This intentionally standardises the result shape before enabling paid live API calls.
    return build_standard_ai_media_provider_result(
        success=True,
        provider_id=selected_provider,
        execution_status="prepared_live_adapter_ready",
        provider_ready_packet=provider_ready_packet,
        provider_response={
            "route": route,
            "adapter_stub_ready": True,
            "live_generation_attempted": False,
            "reason": "live_adapter_foundation_ready_external_call_disabled_until_next_phase",
        },
    )
