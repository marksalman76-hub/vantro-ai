from backend.app.runtime.direct_media_provider_execution_runtime import (
    direct_media_provider_execution_status,
    execute_direct_media_provider_job,
    get_direct_media_provider_job_status,
)


def test_status():
    status = direct_media_provider_execution_status()
    assert status["success"] is True, status
    assert "runway" in status["supported_video_providers"], status
    assert "elevenlabs" in status["supported_audio_providers"], status
    assert status["credential_values_exposed"] is False, status


def test_owner_approval_gate():
    result = execute_direct_media_provider_job({
        "agent_id": "social_media_manager_content_creator_agent",
        "provider": "runway",
        "media_type": "video",
        "prompt": "simple test video",
        "owner_approved": False,
    })
    assert result["status"] == "blocked_owner_approval_required", result
    assert result["credential_values_exposed"] is False, result


def test_missing_provider_gate():
    result = execute_direct_media_provider_job({
        "agent_id": "social_media_manager_content_creator_agent",
        "provider": "not_a_provider",
        "media_type": "video",
        "prompt": "simple test video",
        "owner_approved": True,
    })
    assert result["status"] == "blocked_unsupported_provider", result
    assert result["credential_values_exposed"] is False, result


def test_job_status_readback():
    result = execute_direct_media_provider_job({
        "job_id": "direct_media_job_unit_test_readback",
        "agent_id": "social_media_manager_content_creator_agent",
        "provider": "not_a_provider",
        "media_type": "video",
        "prompt": "simple test video",
        "owner_approved": True,
    })
    status = get_direct_media_provider_job_status(result["job_id"])
    assert status["job_id"] == result["job_id"], status
    assert status["direct_media_provider_execution"] is True, status
    assert status["credential_values_exposed"] is False, status


if __name__ == "__main__":
    test_status()
    test_owner_approval_gate()
    test_missing_provider_gate()
    test_job_status_readback()
    print("DIRECT_MEDIA_PROVIDER_EXECUTION_RUNTIME_TEST_PASSED")
