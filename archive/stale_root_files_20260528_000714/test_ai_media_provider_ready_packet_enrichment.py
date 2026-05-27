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
