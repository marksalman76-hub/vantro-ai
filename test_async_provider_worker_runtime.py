
from backend.app.runtime.async_provider_worker_runtime import (
    enqueue_async_provider_job,
    get_async_provider_worker_status,
    process_next_queued_provider_job,
    process_provider_job,
    process_provider_job_batch,
)
from backend.app.runtime.provider_job_persistence_runtime import get_provider_job

status = get_async_provider_worker_status()
assert status["async_provider_worker_ready"] is True
assert status["credential_values_exposed"] is False

queued = enqueue_async_provider_job({
    "tenant_id": "async-worker-test-tenant",
    "execution_id": "execution_async_001",
    "provider": "openai",
    "job_type": "image_generation",
    "requested_asset_type": "image",
})
assert queued["success"] is True
assert queued["status"] == "queued"

job_id = queued["job"]["job_id"]

completed = process_provider_job(job_id)
assert completed["success"] is True
assert completed["status"] == "completed"
assert completed["worker_status"] == "completed"
assert len(completed["asset_records"]) == 1

found = get_provider_job(job_id)
assert found["success"] is True
assert found["job"]["status"] == "completed"
assert len(found["job"]["asset_records"]) == 1

already = process_provider_job(job_id)
assert already["success"] is True
assert already["status"] == "already_completed"

queued_fail = enqueue_async_provider_job({
    "tenant_id": "async-worker-test-tenant",
    "execution_id": "execution_async_002",
    "provider": "openai",
    "job_type": "video_generation",
    "requested_asset_type": "video",
})
failed = process_provider_job(queued_fail["job"]["job_id"], simulate_success=False)
assert failed["success"] is False
assert failed["status"] == "failed"

idle_or_batch = process_provider_job_batch(limit=2)
assert idle_or_batch["success"] is True
assert idle_or_batch["credential_values_exposed"] is False

queued_next = enqueue_async_provider_job({
    "tenant_id": "async-worker-test-tenant",
    "execution_id": "execution_async_003",
    "provider": "openai",
    "job_type": "image_generation",
    "requested_asset_type": "image",
})
next_result = process_next_queued_provider_job()
assert next_result["success"] is True
assert next_result["status"] == "completed"

final_status = get_async_provider_worker_status()
assert final_status["async_provider_worker_ready"] is True

print("ASYNC_PROVIDER_WORKER_RUNTIME_TESTS_PASSED")
print("status_ready", status["async_provider_worker_ready"])
print("queued_status", queued["status"])
print("completed_status", completed["status"])
print("already_status", already["status"])
print("failed_status", failed["status"])
print("batch_status", idle_or_batch["status"])
print("next_status", next_result["status"])
