from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
runtime_file = ROOT / "backend" / "app" / "runtime" / "ai_media_creative_director.py"

if not runtime_file.exists():
    raise SystemExit("ai_media_creative_director.py not found")

backups = ROOT / "backups"
backups.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_file = backups / f"ai_media_creative_director_before_multilingual_dubbing_{timestamp}.py"
backup_file.write_text(runtime_file.read_text(encoding="utf-8"), encoding="utf-8")

content = runtime_file.read_text(encoding="utf-8")

DUBBING_BLOCK = r'''

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
'''

if "def build_multilingual_dubbing_plan(" not in content:
    insert_before = "\ndef readiness"
    if insert_before in content:
        content = content.replace(insert_before, DUBBING_BLOCK + insert_before, 1)
    else:
        content += DUBBING_BLOCK

attach_block = '''
    orchestration_packet["multilingual_dubbing_plan"] = build_multilingual_dubbing_plan(payload, orchestration_packet)
'''

if 'orchestration_packet["multilingual_dubbing_plan"] = build_multilingual_dubbing_plan(payload, orchestration_packet)' not in content:
    content = content.replace(
        '    orchestration_packet["character_consistency_plan"] = build_character_consistency_plan(payload, orchestration_packet)',
        '    orchestration_packet["character_consistency_plan"] = build_character_consistency_plan(payload, orchestration_packet)\n' + attach_block,
        1,
    )

runtime_file.write_text(content, encoding="utf-8")

test_file = ROOT / "test_ai_media_multilingual_dubbing_rules.py"
test_file.write_text(r'''
from backend.app.runtime.ai_media_creative_director import (
    run_shared_ai_media_creative_director,
    build_multilingual_dubbing_plan,
)


def main():
    payload = {
        "agent_id": "ugc_video_agent",
        "brand_name": "Dubbing Test Brand",
        "product_name": "Dubbing Test Product",
        "target_audience": "international ecommerce buyers",
        "objective": "multilingual premium UGC ad",
        "platform": "TikTok",
        "media_type": "ugc video dubbing",
        "language": "Arabic",
        "target_languages": ["Arabic", "Spanish", "French"],
        "region": "global",
        "character_id": "creator_001",
        "reference_asset_id": "face_ref_001",
    }

    result = run_shared_ai_media_creative_director(payload)
    packet = result["orchestration_packet"]
    plan = packet["multilingual_dubbing_plan"]

    assert result["success"] is True
    assert plan["multilingual_required"] is True
    assert plan["lip_sync_required"] is True
    assert plan["caption_localisation_required"] is True
    assert plan["voice_consistency_required"] is True
    assert plan["voice_rules"]["native_accent_required"] is True
    assert plan["voice_rules"]["preserve_character_voice_when_same_face_required"] is True
    assert plan["provider_requirements"]["requires_voice_provider"] is True
    assert plan["provider_requirements"]["fallback_to_subtitled_variant_if_lip_sync_fails"] is True
    assert "Arabic" in plan["target_languages"]

    direct_plan = build_multilingual_dubbing_plan(payload, packet)
    assert direct_plan["multilingual_required"] is True

    english_result = run_shared_ai_media_creative_director({
        "agent_id": "ugc_video_agent",
        "brand_name": "English Brand",
        "product_name": "English Product",
        "objective": "premium UGC ad",
        "platform": "TikTok",
        "media_type": "ugc video",
        "language": "English",
    })

    english_plan = english_result["orchestration_packet"]["multilingual_dubbing_plan"]
    assert english_plan["multilingual_required"] is False
    assert english_plan["lip_sync_required"] is False

    print("AI_MEDIA_MULTILINGUAL_DUBBING_RULES_OK")


if __name__ == "__main__":
    main()
'''.strip() + "\n", encoding="utf-8")

print("AI_MEDIA_MULTILINGUAL_DUBBING_RULES_ADDED")
print(f"Backup: {backup_file}")
print(f"Updated: {runtime_file}")
print(f"Created: {test_file}")