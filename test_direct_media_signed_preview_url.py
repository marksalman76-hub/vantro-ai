from backend.app.runtime.direct_media_provider_execution_runtime import _normalise_provider_result


def test_signed_preview_url_is_preserved():
    job = {
        "job_id": "direct_media_job_signed_preview_unit",
        "provider": "runway",
        "media_type": "video",
        "customer_safe": True,
        "credential_values_exposed": False,
    }

    provider_result = {
        "success": True,
        "provider": "runway",
        "status": "video_task_completed",
        "output": "AwaitableSucceeded(output=['https://example.cloudfront.net/video.mp4?_jwt=SIGNEDTOKEN'], status='SUCCEEDED')",
        "video_url_preview": "https://example.cloudfront.net/video.mp4",
        "video_saved": True,
        "video_url_found": True,
        "external_action_performed": True,
        "live_provider_call_triggered": True,
        "credential_values_exposed": False,
    }

    result = _normalise_provider_result(job=job, provider_result=provider_result, media_type="video")
    assert result["preview_url"] == "https://example.cloudfront.net/video.mp4?_jwt=SIGNEDTOKEN", result
    assert result["signed_preview_url"] == "https://example.cloudfront.net/video.mp4?_jwt=SIGNEDTOKEN", result
    assert result["playable"] is True, result
    assert result["credential_values_exposed"] is False, result


if __name__ == "__main__":
    test_signed_preview_url_is_preserved()
    print("DIRECT_MEDIA_SIGNED_PREVIEW_URL_TEST_PASSED")
