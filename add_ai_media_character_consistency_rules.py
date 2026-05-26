from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
runtime_file = ROOT / "backend" / "app" / "runtime" / "ai_media_creative_director.py"

if not runtime_file.exists():
    raise SystemExit("ai_media_creative_director.py not found")

backups = ROOT / "backups"
backups.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_file = backups / f"ai_media_creative_director_before_character_consistency_{timestamp}.py"
backup_file.write_text(runtime_file.read_text(encoding="utf-8"), encoding="utf-8")

content = runtime_file.read_text(encoding="utf-8")

RULES_BLOCK = r'''

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
'''

if "def build_character_consistency_plan(" not in content:
    insert_before = "\ndef build_provider_fallback_execution_plan"
    if insert_before in content:
        content = content.replace(insert_before, RULES_BLOCK + insert_before, 1)
    else:
        content += RULES_BLOCK

attach_block = '''
    orchestration_packet["character_consistency_plan"] = build_character_consistency_plan(payload, orchestration_packet)
'''

if 'orchestration_packet["character_consistency_plan"] = build_character_consistency_plan(payload, orchestration_packet)' not in content:
    content = content.replace(
        '    orchestration_packet["provider_fallback_execution_plan"] = build_provider_fallback_execution_plan(orchestration_packet)',
        '    orchestration_packet["provider_fallback_execution_plan"] = build_provider_fallback_execution_plan(orchestration_packet)\n' + attach_block,
        1,
    )

runtime_file.write_text(content, encoding="utf-8")

test_file = ROOT / "test_ai_media_character_consistency_rules.py"
test_file.write_text(r'''
from backend.app.runtime.ai_media_creative_director import (
    run_shared_ai_media_creative_director,
    build_character_consistency_plan,
)


def main():
    payload = {
        "agent_id": "ugc_video_agent",
        "brand_name": "Character Test Brand",
        "product_name": "Character Test Product",
        "target_audience": "online buyers",
        "objective": "premium UGC ad with same creator across scenes",
        "platform": "TikTok",
        "media_type": "ugc video",
        "language": "English",
        "region": "global",
        "character_id": "creator_001",
        "character_description": "same female creator, warm smile, shoulder-length brown hair, natural creator tone",
        "reference_asset_id": "face_ref_001",
    }

    result = run_shared_ai_media_creative_director(payload)
    packet = result["orchestration_packet"]
    plan = packet["character_consistency_plan"]

    assert result["success"] is True
    assert plan["same_face_required"] is True
    assert plan["character_id"] == "creator_001"
    assert plan["reference_asset_id"] == "face_ref_001"
    assert plan["continuity_rules"]["preserve_face_across_scenes"] is True
    assert plan["continuity_rules"]["preserve_face_across_provider_retries"] is True
    assert plan["continuity_rules"]["reject_if_face_drift_detected"] is True
    assert plan["quality_checks"]["face_drift_check_required"] is True
    assert plan["quality_checks"]["minimum_identity_confidence"] >= 0.86

    direct_plan = build_character_consistency_plan(payload, packet)
    assert direct_plan["same_face_required"] is True

    no_character_result = run_shared_ai_media_creative_director({
        "agent_id": "product_image_agent",
        "brand_name": "No Character Brand",
        "product_name": "Product Only",
        "objective": "premium product photography",
        "platform": "website",
        "media_type": "product image",
    })

    no_character_plan = no_character_result["orchestration_packet"]["character_consistency_plan"]
    assert no_character_plan["same_face_required"] is False

    print("AI_MEDIA_CHARACTER_CONSISTENCY_RULES_OK")


if __name__ == "__main__":
    main()
'''.strip() + "\n", encoding="utf-8")

print("AI_MEDIA_CHARACTER_CONSISTENCY_RULES_ADDED")
print(f"Backup: {backup_file}")
print(f"Updated: {runtime_file}")
print(f"Created: {test_file}")