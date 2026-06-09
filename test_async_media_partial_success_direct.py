
from backend.app.runtime.async_media_job_foundation import (
    _asset_delivery_summary,
    _asset_success_summary,
    _delivery_asset_playable,
    _delivery_asset_persisted_real,
)


def test_real_supabase_audio_delivery_counts_as_playable_and_persisted():
    raw_asset = {
        "asset_id": "audio_asset_real",
        "asset_type": "audio",
        "media_type": "audio",
        "provider": "elevenlabs",
        "provider_key": "elevenlabs",
        "status": "completed",
        "persistence": {
            "asset_id": "audio_asset_real",
            "preview_ready": True,
            "download_ready": True,
            "playable": True,
            "signed_delivery_created": True,
            "provider_asset_url": "https://abc.supabase.co/storage/v1/object/public/creative-media-outputs/audio.mp3",
            "preview_url": "https://api.trance-formation.com.au/asset-delivery/preview/audio_asset_real",
            "download_url": "https://api.trance-formation.com.au/asset-delivery/download/audio_asset_real",
        },
    }

    asset = _asset_delivery_summary(raw_asset)
    assert _delivery_asset_playable(asset) is True
    assert _delivery_asset_persisted_real(asset) is True

    summary = _asset_success_summary([asset])
    assert summary["playable_asset_count"] == 1
    assert summary["persisted_asset_count"] == 1
    assert summary["signed_delivery_created"] is True


def test_metadata_only_runway_asset_does_not_count_as_playable():
    raw_asset = {
        "asset_id": "video_asset_meta",
        "asset_type": "video",
        "media_type": "video",
        "provider": "runway",
        "provider_key": "runway",
        "status": "provider_unavailable",
        "metadata_only": True,
        "provider_asset_url": "",
    }

    asset = _asset_delivery_summary(raw_asset)
    assert _delivery_asset_playable(asset) is False
    assert _delivery_asset_persisted_real(asset) is False

    summary = _asset_success_summary([asset])
    assert summary["playable_asset_count"] == 0
    assert summary["persisted_asset_count"] == 0


def test_example_url_is_not_playable_even_with_signed_flag():
    raw_asset = {
        "asset_id": "video_asset_fake",
        "asset_type": "video",
        "media_type": "video",
        "provider": "runway",
        "provider_key": "runway",
        "status": "completed",
        "signed_delivery_created": True,
        "provider_asset_url": "https://example.com/generated/video.mp4",
    }

    asset = _asset_delivery_summary(raw_asset)
    assert _delivery_asset_playable(asset) is False
    assert _delivery_asset_persisted_real(asset) is False


if __name__ == "__main__":
    test_real_supabase_audio_delivery_counts_as_playable_and_persisted()
    test_metadata_only_runway_asset_does_not_count_as_playable()
    test_example_url_is_not_playable_even_with_signed_flag()
    print("ASYNC_MEDIA_PARTIAL_SUCCESS_DIRECT_TESTS_PASSED")
