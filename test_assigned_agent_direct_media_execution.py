import os
import time
from backend.app.runtime import async_media_job_foundation as media


def test_assigned_agent_direct_media_execution_scheduler(monkeypatch):
    old_env = os.environ.get("ASSIGNED_AGENT_DIRECT_MEDIA_EXECUTION_ENABLED")
    os.environ["ASSIGNED_AGENT_DIRECT_MEDIA_EXECUTION_ENABLED"] = "true"

    calls = []

    def fake_process_media_job(job):
        calls.append(job)
        media._write_assigned_agent_direct_execution_state(
            job["job_id"],
            {
                "status": "completed",
                "lifecycle": "completed",
                "final_assets": [{"asset_id": "asset_test", "playable": True}],
                "final_asset_ids": ["asset_test"],
                "playable_asset_count": 1,
                "credential_values_exposed": False,
            },
        )
        return {
            "success": True,
            "job": {
                "job_id": job["job_id"],
                "final_assets": [{"asset_id": "asset_test", "playable": True}],
                "final_asset_ids": ["asset_test"],
            },
        }

    monkeypatch.setattr(media, "process_media_job", fake_process_media_job)

    result = media._schedule_assigned_agent_direct_media_execution(
        {
            "job_id": "media_job_direct_test",
            "task": "test task",
            "agent_id": "social_media_manager_content_creator_agent",
            "tenant_id": "owner_admin",
            "include_image": True,
            "include_audio": True,
            "include_video": True,
            "include_avatar": False,
            "credential_values_exposed": False,
        }
    )

    assert result["scheduled"] is True, result
    assert result["status"] == "assigned_agent_direct_execution_scheduled", result

    for _ in range(30):
        if calls:
            break
        time.sleep(0.1)

    assert calls, "direct execution thread did not invoke process_media_job"
    assert calls[0]["agent_id"] == "social_media_manager_content_creator_agent"

    if old_env is None:
        os.environ.pop("ASSIGNED_AGENT_DIRECT_MEDIA_EXECUTION_ENABLED", None)
    else:
        os.environ["ASSIGNED_AGENT_DIRECT_MEDIA_EXECUTION_ENABLED"] = old_env


if __name__ == "__main__":
    try:
        import pytest
        raise SystemExit(pytest.main([__file__]))
    except ImportError:
        print("pytest not installed; running direct smoke only")
        print("ASSIGNED_AGENT_DIRECT_MEDIA_EXECUTION_TEST_REQUIRES_PYTEST")
