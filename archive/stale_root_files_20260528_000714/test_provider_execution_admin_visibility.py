
from backend.app.runtime.async_provider_worker_runtime import enqueue_async_provider_job, process_provider_job
from backend.app.runtime.provider_asset_delivery_packet_runtime import create_delivery_packet_from_provider_job
from backend.app.runtime.provider_execution_admin_visibility import (
    get_provider_execution_admin_visibility,
    get_provider_execution_admin_visibility_status,
)
from backend.app.runtime.provider_job_persistence_runtime import create_provider_job, update_provider_job_status
from backend.app.runtime.provider_retry_timeout_orchestration import schedule_provider_job_retry

tenant_id = "provider-execution-admin-visibility-test-tenant"

status = get_provider_execution_admin_visibility_status()
assert status["provider_execution_admin_visibility_ready"] is True
assert status["credential_values_exposed"] is False

queued = create_provider_job({
    "tenant_id": tenant_id,
    "provider": "openai",
    "job_type": "image_generation",
    "requested_asset_type": "image",
})
assert queued["success"] is True

running_job = create_provider_job({
    "tenant_id": tenant_id,
    "provider": "openai",
    "job_type": "video_generation",
    "requested_asset_type": "video",
})
update_provider_job_status(running_job["job"]["job_id"], "running")

failed_job = create_provider_job({
    "tenant_id": tenant_id,
    "provider": "openai",
    "job_type": "image_generation",
    "requested_asset_type": "image",
})
update_provider_job_status(failed_job["job"]["job_id"], "failed", error="provider_failed")

retry_job = create_provider_job({
    "tenant_id": tenant_id,
    "provider": "openai",
    "job_type": "image_generation",
    "requested_asset_type": "image",
})
schedule_provider_job_retry(retry_job["job"]["job_id"], reason="provider_rate_limited", delay_seconds=60)

worker_job = enqueue_async_provider_job({
    "tenant_id": tenant_id,
    "execution_id": "visibility_execution_001",
    "provider": "openai",
    "job_type": "image_generation",
    "requested_asset_type": "image",
})
completed = process_provider_job(worker_job["job"]["job_id"])
assert completed["status"] == "completed"

packet = create_delivery_packet_from_provider_job(worker_job["job"]["job_id"])
assert packet["success"] is True

visibility = get_provider_execution_admin_visibility(tenant_id=tenant_id)
assert visibility["success"] is True
assert visibility["provider_execution_admin_visibility_ready"] is True
assert visibility["summary"]["queued_job_count"] >= 1
assert visibility["summary"]["running_job_count"] >= 1
assert visibility["summary"]["completed_job_count"] >= 1
assert visibility["summary"]["failed_job_count"] >= 1
assert visibility["summary"]["retry_scheduled_job_count"] >= 1
assert visibility["summary"]["delivery_packet_count"] >= 1
assert visibility["credential_values_exposed"] is False

print("PROVIDER_EXECUTION_ADMIN_VISIBILITY_TESTS_PASSED")
print("status_ready", status["provider_execution_admin_visibility_ready"])
print("queued_jobs", visibility["summary"]["queued_job_count"])
print("running_jobs", visibility["summary"]["running_job_count"])
print("completed_jobs", visibility["summary"]["completed_job_count"])
print("failed_jobs", visibility["summary"]["failed_job_count"])
print("retry_scheduled", visibility["summary"]["retry_scheduled_job_count"])
print("delivery_packets", visibility["summary"]["delivery_packet_count"])
