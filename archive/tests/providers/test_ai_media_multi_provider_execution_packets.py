from backend.app.runtime.ai_media_multi_provider_execution_packets import (
    advance_packet_to_next_provider,
    ai_media_multi_provider_packets_readiness,
    create_ai_media_multi_provider_packet,
    list_ai_media_multi_provider_packets,
)


def main():
    readiness = ai_media_multi_provider_packets_readiness()
    assert readiness["status"] == "ready"
    assert readiness["supports_provider_fallback_chains"] is True
    assert readiness["layout_changes"] is False

    packet = create_ai_media_multi_provider_packet(
        tenant_id="tenant_test",
        brand_name="Demo Brand",
        media_type="ugc video",
        prompt="Create a premium UGC video ad with hook, proof, benefit and CTA.",
        target_platform="TikTok",
        preferred_provider="runway",
        payload={
            "brand_colours": ["#111827", "#C8A96A"],
            "character_reference": "creator_reference_001",
            "lip_sync_required": True,
            "same_face_required": True,
            "camera_direction": "smooth handheld creator framing",
        },
        owner_approved=True,
        entitlement_active=True,
        quality_score=88,
        max_attempts=3,
    )
    assert packet["status"] == "prepared"
    assert packet["active_provider"] == "runway"
    assert packet["aspect_ratio"] == "9:16"
    assert packet["resolution_target"] == "1080x1920"
    assert packet["execution_allowed"] is True

    fallback = advance_packet_to_next_provider(packet, failure_reason="provider_timeout")
    assert fallback["status"] == "fallback_provider_selected"
    assert fallback["active_provider"] != "runway"

    low_quality = create_ai_media_multi_provider_packet(
        tenant_id="tenant_test",
        brand_name="Demo Brand",
        media_type="image",
        prompt="basic image",
        target_platform="Shopify",
        quality_score=40,
    )
    assert low_quality["status"] == "blocked_by_quality_gate"
    assert low_quality["execution_allowed"] is False

    risky = create_ai_media_multi_provider_packet(
        tenant_id="tenant_test",
        brand_name="Demo Brand",
        media_type="video",
        prompt="publish paid campaign and increase spend",
        target_platform="Meta Ads",
        owner_approved=False,
        quality_score=90,
    )
    assert risky["status"] == "pending_owner_approval"

    listed = list_ai_media_multi_provider_packets(tenant_id="tenant_test")
    assert listed["count"] >= 3

    print("AI_MEDIA_MULTI_PROVIDER_EXECUTION_PACKETS_OK")


if __name__ == "__main__":
    main()
