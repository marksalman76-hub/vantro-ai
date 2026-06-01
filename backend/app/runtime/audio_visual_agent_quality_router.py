
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict

from backend.app.runtime.audio_visual_provider_stack import recommended_stack_for_task


AUDIO_VISUAL_AGENT_CAPABILITIES = {
    "ugc_creative_agent": {
        "quality_mode": "premium_ugc_campaign_runtime",
        "deliverable_types": [
            "storyboard",
            "shot_list",
            "creator_brief",
            "voiceover_script",
            "video_generation_prompt",
            "avatar_video_prompt",
            "paid_social_variants",
        ],
        "visual_preview_type": "ugc_campaign_board",
    },
    "website_landing_apps_agent": {
        "quality_mode": "premium_react_site_generation_runtime",
        "deliverable_types": [
            "react_route",
            "component_layout",
            "visual_direction",
            "asset_prompt_pack",
            "motion_spec",
            "preview_url",
        ],
        "visual_preview_type": "website_preview_packet",
    },
    "product_image_agent": {
        "quality_mode": "premium_product_visual_runtime",
        "deliverable_types": [
            "image_generation_prompt",
            "product_scene_brief",
            "lighting_direction",
            "camera_lens_spec",
            "style_variants",
        ],
        "visual_preview_type": "product_image_board",
    },
    "paid_ads_agent": {
        "quality_mode": "premium_ad_creative_runtime",
        "deliverable_types": [
            "ad_concepts",
            "visual_ad_prompts",
            "ugc_script_variants",
            "search_ads",
            "creative_testing_matrix",
        ],
        "visual_preview_type": "ad_campaign_board",
    },
}


def build_audio_visual_quality_plan(agent_id: str, task: str) -> Dict[str, Any]:
    capability = AUDIO_VISUAL_AGENT_CAPABILITIES.get(agent_id, {
        "quality_mode": "standard_text_deliverable_runtime",
        "deliverable_types": ["text_deliverable"],
        "visual_preview_type": "text_deliverable_preview",
    })

    stack = recommended_stack_for_task(agent_id, task)

    return {
        "success": True,
        "profile": "audio_visual_agent_quality_router_v1",
        "agent_id": agent_id,
        "task": task,
        "quality_mode": capability["quality_mode"],
        "deliverable_types": capability["deliverable_types"],
        "visual_preview_type": capability["visual_preview_type"],
        "recommended_provider_order": stack.get("recommended_order", []),
        "provider_status": stack.get("provider_status", {}),
        "live_external_calls_enabled": False,
        "credential_values_exposed": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
