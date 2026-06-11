from backend.app.runtime.direct_media_provider_execution_runtime import (
    compose_direct_media_video_audio,
    direct_media_composition_status,
)


def test_composition_status_safe():
    status = direct_media_composition_status()
    assert status["success"] is True, status
    assert status["credential_values_exposed"] is False, status
    assert "video_plus_audio_to_mp4" in status["supported_composition"], status


def test_composition_requires_source_jobs():
    result = compose_direct_media_video_audio({
        "owner_approved": True,
    })
    assert result["status"] == "blocked_missing_source_jobs", result
    assert result["credential_values_exposed"] is False, result


def test_composition_owner_gate():
    result = compose_direct_media_video_audio({
        "video_job_id": "video",
        "audio_job_id": "audio",
        "owner_approved": False,
    })
    assert result["status"] == "blocked_owner_approval_required", result
    assert result["credential_values_exposed"] is False, result


if __name__ == "__main__":
    test_composition_status_safe()
    test_composition_requires_source_jobs()
    test_composition_owner_gate()
    print("DIRECT_MEDIA_COMPOSITION_RUNTIME_TEST_PASSED")
