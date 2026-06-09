from pathlib import Path
import tempfile

from backend.app.runtime import async_media_job_foundation as media_jobs


def test_enqueue_media_job_immediately_schedules_worker_queue():
    old_store = media_jobs.STORE
    old_enqueue_creative_media_job_for_worker = media_jobs.enqueue_creative_media_job_for_worker

    calls = []

    def fake_enqueue_creative_media_job_for_worker(job):
        calls.append(job)
        return {
            "success": True,
            "scheduled": True,
            "status": "queued",
            "durable_queue_job_id": "durable_media_queue_test_123",
            "queue_id": "durable_media_queue_test_123",
            "job_id": "durable_media_queue_test_123",
            "queue_name": media_jobs.CREATIVE_MEDIA_GENERATION_QUEUE,
        }

    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            media_jobs.STORE = Path(temp_dir)
            media_jobs.STORE.mkdir(parents=True, exist_ok=True)
            media_jobs.enqueue_creative_media_job_for_worker = fake_enqueue_creative_media_job_for_worker

            job = media_jobs.enqueue_media_job(
                task="Create a fresh short-form video ad with audio and avatar.",
                agent_id="social_media_manager_content_creator_agent",
                tenant_id="owner_admin",
                include_image=True,
                include_audio=True,
                include_video=True,
                include_avatar=True,
            )

            assert job["status"] == "queued"
            assert job["worker_queue_acceptance_checked"] is True
            assert job["worker_queue_scheduled"] is True
            assert job["worker_queue_status"] == "queued"
            assert job["durable_queue_job_id"] == "durable_media_queue_test_123"
            assert job["durable_queue_name"] == media_jobs.CREATIVE_MEDIA_GENERATION_QUEUE
            assert job["durable_queue_status"] == "queued"
            assert job["credential_values_exposed"] is False

            assert calls, "enqueue_creative_media_job_for_worker was not called"
            assert calls[0]["job_id"] == job["job_id"]
            assert calls[0]["agent_id"] == "social_media_manager_content_creator_agent"

            persisted = media_jobs.read_media_job(job["job_id"], include_internal=True)
            assert persisted["worker_queue_acceptance_checked"] is True
            assert persisted["worker_queue_scheduled"] is True
            assert persisted["durable_queue_job_id"] == "durable_media_queue_test_123"
            assert persisted["durable_queue_name"] == media_jobs.CREATIVE_MEDIA_GENERATION_QUEUE
        finally:
            media_jobs.enqueue_creative_media_job_for_worker = old_enqueue_creative_media_job_for_worker
            media_jobs.STORE = old_store


if __name__ == "__main__":
    test_enqueue_media_job_immediately_schedules_worker_queue()
    print("MEDIA_JOB_AUTO_WORKER_QUEUE_ACCEPTANCE_TEST_PASSED")