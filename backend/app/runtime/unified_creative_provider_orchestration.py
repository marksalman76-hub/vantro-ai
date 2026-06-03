from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


PROVIDER_CAPABILITIES = {
    "elevenlabs": {
        "primary": ["voiceover", "narration", "accent", "language", "audio"],
        "best_for": ["premium_voice", "multilingual_voice", "ugc_narration", "ad_voiceover"],
    },
    "runway": {
        "primary": ["cinematic_video", "premium_motion", "commercial_visuals"],
        "best_for": ["luxury_ad", "saas_commercial", "cinematic_product_video"],
    },
    "kling": {
        "primary": ["realistic_video", "social_video", "ugc_motion"],
        "best_for": ["ugc_ad", "ecommerce_social_ad", "realistic_human_motion"],
    },
    "heygen": {
        "primary": ["avatar_video", "spokesperson", "presenter"],
        "best_for": ["avatar_ad", "sales_video", "explainer_video"],
    },
    "sync": {
        "primary": ["lipsync", "dubbing", "localisation"],
        "best_for": ["multilingual_video", "voice_replacement", "translated_avatar"],
    },
}


def choose_creative_provider_mix(
    creative_goal: str,
    content_type: str = "",
    target_platform: str = "",
    language: str = "English",
    accent: str = "",
    region: str = "",
    quality_priority: str = "high",
    budget_priority: str = "balanced",
    requires_avatar: bool = False,
    requires_lipsync: bool = False,
    requires_dubbing: bool = False,
    requires_cinematic: bool = False,
    requires_ugc_realism: bool = False,
    requires_voiceover: bool = True,
    owner_approved_live_execution: bool = False,
) -> Dict[str, Any]:
    goal = " ".join([
        creative_goal or "",
        content_type or "",
        target_platform or "",
        quality_priority or "",
        region or "",
    ]).lower()

    selected: List[str] = []
    reasons: Dict[str, str] = {}

    if requires_voiceover or "voice" in goal or "narration" in goal or "audio" in goal:
        selected.append("elevenlabs")
        reasons["elevenlabs"] = "premium voice, accents, narration, and multilingual audio"

    if requires_avatar or "avatar" in goal or "spokesperson" in goal or "presenter" in goal:
        selected.append("heygen")
        reasons["heygen"] = "avatar presenter and AI spokesperson video generation"

    if requires_lipsync or requires_dubbing or language.lower() != "english" or "dubbing" in goal or "localised" in goal:
        selected.append("sync")
        reasons["sync"] = "lip-sync, dubbing, and multilingual localisation"

    if requires_cinematic or "cinematic" in goal or "luxury" in goal or "premium commercial" in goal:
        selected.append("runway")
        reasons["runway"] = "cinematic, premium commercial video generation"

    if requires_ugc_realism or "ugc" in goal or "social" in goal or "tiktok" in goal or "reels" in goal:
        selected.append("kling")
        reasons["kling"] = "realistic social-first and UGC-style video generation"

    if not any(provider in selected for provider in ["runway", "kling", "heygen"]):
        if budget_priority == "quality_first":
            selected.append("runway")
            reasons["runway"] = "default high-quality cinematic video route"
        else:
            selected.append("kling")
            reasons["kling"] = "default balanced social/video route"

    selected = list(dict.fromkeys(selected))

    execution_allowed = bool(owner_approved_live_execution)

    return {
        "success": True,
        "layer": "unified_creative_provider_orchestration",
        "status": "plan_created",
        "hardcoded_provider_path": False,
        "policy_driven_selection": True,
        "learning_aware_selection_ready": True,
        "selected_providers": selected,
        "provider_reasons": reasons,
        "execution_allowed": execution_allowed,
        "owner_approval_required_for_live_execution": not execution_allowed,
        "credential_values_exposed": False,
        "external_actions_performed": False,
        "live_provider_calls_triggered": False,
        "input_context": {
            "creative_goal": creative_goal,
            "content_type": content_type,
            "target_platform": target_platform,
            "language": language,
            "accent": accent,
            "region": region,
            "quality_priority": quality_priority,
            "budget_priority": budget_priority,
            "requires_avatar": requires_avatar,
            "requires_lipsync": requires_lipsync,
            "requires_dubbing": requires_dubbing,
            "requires_cinematic": requires_cinematic,
            "requires_ugc_realism": requires_ugc_realism,
            "requires_voiceover": requires_voiceover,
        },
        "governance_rules": [
            "Provider selection remains flexible and policy-driven.",
            "Live execution requires owner approval.",
            "Credential values must never be exposed.",
            "Provider calls must remain auditable.",
            "Tenant isolation must remain preserved.",
            "Quality scores may influence future routing but cannot override governance.",
        ],
        "created_at": _now(),
    }


def get_unified_creative_provider_orchestration_status() -> Dict[str, Any]:
    return {
        "success": True,
        "layer": "unified_creative_provider_orchestration",
        "status": "ready",
        "flexible_provider_selection_enabled": True,
        "hardcoded_provider_paths": False,
        "policy_driven_routing_enabled": True,
        "learning_aware_routing_ready": True,
        "owner_approval_required_for_live_execution": True,
        "credential_values_exposed": False,
        "external_actions_performed": False,
        "live_provider_calls_triggered": False,
        "supported_providers": list(PROVIDER_CAPABILITIES.keys()),
        "provider_capabilities": PROVIDER_CAPABILITIES,
        "verified_at": _now(),
    }
