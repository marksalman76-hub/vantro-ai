
from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Dict, List

from app.runtime.creative_provider_routing import (
    creative_provider_status,
    normalize_creative_agent_id,
)
from app.runtime.creative_agent_capability_policy import AGENT_CREATIVE_MODEL_ACCESS


VIDEO_CREATIVE_AGENT_IDS = sorted(
    agent_id
    for agent_id, policy in AGENT_CREATIVE_MODEL_ACCESS.items()
    if policy.get("video")
)
IMAGE_CREATIVE_AGENT_IDS = sorted(
    agent_id
    for agent_id, policy in AGENT_CREATIVE_MODEL_ACCESS.items()
    if policy.get("image")
)


PROVIDER_STACK = {
    "openai": {
        "category": ["text", "image", "vision", "agent_reasoning"],
        "env_keys": ["OPENAI_API_KEY"],
        "agents": [
            "paid_ads_agent",
            "ugc_creative_agent",
            "product_image_agent",
            "website_landing_apps_agent",
            "marketing_specialist_agent",
            "seo_agent",
        ],
        "live_call_enabled_env": "OPENAI_LIVE_EXECUTION_ENABLED",
    },
    "runway": {
        "category": ["video", "image_to_video", "creative_motion"],
        "env_keys": ["RUNWAY_API_KEY"],
        "agents": ["ugc_creative_agent", "product_image_agent", "social_media_content_agent"],
        "live_call_enabled_env": "RUNWAY_LIVE_EXECUTION_ENABLED",
    },
    "kling": {
        "category": ["video", "image_to_video", "cinematic_motion"],
        "env_keys": ["KLING_API_KEY"],
        "agents": ["ugc_creative_agent", "product_image_agent", "social_media_content_agent"],
        "live_call_enabled_env": "KLING_LIVE_EXECUTION_ENABLED",
    },
    "heygen": {
        "category": ["avatar_video", "ugc_avatar", "voice_video"],
        "env_keys": ["HEYGEN_API_KEY"],
        "agents": ["ugc_creative_agent", "social_media_content_agent", "influencer_collaboration_agent"],
        "live_call_enabled_env": "HEYGEN_LIVE_EXECUTION_ENABLED",
    },
    "elevenlabs": {
        "category": ["voice", "audio", "voiceover"],
        "env_keys": ["ELEVENLABS_API_KEY"],
        "agents": ["ugc_creative_agent", "social_media_content_agent", "product_video_agent"],
        "live_call_enabled_env": "ELEVENLABS_LIVE_EXECUTION_ENABLED",
    },
    "replicate": {
        "category": ["image", "video", "model_router", "fallback_generation"],
        "env_keys": ["REPLICATE_API_TOKEN"],
        "agents": ["product_image_agent", "ugc_creative_agent", "website_landing_apps_agent"],
        "live_call_enabled_env": "REPLICATE_LIVE_EXECUTION_ENABLED",
    },
    "higgsfield": {
        "category": ["video", "text_to_video", "image_to_video", "creative_motion"],
        "env_keys": ["HIGGSFIELD_API_KEY"],
        "agents": VIDEO_CREATIVE_AGENT_IDS,
        "live_call_enabled_env": "HIGGSFIELD_LIVE_EXECUTION_ENABLED",
        "models": ["Kling 3.0 Turbo", "Kling 3.0", "Cinema Studio 4K"],
    },
    "nano_banana": {
        "category": ["image", "product_image", "ad_creative_image"],
        "env_keys": ["NANO_BANANA_API_KEY"],
        "agents": IMAGE_CREATIVE_AGENT_IDS,
        "live_call_enabled_env": "NANO_BANANA_LIVE_EXECUTION_ENABLED",
        "models": ["Nano Banana 2", "Nano Banana Pro"],
    },
}


def _truthy(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on", "enabled"}


class _RedactedStatusDict(dict):
    def __repr__(self) -> str:
        return self._redacted_repr()

    def __str__(self) -> str:
        return self._redacted_repr()

    def _redacted_repr(self) -> str:
        def redact(value: Any) -> Any:
            if isinstance(value, str) and "api_key" in value.lower():
                return "[redacted]"
            if isinstance(value, list):
                return [redact(item) for item in value]
            if isinstance(value, tuple):
                return tuple(redact(item) for item in value)
            if isinstance(value, dict):
                return {key: redact(item) for key, item in value.items()}
            return value

        return repr({key: redact(value) for key, value in self.items()})


def provider_config_status(provider_key: str) -> Dict[str, Any]:
    provider = PROVIDER_STACK.get(provider_key)
    if not provider:
        return {
            "success": False,
            "provider": provider_key,
            "status": "unknown_provider",
            "configured": False,
            "live_execution_enabled": False,
            "credential_values_exposed": False,
        }

    required_keys = provider["env_keys"]
    missing = [key for key in required_keys if not os.getenv(key)]
    configured = len(missing) == 0
    live_execution_enabled = configured and _truthy(os.getenv(provider["live_call_enabled_env"]))

    return _RedactedStatusDict({
        "success": True,
        "provider": provider_key,
        "category": provider["category"],
        "agents": provider["agents"],
        "models": provider.get("models", []),
        "required_env_keys": required_keys,
        "missing_env_keys": missing,
        "configured": configured,
        "live_execution_enabled": live_execution_enabled,
        "live_call_enabled_env": provider["live_call_enabled_env"],
        "credential_values_exposed": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
    })


def full_provider_stack_status() -> Dict[str, Any]:
    providers = {
        key: provider_config_status(key)
        for key in PROVIDER_STACK.keys()
    }

    return {
        "success": True,
        "profile": "audio_visual_provider_stack_v1",
        "provider_count": len(PROVIDER_STACK),
        "providers": providers,
        "creative_provider_routing": creative_provider_status(),
        "configured_count": sum(1 for p in providers.values() if p.get("configured")),
        "live_enabled_count": sum(1 for p in providers.values() if p.get("live_execution_enabled")),
        "global_live_calls_safe": False,
        "note": "Provider stack is installed. Live external calls remain disabled unless provider credentials and explicit live execution flags are configured.",
        "credential_values_exposed": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def providers_for_agent(agent_id: str) -> List[str]:
    canonical_agent_id = normalize_creative_agent_id(agent_id)
    return [
        key for key, provider in PROVIDER_STACK.items()
        if canonical_agent_id in provider.get("agents", [])
    ]


def recommended_stack_for_task(agent_id: str, task: str = "") -> Dict[str, Any]:
    task_lower = str(task or "").lower()
    candidates = providers_for_agent(agent_id)

    preferred = []
    if "voice" in task_lower or "voiceover" in task_lower or "audio" in task_lower:
        preferred.append("elevenlabs")
    if "avatar" in task_lower or "presenter" in task_lower:
        preferred.append("heygen")
    if "video" in task_lower or "ugc" in task_lower or "reel" in task_lower:
        preferred.extend(["higgsfield", "kling", "runway", "heygen"])
    if "image" in task_lower or "product photo" in task_lower or "visual" in task_lower:
        preferred.extend(["nano_banana", "openai", "replicate"])
    if "website" in task_lower or "landing page" in task_lower:
        preferred.extend(["openai", "replicate"])

    ordered = []
    for key in preferred + candidates:
        if key in candidates and key not in ordered:
            ordered.append(key)

    return {
        "success": True,
        "agent_id": agent_id,
        "task": task,
        "candidate_providers": candidates,
        "recommended_order": ordered,
        "provider_status": {key: provider_config_status(key) for key in ordered},
        "credential_values_exposed": False,
    }
