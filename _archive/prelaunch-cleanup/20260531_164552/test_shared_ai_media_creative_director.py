from backend.app.runtime.ai_media_creative_director import (
    readiness,
    run_shared_ai_media_creative_director,
    is_ai_media_relevant_agent,
)


def main():
    ready = readiness()
    assert ready["success"] is True
    assert ready["scope"] == "platform_wide_reusable_capability"
    assert ready["available_to_relevant_agents"] is True
    assert "marketing_specialist_agent" in ready["available_agents"]
    assert "ecommerce_agent" in ready["available_agents"]
    assert "ugc_video_agent" in ready["available_agents"]

    assert is_ai_media_relevant_agent("marketing_specialist_agent") is True
    assert is_ai_media_relevant_agent("ecommerce_agent") is True
    assert is_ai_media_relevant_agent("irrelevant_test_agent") is False

    result = run_shared_ai_media_creative_director({
        "agent_id": "marketing_specialist_agent",
        "brand_name": "Test Brand",
        "product_name": "Premium Test Product",
        "target_audience": "busy online shoppers",
        "objective": "conversion-focused premium UGC ad",
        "platform": "TikTok",
        "media_type": "ugc video",
        "language": "English",
        "region": "Australia",
    })

    packet = result["orchestration_packet"]

    assert result["success"] is True
    assert result["scope"] == "platform_wide_reusable_capability"
    assert packet["available_to_relevant_agents"] is True
    assert packet["agent_is_media_relevant"] is True
    assert packet["provider_strategy"]["fallback_required"] is True
    assert packet["quality_rules"]["premium_only"] is True
    assert packet["quality_rules"]["same_character_consistency_required_when_character_present"] is True
    assert packet["adapter_ready_payload"]["shot_count"] >= 4

    print("SHARED_AI_MEDIA_CREATIVE_DIRECTOR_OK")


if __name__ == "__main__":
    main()
