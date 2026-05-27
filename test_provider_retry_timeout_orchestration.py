
from backend.app.runtime.provider_job_persistence_runtime import (
    create_provider_job,
    get_provider_job,
    update_provider_job_status,
)
from backend.app.runtime.provider_retry_timeout_orchestration import (
    get_provider_retry_timeout_status,
    list_retry_ready_provider_jobs,
    mark_provider_job_timed_out,
    requeue_retry_ready_provider_jobs,
    schedule_provider_job_retry,
)

status = get_provider_retry_timeout_status()
assert status["provider_retry_timeout_orchestration_ready"] is True
assert status["credential_values_exposed"] is False

created = create_provider_job({
    "tenant_id": "retry-timeout-test-tenant",
    "provider": "openai",
    "job_type": "image_generation",
    "requested_asset_type": "image",
    "max_attempts": 3,
})
job_id = created["job"]["job_id"]

running = update_provider_job_status(job_id, "running")
assert running["status"] == "running"

retry = schedule_provider_job_retry(job_id, reason="provider_rate_limited", delay_seconds=1)
assert retry["success"] is True
assert retry["status"] == "retry_scheduled"
assert retry["job"]["next_retry_at"]

ready = list_retry_ready_provider_jobs()
assert ready["success"] is True

requeued = requeue_retry_ready_provider_jobs(limit=5)
assert requeued["success"] is True
assert requeued["status"] == "requeued"

timed = mark_provider_job_timed_out(job_id)
assert timed["success"] is True
assert timed["status"] == "timed_out"

found = get_provider_job(job_id)
assert found["success"] is True
assert found["job"]["status"] == "timed_out"

exhausted_job = create_provider_job({
    "tenant_id": "retry-timeout-test-tenant",
    "provider": "openai",
    "job_type": "video_generation",
    "requested_asset_type": "video",
    "attempt_count": 3,
    "max_attempts": 3,
})
exhausted = schedule_provider_job_retry(exhausted_job["job"]["job_id"], reason="provider_failed")
assert exhausted["success"] is False
assert exhausted["status"] == "retry_exhausted"

print("PROVIDER_RETRY_TIMEOUT_ORCHESTRATION_TESTS_PASSED")
print("status_ready", status["provider_retry_timeout_orchestration_ready"])
print("retry_status", retry["status"])
print("ready_count", ready["ready_count"])
print("requeued_status", requeued["status"])
print("timed_status", timed["status"])
print("exhausted_status", exhausted["status"])
