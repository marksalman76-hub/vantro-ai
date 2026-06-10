from backend.app.runtime.shared_creative_media_generation_runtime import _build_video_retry_failover_packet


def test_runway_video_retry_failover_packet():
    packet = _build_video_retry_failover_packet(
        provider_unavailable_reason_code="runway_video_unavailable",
        selected_video_provider="runway",
        readiness_summary={
            "runway_configured": True,
            "kling_configured": True,
            "heygen_configured": False,
            "replicate_configured": False,
        },
        generation_jobs=[
            {
                "media_type": "video",
                "provider": "runway",
                "real_media_asset_created": False,
                "provider_unavailable_reason_code": "runway_video_unavailable",
            }
        ],
        media_assets=[
            {
                "asset_type": "audio",
                "playable": True,
            }
        ],
    )

    assert packet["provider_retry_recommended"] is True, packet
    assert packet["provider_failover_recommended"] is True, packet
    assert packet["provider_retry_allowed"] is True, packet
    assert packet["video_retry_failover_ready"] is True, packet
    assert packet["video_failover_next_provider"] == "kling", packet
    assert packet["final_combined_asset_retry_status"] == "retry_or_failover_ready", packet
    assert packet["provider_retry_external_call_executed"] is False, packet
    assert packet["provider_failover_external_call_executed"] is False, packet
    assert packet["credential_values_exposed"] is False, packet


def test_no_retry_when_video_ready():
    packet = _build_video_retry_failover_packet(
        provider_unavailable_reason_code="none",
        selected_video_provider="runway",
        readiness_summary={},
        generation_jobs=[],
        media_assets=[
            {
                "asset_type": "video",
                "playable": True,
                "download_ready": True,
            }
        ],
    )

    assert packet["provider_retry_recommended"] is False, packet
    assert packet["video_retry_failover_ready"] is False, packet
    assert packet["final_combined_asset_retry_status"] == "not_required", packet


if __name__ == "__main__":
    test_runway_video_retry_failover_packet()
    test_no_retry_when_video_ready()
    print("RUNWAY_VIDEO_RETRY_FAILOVER_PACKET_TEST_PASSED")
