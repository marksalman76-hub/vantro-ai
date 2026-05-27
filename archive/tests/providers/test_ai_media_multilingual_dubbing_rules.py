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
