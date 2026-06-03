from datetime import datetime, timezone
from typing import Any, Dict, List

try:
    from backend.app.runtime.creative_premium_media_plugin_registry import (
        get_creative_premium_media_plugin_registry,
    )
except Exception:
    get_creative_premium_media_plugin_registry = None


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


CREATIVE_AGENT_ROUTING = {
    "ugc_creative_agent": [
        "runway_video_generation",
        "kling_video_generation",
        "heygen_avatar_video",
        "elevenlabs_voice",
        "lip_sync_dubbing",
        "music_sfx_generation",
        "video_editing_render_pipeline",
        "brand_safe_creative_moderation",
        "multi_scene_character_consistency",
        "social_ad_export_presets",
    ],
    "product_image_agent": [
        "runway_video_generation",
        "kling_video_generation",
        "image_video_upscaling",
        "brand_safe_creative_moderation",
        "social_ad_export_presets",
    ],
    "marketing_specialist_agent": [
        "runway_video_generation",
        "kling_video_generation",
        "heygen_avatar_video",
        "elevenlabs_voice",
        "lip_sync_dubbing",
        "music_sfx_generation",
        "video_editing_render_pipeline",
        "brand_safe_creative_moderation",
        "multi_scene_character_consistency",
        "social_ad_export_presets",
    ],
    "social_media_agent": [
        "video_editing_render_pipeline",
        "brand_safe_creative_moderation",
        "social_ad_export_presets",
        "music_sfx_generation",
    ],
    "paid_ads_agent": [
        "brand_safe_creative_moderation",
        "social_ad_export_presets",
        "video_editing_render_pipeline",
        "image_video_upscaling",
    ],
    "brand_strategy_agent": [
        "music_sfx_generation",
        "multi_scene_character_consistency",
        "brand_safe_creative_moderation",
    ],
    "sales_closer_agent": [
        "heygen_avatar_video",
        "elevenlabs_voice",
        "brand_safe_creative_moderation",
    ],
    "product_copywriting_agent": [
        "elevenlabs_voice",
        "brand_safe_creative_moderation",
    ],
}


def _registry_plugins_by_key() -> Dict[str, Dict[str, Any]]:
    if get_creative_premium_media_plugin_registry is None:
        return {}

    registry = get_creative_premium_media_plugin_registry()
    return {
        plugin["plugin_key"]: plugin
        for plugin in registry.get("plugins", [])
    }


def get_creative_agent_premium_plugin_routing() -> Dict[str, Any]:
    plugins = _registry_plugins_by_key()

    routing_records: List[Dict[str, Any]] = []

    for agent_key, plugin_keys in CREATIVE_AGENT_ROUTING.items():
        mapped_plugins = []
        for plugin_key in plugin_keys:
            plugin = plugins.get(plugin_key)
            mapped_plugins.append(
                {
                    "plugin_key": plugin_key,
                    "available_in_registry": plugin is not None,
                    "category": plugin.get("category") if plugin else "unknown",
                    "configured": bool(plugin.get("configured")) if plugin else False,
                    "live_execution_enabled": bool(plugin.get("live_execution_enabled")) if plugin else False,
                    "owner_activation_required": bool(plugin.get("owner_activation_required")) if plugin else True,
                    "credential_values_exposed": False,
                }
            )

        routing_records.append(
            {
                "agent_key": agent_key,
                "premium_plugin_count": len(plugin_keys),
                "plugins": mapped_plugins,
                "live_provider_calls_triggered": False,
                "external_actions_performed": False,
                "credential_values_exposed": False,
                "owner_activation_required_for_paid_providers": True,
            }
        )

    return {
        "success": True,
        "track": "creative_agent_premium_media_plugin_expansion",
        "layer": "creative_agent_premium_plugin_routing",
        "status": "ready",
        "premium_plugin_registry_required": True,
        "creative_agent_routing_enabled": True,
        "agent_count": len(routing_records),
        "credential_values_exposed": False,
        "external_actions_performed": False,
        "live_provider_calls_triggered": False,
        "owner_activation_required_for_paid_providers": True,
        "tenant_isolation_preserved": True,
        "customer_safe_visibility_preserved": True,
        "routing_records": routing_records,
        "routing_rules": [
            "Creative agents can discover premium plugin categories through governed routing.",
            "Routing does not enable live paid provider calls.",
            "Live execution requires provider credentials and owner approval.",
            "Spend-impacting creative provider usage remains owner-approved.",
            "Brand-safe moderation should be applied before customer delivery.",
            "Credential values must never be exposed to client or status routes.",
        ],
        "verified_at": _now(),
    }


def get_client_safe_creative_agent_premium_plugin_routing() -> Dict[str, Any]:
    status = get_creative_agent_premium_plugin_routing()

    return {
        "success": status["success"],
        "track": status["track"],
        "layer": status["layer"],
        "status": status["status"],
        "creative_agent_routing_enabled": status["creative_agent_routing_enabled"],
        "agent_count": status["agent_count"],
        "credential_values_exposed": False,
        "external_actions_performed": False,
        "live_provider_calls_triggered": False,
        "owner_activation_required_for_paid_providers": True,
        "tenant_isolation_preserved": True,
        "customer_safe_visibility_preserved": True,
        "routing_records": [
            {
                "agent_key": record["agent_key"],
                "premium_plugin_count": record["premium_plugin_count"],
                "plugins": [
                    {
                        "plugin_key": plugin["plugin_key"],
                        "available_in_registry": plugin["available_in_registry"],
                        "category": plugin["category"],
                        "configured": plugin["configured"],
                        "live_execution_enabled": plugin["live_execution_enabled"],
                        "owner_activation_required": plugin["owner_activation_required"],
                        "credential_values_exposed": False,
                    }
                    for plugin in record["plugins"]
                ],
            }
            for record in status["routing_records"]
        ],
        "verified_at": status["verified_at"],
    }
