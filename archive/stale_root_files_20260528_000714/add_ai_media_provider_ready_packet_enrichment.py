from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
runtime_file = ROOT / "backend" / "app" / "runtime" / "ai_media_creative_director.py"

if not runtime_file.exists():
    raise SystemExit("ai_media_creative_director.py not found")

backups = ROOT / "backups"
backups.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_file = backups / f"ai_media_creative_director_before_provider_ready_packet_{timestamp}.py"
backup_file.write_text(runtime_file.read_text(encoding="utf-8"), encoding="utf-8")

content = runtime_file.read_text(encoding="utf-8")

PACKET_BLOCK = r'''

def build_provider_ready_execution_packet(orchestration_packet: Dict[str, Any]) -> Dict[str, Any]:
    adapter_payload = orchestration_packet.get("adapter_ready_payload", {})
    provider_strategy = orchestration_packet.get("provider_strategy", {})
    cinematic_preset = orchestration_packet.get("cinematic_parameter_preset", {})
    character_plan = orchestration_packet.get("character_consistency_plan", {})
    dubbing_plan = orchestration_packet.get("multilingual_dubbing_plan", {})
    fallback_plan = orchestration_packet.get("provider_fallback_execution_plan", {})
    score = orchestration_packet.get("orchestration_score", {})

    return {
        "packet_type": "provider_ready_ai_media_execution_packet",
        "packet_version": "1.0.0",
        "execution_allowed": score.get("provider_execution_allowed", True),
        "manual_review_required": score.get("manual_review_required", False),
        "quality_threshold": fallback_plan.get("quality_threshold", 80),
        "primary_provider_slot": provider_strategy.get("primary_provider_slot"),
        "fallback_provider_slots": provider_strategy.get("fallback_provider_slots", []),
        "creative_brief": adapter_payload.get("creative_brief"),
        "media_type": orchestration_packet.get("media_type"),
        "platform": orchestration_packet.get("platform"),
        "brand": orchestration_packet.get("brand"),
        "product": orchestration_packet.get("product"),
        "target_audience": orchestration_packet.get("target_audience"),
        "language": orchestration_packet.get("language"),
        "region": orchestration_packet.get("region"),
        "provider_parameters": {
            "style": adapter_payload.get("style"),
            "camera_language": adapter_payload.get("camera_language"),
            "lighting": adapter_payload.get("lighting"),
            "pacing": adapter_payload.get("pacing"),
            "hook": adapter_payload.get("hook"),
            "scene_plan": adapter_payload.get("scenes", []),
            "aspect_ratio_priority": cinematic_preset.get("provider_parameter_guidance", {}).get("aspect_ratio_priority"),
            "motion_guidance": cinematic_preset.get("provider_parameter_guidance", {}).get("motion_guidance"),
            "lighting_guidance": cinematic_preset.get("provider_parameter_guidance", {}).get("lighting_guidance"),
            "shot_type_guidance": cinematic_preset.get("provider_parameter_guidance", {}).get("shot_type_guidance", []),
            "caption_guidance": cinematic_preset.get("provider_parameter_guidance", {}).get("caption_guidance"),
            "voice_guidance": cinematic_preset.get("provider_parameter_guidance", {}).get("voice_guidance"),
        },
        "continuity_controls": {
            "same_face_required": character_plan.get("same_face_required", False),
            "character_id": character_plan.get("character_id"),
            "reference_asset_id": character_plan.get("reference_asset_id"),
            "identity_lock_fields": character_plan.get("identity_lock_fields", []),
            "face_drift_check_required": character_plan.get("quality_checks", {}).get("face_drift_check_required", False),
            "minimum_identity_confidence": character_plan.get("quality_checks", {}).get("minimum_identity_confidence"),
        },
        "multilingual_controls": {
            "multilingual_required": dubbing_plan.get("multilingual_required", False),
            "target_languages": dubbing_plan.get("target_languages", []),
            "lip_sync_required": dubbing_plan.get("lip_sync_required", False),
            "caption_localisation_required": dubbing_plan.get("caption_localisation_required", False),
            "voice_consistency_required": dubbing_plan.get("voice_consistency_required", False),
            "fallback_to_subtitled_variant_if_lip_sync_fails": dubbing_plan.get("provider_requirements", {}).get("fallback_to_subtitled_variant_if_lip_sync_fails", False),
        },
        "fallback_controls": {
            "fallback_enabled": fallback_plan.get("fallback_enabled", True),
            "execution_mode": fallback_plan.get("execution_mode"),
            "fallback_steps": fallback_plan.get("fallback_steps", []),
            "manual_review_final_step": fallback_plan.get("manual_review_final_step", True),
        },
        "governance_controls": {
            "do_not_publish_without_governance": True,
            "owner_review_required_for_spend_or_campaign_scaling": True,
            "client_safe_output_only": True,
            "internal_rules_hidden_from_client": True,
        },
        "quality_controls": {
            "overall_score": score.get("overall_score"),
            "readiness_level": score.get("readiness_level"),
            "score_breakdown": score.get("scores", {}),
            "premium_only": orchestration_packet.get("quality_rules", {}).get("premium_only", True),
            "no_placeholder_outputs": orchestration_packet.get("quality_rules", {}).get("no_placeholder_outputs", True),
        },
    }
'''

