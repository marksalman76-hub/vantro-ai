from backend.app.runtime.async_media_job_foundation import _asset_delivery_summary


def test_asset_delivery_summary_preserves_media_job_correlation_fields():
    asset = {
        "asset_id": "audio_asset_test",
        "media_job_id": "media_job_test_123",
        "job_id": "media_job_test_123",
        "task_id": "media_job_test_123",
        "durable_queue_job_id": "queue_job_test_456",
        "media_type": "audio",
        "asset_type": "audio",
        "provider": "test_provider",
        "metadata_only": True,
    }

    summary = _asset_delivery_summary(asset)

    assert summary["asset_id"] == "audio_asset_test"
    assert summary["media_job_id"] == "media_job_test_123"
    assert summary["job_id"] == "media_job_test_123"
    assert summary["task_id"] == "media_job_test_123"
    assert summary["durable_queue_job_id"] == "queue_job_test_456"
    assert summary["metadata_only"] is True
    assert summary["playable"] is False


if __name__ == "__main__":
    test_asset_delivery_summary_preserves_media_job_correlation_fields()
    print("ASSET_DELIVERY_SUMMARY_CORRELATION_FIELDS_TEST_PASSED")
