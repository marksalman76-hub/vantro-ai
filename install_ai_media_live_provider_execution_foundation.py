from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
runtime_dir = ROOT / "backend" / "app" / "runtime"
runtime_dir.mkdir(parents=True, exist_ok=True)

live_provider_file = runtime_dir / "ai_media_live_provider_execution.py"
bridge_file = runtime_dir / "provider_connector_registry.py"

backups = ROOT / "backups"
backups.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

for path in [live_provider_file, bridge_file]:
    if path.exists():
        backup = backups / f"{path.stem}_before_ai_media_live_provider_execution_{timestamp}.py"
        backup.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")

live_provider_code = r'''
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
'''

live_provider_file.write_text(live_provider_code.strip() + "\n", encoding="utf-8")

if not bridge_file.exists():
    bridge_file.write_text("", encoding="utf-8")

bridge_text = bridge_file.read_text(encoding="utf-8")

bridge_import = """
from backend.app.runtime.ai_media_live_provider_execution import (
    detect_ai_media_provider_readiness,
    execute_ai_media_provider_ready_packet,
    select_provider_route,
)
"""

if "execute_ai_media_provider_ready_packet" not in bridge_text:
    bridge_text = bridge_import.strip() + "\n\n" + bridge_text

bridge_helpers = r'''

def ai_media_provider_execution_bridge(payload):
    if not isinstance(payload, dict):
        return {
            "success": False,
            "error": "payload_required",
            "runtime": "ai_media_provider_execution_bridge",
        }

    packet = None

    if isinstance(payload.get("provider_ready_execution_packet"), dict):
        packet = payload.get("provider_ready_execution_packet")
    elif isinstance(payload.get("ai_media_provider_ready_packet"), dict):
        packet = payload.get("ai_media_provider_ready_packet")
    elif isinstance(payload.get("orchestration_packet"), dict):
        packet = payload["orchestration_packet"].get("provider_ready_execution_packet")
    elif isinstance(payload.get("creative_direction"), dict):
        nested = payload["creative_direction"].get("orchestration_packet", {})
        if isinstance(nested, dict):
            packet = nested.get("provider_ready_execution_packet")

    if not isinstance(packet, dict):
        return {
            "success": False,
            "error": "provider_ready_execution_packet_missing",
            "runtime": "ai_media_provider_execution_bridge",
        }

    result = execute_ai_media_provider_ready_packet(packet)
    result["bridge_runtime"] = "ai_media_provider_execution_bridge"
    return result
'''

if "def ai_media_provider_execution_bridge(" not in bridge_text:
    bridge_text = bridge_text.rstrip() + "\n" + bridge_helpers + "\n"

bridge_file.write_text(bridge_text, encoding="utf-8")

test_file = ROOT / "test_ai_media_live_provider_execution_foundation.py"
test_file.write_text(r'''
from backend.app.runtime.ai_media_live_provider_execution import (
    detect_ai_media_provider_readiness,
    execute_ai_media_provider_ready_packet,
    select_provider_route,
)
from backend.app.runtime.provider_connector_registry import ai_media_provider_execution_bridge


def sample_packet():
    return {
        "packet_type": "provider_ready_ai_media_execution_packet",
        "execution_allowed": True,
        "manual_review_required": False,
        "primary_provider_slot": "video_generation_provider",
        "fallback_provider_slots": ["ugc_avatar_provider", "generic_video_provider"],
        "media_type": "ugc video",
        "platform": "TikTok",
        "brand": "Provider Foundation Brand",
        "product": "Provider Foundation Product",
        "target_audience": "online buyers",
        "language": "English",
        "region": "global",
        "provider_parameters": {
            "style": "premium UGC",
            "aspect_ratio_priority": "9:16",
            "scene_plan": [{"scene": 1}, {"scene": 2}, {"scene": 3}, {"scene": 4}],
        },
        "continuity_controls": {"same_face_required": False},
        "multilingual_controls": {"multilingual_required": False},
        "fallback_controls": {"fallback_enabled": True},
        "governance_controls": {
            "do_not_publish_without_governance": True,
            "owner_review_required_for_spend_or_campaign_scaling": True,
        },
        "quality_controls": {
            "overall_score": 92,
            "premium_only": True,
            "no_placeholder_outputs": True,
        },
    }


def main():
    readiness = detect_ai_media_provider_readiness()
    assert readiness["success"] is True
    assert readiness["provider_detection_enabled"] is True
    assert readiness["secret_exposure"] is False
    assert "openai_image" in readiness["providers"]
    assert "runway" in readiness["providers"]
    assert "elevenlabs" in readiness["providers"]

    route = select_provider_route(sample_packet())
    assert route["success"] is True
    assert "preferred_provider_order" in route
    assert route["secret_exposure"] is False

    result = execute_ai_media_provider_ready_packet(sample_packet())
    assert result["success"] is True
    assert result["runtime"] == "ai_media_live_provider_execution"
    assert result["execution_status"] in {
        "prepared_no_live_provider_configured",
        "prepared_provider_adapter_stub",
        "prepared_live_adapter_ready",
    }
    assert result["secret_exposure"] is False
    assert result["governance_controls"]["do_not_publish_without_governance"] is True

    bridge_result = ai_media_provider_execution_bridge({
        "provider_ready_execution_packet": sample_packet()
    })
    assert bridge_result["success"] is True
    assert bridge_result["bridge_runtime"] == "ai_media_provider_execution_bridge"

    missing = ai_media_provider_execution_bridge({"normal": "payload"})
    assert missing["success"] is False
    assert missing["error"] == "provider_ready_execution_packet_missing"

    print("AI_MEDIA_LIVE_PROVIDER_EXECUTION_FOUNDATION_OK")


if __name__ == "__main__":
    main()
'''.strip() + "\n", encoding="utf-8")

print("AI_MEDIA_LIVE_PROVIDER_EXECUTION_FOUNDATION_INSTALLED")
print(f"Created/updated: {live_provider_file}")
print(f"Updated: {bridge_file}")
print(f"Created: {test_file}")