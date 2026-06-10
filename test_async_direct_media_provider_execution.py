from backend.app.runtime.direct_media_provider_execution_runtime import (
    start_direct_media_provider_job_async,
    get_direct_media_provider_job_status,
)


def test_async_direct_media_provider_owner_gate():
    result = start_direct_media_provider_job_async({
        "job_id": "direct_media_job_async_unit_owner_gate",
        "agent_id": "social_media_manager_content_creator_agent",
        "provider": "runway",
        "media_type": "video",
        "prompt": "simple test video",
        "owner_approved": False,
    })
    assert result["accepted"] is True, result
    status = get_direct_media_provider_job_status(result["job_id"])
    assert status["job_id"] == result["job_id"], status
    assert status["credential_values_exposed"] is False, status


if __name__ == "__main__":
    test_async_direct_media_provider_owner_gate()
    print("ASYNC_DIRECT_MEDIA_PROVIDER_EXECUTION_TEST_PASSED")
