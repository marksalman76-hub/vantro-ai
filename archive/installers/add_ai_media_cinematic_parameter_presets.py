from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
runtime_file = ROOT / "backend" / "app" / "runtime" / "ai_media_creative_director.py"

if not runtime_file.exists():
    raise SystemExit("ai_media_creative_director.py not found")

backups = ROOT / "backups"
backups.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_file = backups / f"ai_media_creative_director_before_cinematic_presets_{timestamp}.py"
backup_file.write_text(runtime_file.read_text(encoding="utf-8"), encoding="utf-8")

content = runtime_file.read_text(encoding="utf-8")

PRESET_BLOCK = r'''

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
'''

if "CINEMATIC_PARAMETER_PRESETS" not in content:
    insert_before = "\ndef score_ai_media_orchestration"
    if insert_before in content:
        content = content.replace(insert_before, PRESET_BLOCK + insert_before, 1)
    else:
        content += PRESET_BLOCK

preset_attach = '''
    cinematic_parameter_preset = select_cinematic_parameter_preset(
        agent_id=agent_id,
        media_type=media_type,
        objective=objective,
        platform=platform,
        language=language,
    )
'''

if "cinematic_parameter_preset = select_cinematic_parameter_preset(" not in content:
    content = content.replace(
        "    provider_strategy = build_provider_strategy(agent_id, media_type)",
        "    provider_strategy = build_provider_strategy(agent_id, media_type)\n" + preset_attach,
        1,
    )

if '"cinematic_parameter_preset": cinematic_parameter_preset,' not in content:
    content = content.replace(
        '        "provider_strategy": provider_strategy,',
        '        "provider_strategy": provider_strategy,\n        "cinematic_parameter_preset": cinematic_parameter_preset,',
        1,
    )

if '"cinematic_parameter_preset": cinematic_parameter_preset,' not in content:
    raise SystemExit("Failed to attach cinematic_parameter_preset to orchestration packet")

runtime_file.write_text(content, encoding="utf-8")

test_file = ROOT / "test_ai_media_cinematic_parameter_presets.py"
test_file.write_text(r'''
from backend.app.runtime.ai_media_creative_director import (
    run_shared_ai_media_creative_director,
    select_cinematic_parameter_preset,
)


def main():
    ugc = run_shared_ai_media_creative_director({
        "agent_id": "ugc_video_agent",
        "brand_name": "UGC Brand",
        "product_name": "UGC Product",
        "objective": "premium UGC ad",
        "platform": "TikTok",
        "media_type": "ugc video",
        "language": "English",
    })["orchestration_packet"]["cinematic_parameter_preset"]

    assert ugc["preset_key"] == "premium_ugc_video"
    assert "9:16" in ugc["aspect_ratios"]
    assert ugc["provider_parameter_guidance"]["aspect_ratio_priority"] == "9:16"

    product = select_cinematic_parameter_preset(
        agent_id="product_image_agent",
        media_type="product image",
        objective="premium product photography",
        platform="website",
        language="English",
    )
    assert product["preset_key"] == "product_photography"

    luxury = select_cinematic_parameter_preset(
        agent_id="ad_creative_agent",
        media_type="video",
        objective="luxury cinematic ecommerce ad",
        platform="Instagram",
        language="English",
    )
    assert luxury["preset_key"] == "luxury_cinematic_ad"

    direct = select_cinematic_parameter_preset(
        agent_id="marketing_specialist_agent",
        media_type="video",
        objective="conversion direct response ad",
        platform="Meta",
        language="English",
    )
    assert direct["preset_key"] == "direct_response_ad"

    multilingual = select_cinematic_parameter_preset(
        agent_id="ugc_video_agent",
        media_type="ugc video dubbing",
        objective="multilingual ad variant",
        platform="TikTok",
        language="Arabic",
    )
    assert multilingual["preset_key"] == "multilingual_dubbing"

    print("AI_MEDIA_CINEMATIC_PARAMETER_PRESETS_OK")


if __name__ == "__main__":
    main()
'''.strip() + "\n", encoding="utf-8")

print("AI_MEDIA_CINEMATIC_PARAMETER_PRESETS_ADDED")
print(f"Backup: {backup_file}")
print(f"Updated: {runtime_file}")
print(f"Created: {test_file}")