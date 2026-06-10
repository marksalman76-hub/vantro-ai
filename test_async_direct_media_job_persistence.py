from backend.app.runtime.direct_media_provider_execution_runtime import (
    start_direct_media_provider_job_async,
    get_direct_media_provider_job_status,
)


def test_async_job_status_readback_immediate():
    result = start_direct_media_provider_job_async({
        "job_id": "direct_media_job_async_readback_immediate",
        "agent_id": "social_media_manager_content_creator_agent",
        "provider": "runway",
        "media_type": "video",
        "prompt": "simple test video",
        "owner_approved": False,
    })

    assert result["success"] is True, result
    assert result["accepted"] is True, result
    assert result["job_id"] == "direct_media_job_async_readback_immediate", result
    assert result["credential_values_exposed"] is False, result

    status = get_direct_media_provider_job_status(result["job_id"])
    assert status["job_id"] == result["job_id"], status
    assert status["status"] in {
        "queued",
        "running",
        "blocked_owner_approval_required",
        "completed",
        "provider_failed",
    }, status
    assert status["credential_values_exposed"] is False, status
    assert status["customer_safe"] is True, status


if __name__ == "__main__":
    test_async_job_status_readback_immediate()
    print("ASYNC_DIRECT_MEDIA_JOB_PERSISTENCE_TEST_PASSED")
