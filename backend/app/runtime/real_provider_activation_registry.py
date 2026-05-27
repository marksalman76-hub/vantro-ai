"""
Real Provider Activation Registry

Credential-safe provider activation layer for the unique multi-agent platform.

Rules:
- Never returns raw credentials.
- Detects provider readiness from environment variables only.
- Preserves owner-governed execution.
- Supports future async execution, polling, asset persistence, and failover routing.
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Dict, List


PROVIDER_DEFINITIONS: Dict[str, Dict[str, Any]] = {
    "openai": {
        "display_name": "OpenAI",
        "category": "llm_and_media",
        "required_env": ["OPENAI_API_KEY"],
        "optional_env": ["OPENAI_ORG_ID", "OPENAI_PROJECT_ID"],
        "capabilities": ["text", "vision", "image_generation", "agent_reasoning"],
        "supports_async": True,
        "supports_polling": True,
        "supports_asset_output": True,
    },
    "runway": {
        "display_name": "Runway",
        "category": "video_generation",
        "required_env": ["RUNWAY_API_KEY"],
        "optional_env": ["RUNWAY_API_BASE_URL"],
        "capabilities": ["video_generation", "image_to_video", "text_to_video"],
        "supports_async": True,
        "supports_polling": True,
        "supports_asset_output": True,
    },
    "kling": {
        "display_name": "Kling",
        "category": "video_generation",
        "required_env": ["KLING_API_KEY"],
        "optional_env": ["KLING_API_BASE_URL"],
        "capabilities": ["video_generation", "image_to_video", "text_to_video"],
        "supports_async": True,
        "supports_polling": True,
        "supports_asset_output": True,
    },
    "heygen": {
        "display_name": "HeyGen",
        "category": "avatar_video",
        "required_env": ["HEYGEN_API_KEY"],
        "optional_env": ["HEYGEN_API_BASE_URL"],
        "capabilities": ["avatar_video", "ugc_video", "voice_avatar"],
        "supports_async": True,
        "supports_polling": True,
        "supports_asset_output": True,
    },
    "elevenlabs": {
        "display_name": "ElevenLabs",
        "category": "voice_generation",
        "required_env": ["ELEVENLABS_API_KEY"],
        "optional_env": ["ELEVENLABS_API_BASE_URL"],
        "capabilities": ["voice_generation", "dubbing", "speech"],
        "supports_async": True,
        "supports_polling": True,
        "supports_asset_output": True,
    },
    "replicate": {
        "display_name": "Replicate",
        "category": "multi_model_generation",
        "required_env": ["REPLICATE_API_TOKEN"],
        "optional_env": ["REPLICATE_API_BASE_URL"],
        "capabilities": ["image_generation", "video_generation", "model_inference"],
        "supports_async": True,
        "supports_polling": True,
        "supports_asset_output": True,
    },
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _env_present(name: str) -> bool:
    value = os.getenv(name)
    return bool(value and value.strip())


def _masked_presence(name: str) -> Dict[str, Any]:
    return {
        "name": name,
        "configured": _env_present(name),
        "value_exposed": False,
    }


def get_provider_activation_status(provider_key: str) -> Dict[str, Any]:
    provider = PROVIDER_DEFINITIONS.get(provider_key)
    if not provider:
        return {
            "provider_key": provider_key,
            "known_provider": False,
            "configured": False,
            "ready": False,
            "error": "unknown_provider",
            "checked_at": _now_iso(),
        }

    required_env = provider.get("required_env", [])
    optional_env = provider.get("optional_env", [])

    required_status = [_masked_presence(name) for name in required_env]
    optional_status = [_masked_presence(name) for name in optional_env]

    missing_required = [
        item["name"] for item in required_status if not item["configured"]
    ]

    configured = len(missing_required) == 0

    return {
        "provider_key": provider_key,
        "display_name": provider["display_name"],
        "known_provider": True,
        "category": provider["category"],
        "configured": configured,
        "ready": configured,
        "missing_required_env": missing_required,
        "required_env": required_status,
        "optional_env": optional_status,
        "capabilities": provider["capabilities"],
        "supports_async": provider["supports_async"],
        "supports_polling": provider["supports_polling"],
        "supports_asset_output": provider["supports_asset_output"],
        "credential_values_exposed": False,
        "owner_governed_execution_required": True,
        "checked_at": _now_iso(),
    }


def get_all_provider_activation_statuses() -> Dict[str, Any]:
    providers = [
        get_provider_activation_status(provider_key)
        for provider_key in PROVIDER_DEFINITIONS.keys()
    ]

    configured = [p for p in providers if p.get("configured")]
    unconfigured = [p for p in providers if not p.get("configured")]

    return {
        "status": "ok",
        "activation_registry": "real_provider_activation_registry_v1",
        "configured_provider_count": len(configured),
        "unconfigured_provider_count": len(unconfigured),
        "total_provider_count": len(providers),
        "configured_providers": [p["provider_key"] for p in configured],
        "unconfigured_providers": [p["provider_key"] for p in unconfigured],
        "providers": providers,
        "credential_values_exposed": False,
        "owner_governed_execution_required": True,
        "async_execution_ready_for_next_layer": True,
        "checked_at": _now_iso(),
    }


def select_ready_provider_for_capability(capability: str) -> Dict[str, Any]:
    statuses = get_all_provider_activation_statuses()["providers"]
    matching = [
        provider for provider in statuses
        if provider.get("ready") and capability in provider.get("capabilities", [])
    ]

    if not matching:
        return {
            "selected": False,
            "capability": capability,
            "provider_key": None,
            "reason": "no_configured_provider_for_capability",
            "owner_governed_execution_required": True,
            "credential_values_exposed": False,
            "checked_at": _now_iso(),
        }

    selected = matching[0]

    return {
        "selected": True,
        "capability": capability,
        "provider_key": selected["provider_key"],
        "display_name": selected["display_name"],
        "supports_async": selected["supports_async"],
        "supports_polling": selected["supports_polling"],
        "supports_asset_output": selected["supports_asset_output"],
        "owner_governed_execution_required": True,
        "credential_values_exposed": False,
        "checked_at": _now_iso(),
    }
