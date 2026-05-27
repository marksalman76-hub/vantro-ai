from backend.app.runtime.ai_media_live_provider_execution import (
    detect_ai_media_provider_readiness,
    execute_ai_media_provider_ready_packet,
    select_provider_route,
)
from backend.app.runtime.provider_connector_registry import ai_media_provider_execution_bridge


def sample_packet():
    return {
        "packet_type": "provider_ready_ai_media_execution_packet",
        "execution_allowed": True,
        "manual_review_required": False,
        "primary_provider_slot": "video_generation_provider",
        "fallback_provider_slots": ["ugc_avatar_provider", "generic_video_provider"],
        "media_type": "ugc video",
        "platform": "TikTok",
        "brand": "Provider Foundation Brand",
        "product": "Provider Foundation Product",
        "target_audience": "online buyers",
        "language": "English",
        "region": "global",
        "provider_parameters": {
            "style": "premium UGC",
            "aspect_ratio_priority": "9:16",
            "scene_plan": [{"scene": 1}, {"scene": 2}, {"scene": 3}, {"scene": 4}],
        },
        "continuity_controls": {"same_face_required": False},
        "multilingual_controls": {"multilingual_required": False},
        "fallback_controls": {"fallback_enabled": True},
        "governance_controls": {
            "do_not_publish_without_governance": True,
            "owner_review_required_for_spend_or_campaign_scaling": True,
        },
        "quality_controls": {
            "overall_score": 92,
            "premium_only": True,
            "no_placeholder_outputs": True,
        },
    }


def main():
    readiness = detect_ai_media_provider_readiness()
    assert readiness["success"] is True
    assert readiness["provider_detection_enabled"] is True
    assert readiness["secret_exposure"] is False
    assert "openai_image" in readiness["providers"]
    assert "runway" in readiness["providers"]
    assert "elevenlabs" in readiness["providers"]

    route = select_provider_route(sample_packet())
    assert route["success"] is True
    assert "preferred_provider_order" in route
    assert route["secret_exposure"] is False

    result = execute_ai_media_provider_ready_packet(sample_packet())
    assert result["success"] is True
    assert result["runtime"] == "ai_media_live_provider_execution"
    assert result["execution_status"] in {
        "prepared_no_live_provider_configured",
        "prepared_provider_adapter_stub",
        "prepared_live_adapter_ready",
    }
    assert result["secret_exposure"] is False
    assert result["governance_controls"]["do_not_publish_without_governance"] is True

    bridge_result = ai_media_provider_execution_bridge({
        "provider_ready_execution_packet": sample_packet()
    })
    assert bridge_result["success"] is True
    assert bridge_result["bridge_runtime"] == "ai_media_provider_execution_bridge"

    missing = ai_media_provider_execution_bridge({"normal": "payload"})
    assert missing["success"] is False
    assert missing["error"] == "provider_ready_execution_packet_missing"

    print("AI_MEDIA_LIVE_PROVIDER_EXECUTION_FOUNDATION_OK")


if __name__ == "__main__":
    main()
