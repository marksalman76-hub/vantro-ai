from datetime import datetime, timezone
from typing import Any, Dict, List
import os


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


PROVIDERS = [
    {
        "provider_key": "runway",
        "credential_envs": ["RUNWAY_API_KEY"],
        "category": "video_generation",
    },
    {
        "provider_key": "kling",
        "credential_envs": ["KLING_API_KEY"],
        "category": "video_generation",
    },
    {
        "provider_key": "heygen",
        "credential_envs": ["HEYGEN_API_KEY"],
        "category": "avatar_video",
    },
    {
        "provider_key": "elevenlabs",
        "credential_envs": ["ELEVENLABS_API_KEY"],
        "category": "voice_generation",
    },
    {
        "provider_key": "lipsync_dubbing",
        "credential_envs": ["LIPSYNC_API_KEY"],
        "category": "dubbing_lipsync",
    },
    {
        "provider_key": "music_sfx",
        "credential_envs": ["MUSIC_SFX_API_KEY"],
        "category": "audio_generation",
    },
    {
        "provider_key": "upscaling",
        "credential_envs": ["UPSCALE_API_KEY"],
        "category": "enhancement",
    },
]


def _provider_status(provider: Dict[str, Any]) -> Dict[str, Any]:
    credential_present = any(
        bool(os.getenv(env_name, "").strip())
        for env_name in provider["credential_envs"]
    )

    return {
        "provider_key": provider["provider_key"],
        "category": provider["category"],
        "credential_configured": credential_present,
        "credential_values_exposed": False,
        "live_execution_enabled": False,
        "owner_activation_required": True,
        "provider_ready_for_activation": credential_present,
        "external_actions_performed": False,
        "live_provider_calls_triggered": False,
    }


def get_creative_provider_credential_activation_checks() -> Dict[str, Any]:
    provider_statuses = [_provider_status(provider) for provider in PROVIDERS]

    configured_count = len([
        provider for provider in provider_statuses
        if provider["credential_configured"]
    ])

    return {
        "success": True,
        "track": "creative_agent_premium_media_plugin_expansion",
        "layer": "provider_credential_activation_checks",
        "status": "ready",
        "provider_count": len(provider_statuses),
        "configured_provider_count": configured_count,
        "credential_values_exposed": False,
        "external_actions_performed": False,
        "live_provider_calls_triggered": False,
        "live_execution_globally_enabled": False,
        "owner_activation_required_for_paid_providers": True,
        "tenant_isolation_preserved": True,
        "customer_safe_visibility_preserved": True,
        "providers": provider_statuses,
        "activation_rules": [
            "Credential presence does not automatically enable live execution.",
            "Live execution requires explicit owner activation.",
            "Credential values must never be exposed.",
            "Paid provider usage remains owner-approved.",
            "Provider calls must remain governed and auditable.",
            "Tenant isolation and customer-safe visibility must remain preserved.",
        ],
        "verified_at": _now(),
    }


def get_client_safe_creative_provider_credential_activation_checks() -> Dict[str, Any]:
    status = get_creative_provider_credential_activation_checks()

    return {
        "success": status["success"],
        "track": status["track"],
        "layer": status["layer"],
        "status": status["status"],
        "provider_count": status["provider_count"],
        "configured_provider_count": status["configured_provider_count"],
        "credential_values_exposed": False,
        "external_actions_performed": False,
        "live_provider_calls_triggered": False,
        "live_execution_globally_enabled": False,
        "owner_activation_required_for_paid_providers": True,
        "tenant_isolation_preserved": True,
        "customer_safe_visibility_preserved": True,
        "providers": [
            {
                "provider_key": provider["provider_key"],
                "category": provider["category"],
                "credential_configured": provider["credential_configured"],
                "provider_ready_for_activation": provider["provider_ready_for_activation"],
                "live_execution_enabled": provider["live_execution_enabled"],
                "owner_activation_required": provider["owner_activation_required"],
                "credential_values_exposed": False,
            }
            for provider in status["providers"]
        ],
        "verified_at": status["verified_at"],
    }
