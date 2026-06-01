from pathlib import Path
from datetime import datetime
import shutil
import json

ROOT = Path.cwd()
RUNTIME_DIR = ROOT / "backend" / "app" / "runtime"
TARGET = RUNTIME_DIR / "audio_visual_provider_stack.py"
TEST = ROOT / "test_audio_visual_provider_stack.py"

BACKUP = ROOT / "backups" / f"audio_visual_provider_stack_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
BACKUP.mkdir(parents=True, exist_ok=True)

if TARGET.exists():
    shutil.copy2(TARGET, BACKUP / TARGET.name)

RUNTIME_DIR.mkdir(parents=True, exist_ok=True)

TARGET.write_text(r'''
from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Dict, List


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
}


def _truthy(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on", "enabled"}


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

    return {
        "success": True,
        "provider": provider_key,
        "category": provider["category"],
        "agents": provider["agents"],
        "required_env_keys": required_keys,
        "missing_env_keys": missing,
        "configured": configured,
        "live_execution_enabled": live_execution_enabled,
        "live_call_enabled_env": provider["live_call_enabled_env"],
        "credential_values_exposed": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


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
        "configured_count": sum(1 for p in providers.values() if p.get("configured")),
        "live_enabled_count": sum(1 for p in providers.values() if p.get("live_execution_enabled")),
        "global_live_calls_safe": False,
        "note": "Provider stack is installed. Live external calls remain disabled unless provider credentials and explicit live execution flags are configured.",
        "credential_values_exposed": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def providers_for_agent(agent_id: str) -> List[str]:
    return [
        key for key, provider in PROVIDER_STACK.items()
        if agent_id in provider.get("agents", [])
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
        preferred.extend(["runway", "kling", "heygen"])
    if "image" in task_lower or "product photo" in task_lower or "visual" in task_lower:
        preferred.extend(["openai", "replicate"])
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
''', encoding="utf-8")

TEST.write_text(r'''
from backend.app.runtime.audio_visual_provider_stack import (
    full_provider_stack_status,
    provider_config_status,
    providers_for_agent,
    recommended_stack_for_task,
)

status = full_provider_stack_status()

assert status["success"] is True
assert status["provider_count"] == 6
assert status["credential_values_exposed"] is False

for key in ["openai", "runway", "kling", "heygen", "elevenlabs", "replicate"]:
    provider = provider_config_status(key)
    assert provider["success"] is True
    assert provider["credential_values_exposed"] is False
    assert "required_env_keys" in provider

assert "runway" in providers_for_agent("ugc_creative_agent")
assert "elevenlabs" in providers_for_agent("ugc_creative_agent")
assert "openai" in providers_for_agent("product_image_agent")

recommendation = recommended_stack_for_task(
    "ugc_creative_agent",
    "Create UGC video with avatar and voiceover"
)

assert "heygen" in recommendation["recommended_order"]
assert "elevenlabs" in recommendation["recommended_order"]

print("AUDIO_VISUAL_PROVIDER_STACK_TEST_PASSED")
print(status)
''', encoding="utf-8")

print("AUDIO_VISUAL_PROVIDER_STACK_INSTALLED")
print("Runtime:", TARGET)
print("Test:", TEST)
print("Backup:", BACKUP)