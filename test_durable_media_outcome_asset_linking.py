
from backend.app.runtime.async_media_job_foundation import _apply_durable_outcome_asset_summary


def test_durable_provider_unavailable_with_no_resolved_assets_stays_unavailable():
    result = _apply_durable_outcome_asset_summary(
        status="provider_unavailable",
        safe_reason="Provider execution is not currently available.",
        asset_count=3,
        playable_asset_count=0,
        preview_ready_count=0,
        download_ready_count=0,
        final_asset_ids=["video_asset_meta"],
        final_assets=[],
    )

    assert result["status"] == "provider_unavailable"
    assert result["playable_asset_count"] == 0
    assert result["playable_asset_created"] is False
    assert result["metadata_only"] is True


def test_durable_provider_unavailable_with_playable_audio_becomes_partial_success():
    result = _apply_durable_outcome_asset_summary(
        status="provider_unavailable",
        safe_reason="Provider execution is not currently available.",
        asset_count=3,
        playable_asset_count=0,
        preview_ready_count=0,
        download_ready_count=0,
        final_asset_ids=["audio_asset_real", "video_asset_meta"],
        final_assets=[
            {
                "asset_id": "audio_asset_real",
                "asset_type": "audio",
                "media_type": "audio",
                "provider": "elevenlabs",
                "provider_key": "elevenlabs",
                "status": "completed",
                "playable": True,
                "preview_ready": True,
                "download_ready": True,
                "signed_delivery_created": True,
                "provider_asset_url": "https://abc.supabase.co/storage/v1/object/public/creative-media/audio.mp3",
            },
            {
                "asset_id": "video_asset_meta",
                "asset_type": "video",
                "media_type": "video",
                "provider": "runway",
                "provider_key": "runway",
                "status": "provider_unavailable",
                "metadata_only": True,
            },
        ],
    )

    assert result["status"] == "partial_success"
    assert result["playable_asset_count"] == 1
    assert result["playable_asset_created"] is True
    assert result["signed_delivery_created"] is True
    assert result["metadata_only"] is False
    assert result["partial_success"] is True
    assert "Partial media success" in result["safe_visible_reason"]


def test_durable_demo_supabase_placeholder_does_not_count_as_playable():
    result = _apply_durable_outcome_asset_summary(
        status="provider_unavailable",
        safe_reason="Provider execution is not currently available.",
        asset_count=1,
        playable_asset_count=0,
        preview_ready_count=0,
        download_ready_count=0,
        final_asset_ids=["audio_asset_demo"],
        final_assets=[
            {
                "asset_id": "audio_asset_demo",
                "asset_type": "audio",
                "media_type": "audio",
                "provider": "elevenlabs",
                "provider_key": "elevenlabs",
                "status": "completed",
                "signed_delivery_created": True,
                "provider_asset_url": "https://demo.supabase.co/storage/v1/object/public/creative-media/audio.mp3",
            }
        ],
    )

    assert result["status"] == "provider_unavailable"
    assert result["playable_asset_count"] == 0
    assert result["playable_asset_created"] is False
    assert result["metadata_only"] is True


if __name__ == "__main__":
    test_durable_provider_unavailable_with_no_resolved_assets_stays_unavailable()
    test_durable_provider_unavailable_with_playable_audio_becomes_partial_success()
    test_durable_demo_supabase_placeholder_does_not_count_as_playable()
    print("DURABLE_MEDIA_OUTCOME_ASSET_LINKING_TESTS_PASSED")
