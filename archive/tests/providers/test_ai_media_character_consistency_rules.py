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
