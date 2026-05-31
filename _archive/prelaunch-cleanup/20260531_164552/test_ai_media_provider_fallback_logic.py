from backend.app.runtime.ai_media_creative_director import (
    run_shared_ai_media_creative_director,
    build_provider_fallback_execution_plan,
)


def main():
    result = run_shared_ai_media_creative_director({
        "agent_id": "ad_creative_agent",
        "brand_name": "Fallback Test Brand",
        "product_name": "Fallback Test Product",
        "target_audience": "online shoppers",
        "objective": "conversion-focused ecommerce ad",
        "platform": "Meta",
        "media_type": "ugc video",
        "language": "English",
        "region": "global",
    })

    packet = result["orchestration_packet"]
    fallback_plan = packet["provider_fallback_execution_plan"]

    assert result["success"] is True
    assert fallback_plan["fallback_enabled"] is True
    assert fallback_plan["manual_review_final_step"] is True
    assert fallback_plan["primary_provider_slot"] == "video_generation_provider"
    assert len(fallback_plan["fallback_steps"]) >= 3
    assert fallback_plan["rules"]["preserve_brand_memory"] is True
    assert fallback_plan["rules"]["preserve_character_consistency"] is True
    assert fallback_plan["rules"]["do_not_publish_without_governance"] is True
    assert fallback_plan["rules"]["owner_review_required_for_spend_or_campaign_scaling"] is True

    direct_plan = build_provider_fallback_execution_plan(packet)
    assert direct_plan["fallback_enabled"] is True
    assert direct_plan["adapter_payload_present"] is True

    print("AI_MEDIA_PROVIDER_FALLBACK_LOGIC_OK")


if __name__ == "__main__":
    main()
