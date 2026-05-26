from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


MEDIA_RELEVANT_AGENTS = {
    "ugc_video_agent",
    "product_image_agent",
    "ad_creative_agent",
    "social_media_manager_agent",
    "content_creator_agent",
    "marketing_specialist_agent",
    "ecommerce_agent",
    "influencer_outreach_agent",
    "product_development_agent",
    "head_agent",
    "orchestration_agent",
}


CINEMATIC_STYLE_PRESETS = {
    "premium_ugc": {
        "style": "premium handheld UGC",
        "camera_language": "natural phone-style movement with controlled polish",
        "lighting": "soft natural commercial lighting",
        "pacing": "fast hook, clear product reveal, confident CTA",
        "best_for": ["ugc_video_agent", "social_media_manager_agent", "marketing_specialist_agent"],
    },
    "cinematic_luxury": {
        "style": "cinematic luxury ecommerce",
        "camera_language": "slow controlled motion, macro close-ups, elegant transitions",
        "lighting": "high-end studio lighting with depth and contrast",
        "pacing": "aspirational opening, sensory product details, refined CTA",
        "best_for": ["product_image_agent", "ad_creative_agent", "ecommerce_agent"],
    },
    "direct_response": {
        "style": "conversion-focused direct response",
        "camera_language": "clear demonstration angles and benefit-led cuts",
        "lighting": "bright, clean, trust-building ecommerce lighting",
        "pacing": "problem, proof, benefit, urgency, CTA",
        "best_for": ["marketing_specialist_agent", "ad_creative_agent", "ecommerce_agent"],
    },
    "creator_collab": {
        "style": "authentic influencer collaboration",
        "camera_language": "creator-native framing and lifestyle context",
        "lighting": "realistic social-native lighting",
        "pacing": "personal intro, usage moment, honest reaction, CTA",
        "best_for": ["influencer_outreach_agent", "ugc_video_agent", "content_creator_agent"],
    },
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_text(value: Any, fallback: str = "") -> str:
    if value is None:
        return fallback
    return str(value).strip() or fallback


def is_ai_media_relevant_agent(agent_id: str) -> bool:
    return _safe_text(agent_id).lower() in MEDIA_RELEVANT_AGENTS


def select_style_preset(agent_id: str, objective: str = "", platform: str = "") -> Dict[str, Any]:
    agent = _safe_text(agent_id).lower()
    objective_l = _safe_text(objective).lower()
    platform_l = _safe_text(platform).lower()

    if "luxury" in objective_l or "premium" in objective_l or agent == "product_image_agent":
        return CINEMATIC_STYLE_PRESETS["cinematic_luxury"]

    if "conversion" in objective_l or "sales" in objective_l or "meta" in platform_l:
        return CINEMATIC_STYLE_PRESETS["direct_response"]

    if agent == "influencer_outreach_agent" or "creator" in objective_l:
        return CINEMATIC_STYLE_PRESETS["creator_collab"]

    return CINEMATIC_STYLE_PRESETS["premium_ugc"]


def build_hook_strategy(objective: str, product: str, audience: str) -> Dict[str, Any]:
    objective_l = _safe_text(objective).lower()

    if "problem" in objective_l or "pain" in objective_l:
        hook_type = "pain-point hook"
        hook_direction = f"Open by naming the buyer problem before introducing {product} as the clean solution."
    elif "luxury" in objective_l or "premium" in objective_l:
        hook_type = "aspirational hook"
        hook_direction = f"Open with the desired lifestyle outcome and position {product} as the premium choice."
    elif "urgent" in objective_l or "sale" in objective_l:
        hook_type = "urgency hook"
        hook_direction = f"Open with a time-sensitive reason to pay attention before showing {product}."
    else:
        hook_type = "curiosity hook"
        hook_direction = f"Open with a visual or spoken claim that makes {audience} want to see what {product} does."

    return {
        "hook_type": hook_type,
        "hook_direction": hook_direction,
        "scroll_stop_standard": "First 1.5 seconds must create visual or verbal interruption without feeling fake.",
    }


def build_scene_plan(product: str, objective: str, platform: str) -> List[Dict[str, Any]]:
    platform_l = _safe_text(platform).lower()
    short_form = any(x in platform_l for x in ["tiktok", "reels", "shorts", "meta", "instagram"])

    if short_form:
        return [
            {"scene": 1, "purpose": "hook", "duration_seconds": "0-2", "direction": "Open with strong face/product framing and immediate benefit cue."},
            {"scene": 2, "purpose": "product reveal", "duration_seconds": "2-5", "direction": f"Show {product} clearly with no visual clutter."},
            {"scene": 3, "purpose": "proof/demo", "duration_seconds": "5-10", "direction": "Show usage, texture, transformation, result, or proof moment."},
            {"scene": 4, "purpose": "benefit stack", "duration_seconds": "10-15", "direction": "Highlight 2-3 strongest buying reasons quickly."},
            {"scene": 5, "purpose": "CTA", "duration_seconds": "15-20", "direction": "End with clear action and confident brand-safe closing."},
        ]

    return [
        {"scene": 1, "purpose": "brand opening", "duration_seconds": "0-3", "direction": "Establish premium visual world and customer desire."},
        {"scene": 2, "purpose": "product hero", "duration_seconds": "3-8", "direction": f"Present {product} as the central hero with controlled cinematic framing."},
        {"scene": 3, "purpose": "feature proof", "duration_seconds": "8-16", "direction": "Show key feature, use case, or differentiator."},
        {"scene": 4, "purpose": "commercial close", "duration_seconds": "16-25", "direction": "Resolve with offer, trust cue, and CTA."},
    ]


def build_provider_strategy(agent_id: str, media_type: str, quality_target: str = "premium") -> Dict[str, Any]:
    media_type_l = _safe_text(media_type).lower()

    if "video" in media_type_l or "ugc" in media_type_l:
        primary = "video_generation_provider"
        fallback = ["cinematic_video_provider", "ugc_avatar_provider", "generic_video_provider"]
    elif "image" in media_type_l or "product" in media_type_l:
        primary = "image_generation_provider"
        fallback = ["product_photography_provider", "lifestyle_image_provider", "generic_image_provider"]
    elif "voice" in media_type_l or "dub" in media_type_l:
        primary = "voice_dubbing_provider"
        fallback = ["multilingual_voice_provider", "generic_voice_provider"]
    else:
        primary = "multi_modal_generation_provider"
        fallback = ["video_generation_provider", "image_generation_provider", "generic_generation_provider"]

    return {
        "primary_provider_slot": primary,
        "fallback_provider_slots": fallback,
        "execution_mode": "orchestration_first",
        "quality_target": quality_target,
        "fallback_required": True,
        "manual_review_if_all_providers_fail": True,
    }



def score_ai_media_orchestration(orchestration_packet: Dict[str, Any]) -> Dict[str, Any]:
    quality_rules = orchestration_packet.get("quality_rules", {})
    provider_strategy = orchestration_packet.get("provider_strategy", {})
    scene_plan = orchestration_packet.get("scene_plan", [])
    cinematic_direction = orchestration_packet.get("cinematic_direction", {})
    hook_strategy = orchestration_packet.get("hook_strategy", {})

    scores = {
        "brand_fit": 90 if orchestration_packet.get("brand") else 72,
        "cinematic_quality": 92 if cinematic_direction.get("camera_language") and cinematic_direction.get("lighting") else 70,
        "ecommerce_conversion_strength": 91 if hook_strategy.get("hook_direction") and len(scene_plan) >= 4 else 68,
        "character_consistency_readiness": 90 if quality_rules.get("same_character_consistency_required_when_character_present") else 65,
        "provider_fallback_readiness": 94 if provider_strategy.get("fallback_required") and provider_strategy.get("fallback_provider_slots") else 60,
        "multilingual_readiness": 88 if quality_rules.get("multilingual_adaptation_supported") else 62,
        "premium_output_readiness": 95 if quality_rules.get("premium_only") and quality_rules.get("no_placeholder_outputs") else 58,
    }

    overall_score = round(sum(scores.values()) / len(scores), 2)

    if overall_score >= 90:
        readiness_level = "premium_ready"
    elif overall_score >= 80:
        readiness_level = "ready_with_minor_review"
    elif overall_score >= 70:
        readiness_level = "manual_review_recommended"
    else:
        readiness_level = "not_ready_for_provider_execution"

    return {
        "overall_score": overall_score,
        "readiness_level": readiness_level,
        "scores": scores,
        "provider_execution_allowed": overall_score >= 80,
        "manual_review_required": overall_score < 80,
        "recommendations": [
            "Preserve brand and character consistency before provider execution.",
            "Use fallback provider strategy for failed or low-quality provider results.",
            "Reject placeholder/basic media prompts before generation.",
            "Keep ecommerce conversion objective visible in hook, scene flow, and CTA.",
        ],
    }

def run_shared_ai_media_creative_director(payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    payload = payload or {}

    agent_id = _safe_text(payload.get("agent_id"), "orchestration_agent").lower()
    product = _safe_text(payload.get("product_name") or payload.get("product"), "the product")
    brand = _safe_text(payload.get("brand_name") or payload.get("brand"), "the brand")
    audience = _safe_text(payload.get("target_audience"), "the target buyer")
    objective = _safe_text(payload.get("objective") or payload.get("campaign_goal"), "premium ecommerce media generation")
    platform = _safe_text(payload.get("platform"), "short-form social")
    media_type = _safe_text(payload.get("media_type"), "ugc video")
    language = _safe_text(payload.get("language"), "English")
    region = _safe_text(payload.get("region") or payload.get("country"), "global")

    relevant = is_ai_media_relevant_agent(agent_id)
    style = select_style_preset(agent_id, objective, platform)
    hook = build_hook_strategy(objective, product, audience)
    scenes = build_scene_plan(product, objective, platform)
    provider_strategy = build_provider_strategy(agent_id, media_type)

    orchestration_packet = {
        "runtime": "shared_ai_media_creative_director",
        "version": "1.0.0",
        "generated_at": _utc_now(),
        "agent_id": agent_id,
        "available_to_relevant_agents": True,
        "agent_is_media_relevant": relevant,
        "brand": brand,
        "product": product,
        "target_audience": audience,
        "objective": objective,
        "platform": platform,
        "media_type": media_type,
        "language": language,
        "region": region,
        "cinematic_direction": style,
        "hook_strategy": hook,
        "scene_plan": scenes,
        "provider_strategy": provider_strategy,
        "quality_rules": {
            "premium_only": True,
            "no_placeholder_outputs": True,
            "brand_consistency_required": True,
            "same_character_consistency_required_when_character_present": True,
            "multilingual_adaptation_supported": True,
            "ecommerce_conversion_focus_required": True,
            "manual_review_for_low_confidence": True,
        },
        "adapter_ready_payload": {
            "creative_brief": f"{brand} {product} campaign for {audience}",
            "shot_count": len(scenes),
            "style": style.get("style"),
            "camera_language": style.get("camera_language"),
            "lighting": style.get("lighting"),
            "pacing": style.get("pacing"),
            "hook": hook.get("hook_direction"),
            "scenes": scenes,
            "language": language,
            "region": region,
            "provider_strategy": provider_strategy,
        },
    }


    orchestration_packet["orchestration_score"] = score_ai_media_orchestration(orchestration_packet)

    orchestration_packet["provider_fallback_execution_plan"] = build_provider_fallback_execution_plan(orchestration_packet)


    return {
        "success": True,
        "status": "shared_ai_media_creative_director_ready",
        "scope": "platform_wide_reusable_capability",
        "available_agents": sorted(MEDIA_RELEVANT_AGENTS),
        "orchestration_packet": orchestration_packet,
    }



def build_provider_fallback_execution_plan(orchestration_packet: Dict[str, Any]) -> Dict[str, Any]:
    provider_strategy = orchestration_packet.get("provider_strategy", {})
    orchestration_score = orchestration_packet.get("orchestration_score", {})
    adapter_payload = orchestration_packet.get("adapter_ready_payload", {})

    primary_provider = provider_strategy.get("primary_provider_slot", "multi_modal_generation_provider")
    fallback_providers = provider_strategy.get("fallback_provider_slots", [])

    fallback_steps = []

    fallback_steps.append({
        "step": 1,
        "provider_slot": primary_provider,
        "execution_role": "primary_generation_attempt",
        "allowed": orchestration_score.get("provider_execution_allowed", True),
        "failure_triggers": [
            "provider_timeout",
            "provider_error",
            "low_quality_result",
            "brand_mismatch",
            "character_inconsistency",
            "policy_or_safety_rejection",
        ],
    })

    for index, fallback_provider in enumerate(fallback_providers, start=2):
        fallback_steps.append({
            "step": index,
            "provider_slot": fallback_provider,
            "execution_role": "fallback_generation_attempt",
            "allowed": True,
            "inherits_payload": True,
            "payload_adjustment": "preserve creative direction, simplify provider-specific execution constraints if needed",
            "failure_triggers": [
                "provider_timeout",
                "provider_error",
                "low_quality_result",
                "brand_mismatch",
                "character_inconsistency",
            ],
        })

    fallback_steps.append({
        "step": len(fallback_steps) + 1,
        "provider_slot": "manual_review_queue",
        "execution_role": "human_review_or_owner_review",
        "allowed": True,
        "trigger": "all_provider_attempts_failed_or_quality_score_below_threshold",
        "required_action": "review creative brief, provider payload, quality issues, and retry recommendation",
    })

    return {
        "fallback_enabled": True,
        "execution_mode": "primary_then_fallback_provider_chain",
        "primary_provider_slot": primary_provider,
        "fallback_provider_slots": fallback_providers,
        "manual_review_final_step": True,
        "quality_threshold": 80,
        "score_at_plan_time": orchestration_score.get("overall_score"),
        "adapter_payload_present": bool(adapter_payload),
        "fallback_steps": fallback_steps,
        "rules": {
            "preserve_brand_memory": True,
            "preserve_character_consistency": True,
            "preserve_cinematic_direction": True,
            "preserve_ecommerce_objective": True,
            "do_not_publish_without_governance": True,
            "owner_review_required_for_spend_or_campaign_scaling": True,
        },
    }

def readiness() -> Dict[str, Any]:
    return {
        "success": True,
        "runtime": "shared_ai_media_creative_director",
        "status": "ready",
        "scope": "platform_wide_reusable_capability",
        "available_to_relevant_agents": True,
        "relevant_agent_count": len(MEDIA_RELEVANT_AGENTS),
        "available_agents": sorted(MEDIA_RELEVANT_AGENTS),
        "capabilities": [
            "cinematic_style_selection",
            "hook_strategy",
            "scene_planning",
            "brand_consistency_direction",
            "same_character_consistency_rules",
            "multilingual_adaptation_rules",
            "provider_strategy",
            "fallback_strategy",
            "adapter_ready_payload_generation",
            "premium_ecommerce_quality_rules",
        ],
    }
