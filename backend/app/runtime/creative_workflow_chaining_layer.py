from datetime import datetime, timezone
from typing import Any, Dict, List


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


WORKFLOW_TEMPLATES = {
    "premium_voiceover_ad": [
        "script_generation",
        "elevenlabs_voiceover",
        "runway_or_kling_visual_generation",
        "export_preset_formatting",
        "quality_scoring",
    ],
    "realistic_ugc_ad": [
        "brief_analysis",
        "script_generation",
        "elevenlabs_creator_voice",
        "kling_social_video_generation",
        "brand_safe_review",
        "export_preset_formatting",
        "quality_scoring",
    ],
    "cinematic_commercial": [
        "brief_analysis",
        "script_generation",
        "elevenlabs_narration",
        "runway_cinematic_generation",
        "optional_kling_alternative_generation",
        "quality_scoring",
        "best_output_selection",
        "export_preset_formatting",
    ],
    "avatar_spokesperson_video": [
        "brief_analysis",
        "script_generation",
        "elevenlabs_voiceover",
        "heygen_avatar_generation",
        "optional_sync_lipsync_refinement",
        "brand_safe_review",
        "export_preset_formatting",
        "quality_scoring",
    ],
    "multilingual_localised_campaign": [
        "brief_analysis",
        "script_generation",
        "language_localisation",
        "elevenlabs_multilingual_voice",
        "heygen_or_kling_video_generation",
        "sync_dubbing_lipsync",
        "regional_quality_review",
        "export_preset_formatting",
        "quality_scoring",
    ],
}


def create_creative_workflow_chain(
    workflow_goal: str,
    target_platform: str = "general",
    language: str = "English",
    region: str = "",
    quality_priority: str = "high",
    owner_approved_live_execution: bool = False,
) -> Dict[str, Any]:
    goal = (workflow_goal or "").lower()

    if "avatar" in goal or "spokesperson" in goal or "presenter" in goal:
        template_key = "avatar_spokesperson_video"
    elif "multilingual" in goal or "localised" in goal or "localized" in goal or language.lower() != "english":
        template_key = "multilingual_localised_campaign"
    elif "ugc" in goal or "tiktok" in goal or "reels" in goal or "social" in goal:
        template_key = "realistic_ugc_ad"
    elif "cinematic" in goal or "commercial" in goal or "luxury" in goal:
        template_key = "cinematic_commercial"
    else:
        template_key = "premium_voiceover_ad"

    steps = WORKFLOW_TEMPLATES[template_key]

    return {
        "success": True,
        "layer": "creative_workflow_chaining_layer",
        "status": "workflow_chain_created",
        "workflow_goal": workflow_goal,
        "selected_template": template_key,
        "target_platform": target_platform,
        "language": language,
        "region": region,
        "quality_priority": quality_priority,
        "workflow_steps": steps,
        "workflow_step_count": len(steps),
        "hardcoded_single_provider_path": False,
        "multi_provider_chaining_enabled": True,
        "owner_approval_required_for_live_execution": not owner_approved_live_execution,
        "execution_allowed": bool(owner_approved_live_execution),
        "credential_values_exposed": False,
        "external_actions_performed": False,
        "live_provider_calls_triggered": False,
        "chain_rules": [
            "Create execution plans before live provider calls.",
            "Use only providers needed for the workflow goal.",
            "Live provider execution requires owner approval.",
            "Provider outputs should feed into quality scoring.",
            "Approved/rejected outputs should feed governed learning memory.",
            "Credentials must never be exposed.",
            "Tenant isolation must remain preserved.",
        ],
        "created_at": _now(),
    }


def get_creative_workflow_chaining_status() -> Dict[str, Any]:
    return {
        "success": True,
        "layer": "creative_workflow_chaining_layer",
        "status": "ready",
        "multi_provider_chaining_enabled": True,
        "workflow_template_count": len(WORKFLOW_TEMPLATES),
        "workflow_templates": WORKFLOW_TEMPLATES,
        "hardcoded_single_provider_path": False,
        "owner_approval_required_for_live_execution": True,
        "credential_values_exposed": False,
        "external_actions_performed": False,
        "live_provider_calls_triggered": False,
        "supported_chains": list(WORKFLOW_TEMPLATES.keys()),
        "verified_at": _now(),
    }
