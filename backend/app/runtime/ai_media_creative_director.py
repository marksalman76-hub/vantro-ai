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




CINEMATIC_PARAMETER_PRESETS = {
    "premium_ugc_video": {
        "aspect_ratios": ["9:16", "4:5", "1:1"],
        "camera_motion": "natural handheld with stable face/product framing",
        "shot_types": ["creator close-up", "product reveal", "usage demo", "reaction shot", "CTA frame"],
        "lens_language": "smartphone-realistic with premium polish",
        "lighting_style": "soft natural key light, realistic home or lifestyle setting",
        "motion_intensity": "medium",
        "cutting_pace": "fast first 3 seconds, then controlled benefit-led cuts",
        "voice_direction": "natural creator voice, confident, conversational",
        "subtitle_style": "large readable social captions with emphasis words",
        "best_for": ["ugc_video_agent", "social_media_manager_agent", "content_creator_agent"],
    },
    "product_photography": {
        "aspect_ratios": ["1:1", "4:5", "16:9"],
        "camera_motion": "static or slow slider-style product movement",
        "shot_types": ["hero product", "macro detail", "texture close-up", "lifestyle placement", "packaging shot"],
        "lens_language": "premium ecommerce studio photography",
        "lighting_style": "clean studio lighting with controlled shadows",
        "motion_intensity": "low",
        "cutting_pace": "slow and polished",
        "voice_direction": "optional, minimal, product-led",
        "subtitle_style": "minimal premium text overlays",
        "best_for": ["product_image_agent", "ecommerce_agent", "ad_creative_agent"],
    },
    "luxury_cinematic_ad": {
        "aspect_ratios": ["16:9", "9:16", "4:5"],
        "camera_motion": "slow cinematic push-ins, elegant parallax, controlled macro movement",
        "shot_types": ["atmospheric opener", "premium hero shot", "detail sequence", "lifestyle moment", "elegant CTA"],
        "lens_language": "high-end cinematic commercial",
        "lighting_style": "dramatic soft contrast, premium highlights, deep background separation",
        "motion_intensity": "low to medium",
        "cutting_pace": "slow premium pacing with deliberate transitions",
        "voice_direction": "calm, premium, aspirational",
        "subtitle_style": "minimal luxury typography",
        "best_for": ["ad_creative_agent", "marketing_specialist_agent", "ecommerce_agent"],
    },
    "direct_response_ad": {
        "aspect_ratios": ["9:16", "4:5", "1:1"],
        "camera_motion": "direct demonstration framing with sharp product visibility",
        "shot_types": ["problem hook", "product demo", "proof point", "benefit stack", "offer CTA"],
        "lens_language": "clear ecommerce conversion framing",
        "lighting_style": "bright trust-building lighting",
        "motion_intensity": "medium to high",
        "cutting_pace": "fast hook, rapid proof, strong CTA",
        "voice_direction": "clear, persuasive, energetic, not spammy",
        "subtitle_style": "bold performance captions with benefit emphasis",
        "best_for": ["marketing_specialist_agent", "ad_creative_agent", "ecommerce_agent"],
    },
    "multilingual_dubbing": {
        "aspect_ratios": ["9:16", "16:9"],
        "camera_motion": "preserve original visual timing and facial rhythm",
        "shot_types": ["speaker close-up", "product cutaway", "reaction shot", "CTA frame"],
        "lens_language": "speech-safe framing for lip-sync readability",
        "lighting_style": "clear face visibility with clean product cutaways",
        "motion_intensity": "low to medium",
        "cutting_pace": "language-aware pacing with room for translated speech length",
        "voice_direction": "native-sounding, region-aware, natural pacing and intonation",
        "subtitle_style": "localized captions matching language and reading speed",
        "best_for": ["ugc_video_agent", "social_media_manager_agent", "marketing_specialist_agent"],
    },
}


def select_cinematic_parameter_preset(
    agent_id: str,
    media_type: str = "",
    objective: str = "",
    platform: str = "",
    language: str = "English",
) -> Dict[str, Any]:
    agent = _safe_text(agent_id).lower()
    media_type_l = _safe_text(media_type).lower()
    objective_l = _safe_text(objective).lower()
    platform_l = _safe_text(platform).lower()
    language_l = _safe_text(language, "English").lower()

    if language_l not in {"english", "en"} or "dub" in media_type_l or "multilingual" in objective_l:
        selected_key = "multilingual_dubbing"
    elif "luxury" in objective_l or "premium cinematic" in objective_l:
        selected_key = "luxury_cinematic_ad"
    elif "image" in media_type_l or agent == "product_image_agent":
        selected_key = "product_photography"
    elif "conversion" in objective_l or "direct response" in objective_l or "meta" in platform_l:
        selected_key = "direct_response_ad"
    else:
        selected_key = "premium_ugc_video"

    preset = dict(CINEMATIC_PARAMETER_PRESETS[selected_key])
    preset["preset_key"] = selected_key
    preset["selected_for_agent"] = agent
    preset["selected_for_platform"] = _safe_text(platform, "short-form social")
    preset["provider_parameter_guidance"] = {
        "aspect_ratio_priority": preset["aspect_ratios"][0],
        "motion_guidance": preset["camera_motion"],
        "lighting_guidance": preset["lighting_style"],
        "shot_type_guidance": preset["shot_types"],
        "caption_guidance": preset["subtitle_style"],
        "voice_guidance": preset["voice_direction"],
    }
    return preset

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

    cinematic_parameter_preset = select_cinematic_parameter_preset(
        agent_id=agent_id,
        media_type=media_type,
        objective=objective,
        platform=platform,
        language=language,
    )


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
        "cinematic_parameter_preset": cinematic_parameter_preset,
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

    orchestration_packet["character_consistency_plan"] = build_character_consistency_plan(payload, orchestration_packet)

    orchestration_packet["multilingual_dubbing_plan"] = build_multilingual_dubbing_plan(payload, orchestration_packet)




    return {
        "success": True,
        "status": "shared_ai_media_creative_director_ready",
        "scope": "platform_wide_reusable_capability",
        "available_agents": sorted(MEDIA_RELEVANT_AGENTS),
        "orchestration_packet": orchestration_packet,
    }




