from backend.app.runtime.ai_media_creative_director import (
    run_shared_ai_media_creative_director,
    score_ai_media_orchestration,
)


def main():
    result = run_shared_ai_media_creative_director({
        "agent_id": "ugc_video_agent",
        "brand_name": "Premium Brand",
        "product_name": "Premium Product",
        "target_audience": "high-intent ecommerce buyers",
        "objective": "premium conversion-focused UGC video",
        "platform": "TikTok",
        "media_type": "ugc video",
        "language": "English",
        "region": "global",
    })

    packet = result["orchestration_packet"]
    score = packet["orchestration_score"]

    assert result["success"] is True
    assert score["overall_score"] >= 80
    assert score["provider_execution_allowed"] is True
    assert score["manual_review_required"] is False
    assert "brand_fit" in score["scores"]
    assert "cinematic_quality" in score["scores"]
    assert "ecommerce_conversion_strength" in score["scores"]
    assert "provider_fallback_readiness" in score["scores"]
    assert "premium_output_readiness" in score["scores"]

    direct_score = score_ai_media_orchestration(packet)
    assert direct_score["overall_score"] >= 80

    print("AI_MEDIA_ORCHESTRATION_SCORING_OK")


if __name__ == "__main__":
    main()