if "def build_provider_ready_execution_packet(" not in content:
    insert_before = "\ndef readiness"
    if insert_before in content:
        content = content.replace(insert_before, PACKET_BLOCK + insert_before, 1)
    else:
        content += PACKET_BLOCK

attach_block = '''
    orchestration_packet["provider_ready_execution_packet"] = build_provider_ready_execution_packet(orchestration_packet)
'''

if 'orchestration_packet["provider_ready_execution_packet"] = build_provider_ready_execution_packet(orchestration_packet)' not in content:
    content = content.replace(
        '    orchestration_packet["multilingual_dubbing_plan"] = build_multilingual_dubbing_plan(payload, orchestration_packet)',
        '    orchestration_packet["multilingual_dubbing_plan"] = build_multilingual_dubbing_plan(payload, orchestration_packet)\n' + attach_block,
        1,
    )

runtime_file.write_text(content, encoding="utf-8")

test_file = ROOT / "test_ai_media_provider_ready_packet_enrichment.py"
test_file.write_text(r'''
from backend.app.runtime.ai_media_creative_director import (
    run_shared_ai_media_creative_director,
    build_provider_ready_execution_packet,
)


def main():
    payload = {
        "agent_id": "ugc_video_agent",
        "brand_name": "Provider Packet Brand",
        "product_name": "Provider Packet Product",
        "target_audience": "premium ecommerce buyers",
        "objective": "multilingual premium UGC conversion ad",
        "platform": "TikTok",
        "media_type": "ugc video dubbing",
        "language": "Spanish",
        "target_languages": ["Spanish", "Arabic"],
        "region": "global",
        "character_id": "creator_002",
        "reference_asset_id": "face_ref_002",
    }

    result = run_shared_ai_media_creative_director(payload)
    packet = result["orchestration_packet"]
    provider_packet = packet["provider_ready_execution_packet"]

    assert result["success"] is True
    assert provider_packet["packet_type"] == "provider_ready_ai_media_execution_packet"
    assert provider_packet["execution_allowed"] is True
    assert provider_packet["primary_provider_slot"] == "video_generation_provider"
    assert len(provider_packet["fallback_provider_slots"]) >= 1
    assert provider_packet["continuity_controls"]["same_face_required"] is True
    assert provider_packet["continuity_controls"]["character_id"] == "creator_002"
    assert provider_packet["multilingual_controls"]["multilingual_required"] is True
    assert "Spanish" in provider_packet["multilingual_controls"]["target_languages"]
    assert provider_packet["governance_controls"]["do_not_publish_without_governance"] is True
    assert provider_packet["quality_controls"]["premium_only"] is True
    assert provider_packet["provider_parameters"]["aspect_ratio_priority"] is not None
    assert len(provider_packet["provider_parameters"]["scene_plan"]) >= 4

    direct_packet = build_provider_ready_execution_packet(packet)
    assert direct_packet["packet_type"] == "provider_ready_ai_media_execution_packet"

    print("AI_MEDIA_PROVIDER_READY_PACKET_ENRICHMENT_OK")


if __name__ == "__main__":
    main()
'''.strip() + "\n", encoding="utf-8")

print("AI_MEDIA_PROVIDER_READY_PACKET_ENRICHMENT_ADDED")
print(f"Backup: {backup_file}")
print(f"Updated: {runtime_file}")
print(f"Created: {test_file}")