def build_character_consistency_plan(payload: Dict[str, Any], orchestration_packet: Dict[str, Any]) -> Dict[str, Any]:
    character_id = _safe_text(payload.get("character_id") or payload.get("avatar_id") or payload.get("creator_id"), "")
    character_description = _safe_text(payload.get("character_description") or payload.get("avatar_description"), "")
    reference_asset_id = _safe_text(payload.get("reference_asset_id") or payload.get("face_reference_id"), "")
    requires_same_face = bool(character_id or character_description or reference_asset_id)

    locked_identity_fields = [
        "face_shape",
        "skin_tone",
        "hair_style",
        "hair_colour",
        "eye_shape",
        "age_range",
        "facial_hair",
        "distinctive_features",
        "body_type",
        "voice_profile",
        "accent",
        "speaking_pace",
        "creator_style",
    ]

    return {
        "same_face_required": requires_same_face,
        "character_id": character_id or None,
        "reference_asset_id": reference_asset_id or None,
        "character_description_present": bool(character_description),
        "identity_lock_fields": locked_identity_fields,
        "continuity_rules": {
            "preserve_face_across_scenes": requires_same_face,
            "preserve_face_across_provider_retries": requires_same_face,
            "preserve_face_across_platform_variants": requires_same_face,
            "preserve_voice_across_dubs": requires_same_face,
            "preserve_creator_style": requires_same_face,
            "reject_if_face_drift_detected": requires_same_face,
            "manual_review_if_identity_confidence_low": requires_same_face,
        },
        "provider_prompt_rules": [
            "Use the same character identity across every shot.",
            "Do not alter age, ethnicity, facial structure, hairstyle, or distinctive features between scenes.",
            "Preserve the same speaker identity when creating multilingual variants.",
            "Use reference assets where supported by the selected provider.",
            "If provider cannot preserve identity, route to fallback provider or manual review.",
        ],
        "quality_checks": {
            "minimum_identity_confidence": 0.86 if requires_same_face else None,
            "face_drift_check_required": requires_same_face,
            "voice_drift_check_required": requires_same_face,
            "scene_to_scene_identity_check_required": requires_same_face,
            "provider_retry_identity_check_required": requires_same_face,
        },
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


def build_multilingual_dubbing_plan(payload: Dict[str, Any], orchestration_packet: Dict[str, Any]) -> Dict[str, Any]:
    language = _safe_text(payload.get("language"), "English")
    target_languages = payload.get("target_languages") or payload.get("languages") or []
    region = _safe_text(payload.get("region") or payload.get("country"), "global")
    media_type = _safe_text(payload.get("media_type"), "")
    objective = _safe_text(payload.get("objective") or payload.get("campaign_goal"), "")

    if isinstance(target_languages, str):
        target_languages = [item.strip() for item in target_languages.split(",") if item.strip()]

    language_l = language.lower()
    objective_l = objective.lower()
    media_type_l = media_type.lower()

    multilingual_required = bool(
        target_languages
        or language_l not in {"english", "en"}
        or "dub" in media_type_l
        or "multilingual" in objective_l
        or "localized" in objective_l
        or "localised" in objective_l
    )

    if multilingual_required and not target_languages:
        target_languages = [language]

    return {
        "multilingual_required": multilingual_required,
        "source_language": "English",
        "primary_language": language,
        "target_languages": target_languages,
        "region": region,
        "dubbing_mode": "native_sounding_region_aware_dubbing" if multilingual_required else "not_required",
        "lip_sync_required": multilingual_required,
        "caption_localisation_required": multilingual_required,
        "voice_consistency_required": multilingual_required,
        "script_adaptation_rules": {
            "translate_meaning_not_literal_words": True,
            "preserve_offer_and_claim_accuracy": True,
            "preserve_brand_voice": True,
            "adapt_idioms_to_region": multilingual_required,
            "adapt_cta_to_platform_and_country": multilingual_required,
            "avoid_unsupported_local_claims": True,
        },
        "voice_rules": {
            "native_accent_required": multilingual_required,
            "natural_pacing_required": multilingual_required,
            "preserve_creator_energy": multilingual_required,
            "preserve_character_voice_when_same_face_required": orchestration_packet.get("character_consistency_plan", {}).get("same_face_required", False),
            "avoid_robotic_or_overacted_delivery": True,
        },
        "timing_rules": {
            "allow_translation_length_variance": True,
            "adjust_scene_pacing_for_language_length": multilingual_required,
            "maintain_cta_readability": True,
            "keep_hook_inside_first_two_seconds_where_possible": True,
        },
        "quality_checks": {
            "translation_accuracy_check_required": multilingual_required,
            "lip_sync_quality_check_required": multilingual_required,
            "caption_readability_check_required": multilingual_required,
            "regional_compliance_review_recommended": multilingual_required,
            "manual_review_if_claims_change": True,
        },
        "provider_requirements": {
            "requires_voice_provider": multilingual_required,
            "requires_lip_sync_provider": multilingual_required,
            "requires_caption_generation": multilingual_required,
            "fallback_to_subtitled_variant_if_lip_sync_fails": multilingual_required,
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
