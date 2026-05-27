from backend.app.runtime.async_provider_job_runtime import (
    create_async_provider_job,
    get_async_provider_job,
    list_async_provider_jobs,
    update_async_provider_job_status,
    mark_async_provider_job_retry,
)

job = create_async_provider_job(
    tenant_id="test-tenant",
    actor_role="owner",
    provider_key="openai",
    capability="image_generation",
    request_payload={"prompt": "test"},
)

assert job["status"] == "queued"
assert job["credential_values_exposed"] is False
assert job["customer_safe"] is True
assert job["owner_approval_required"] is True

fetched = get_async_provider_job(job["job_id"])
assert fetched["found"] is True
assert fetched["job_id"] == job["job_id"]

updated = update_async_provider_job_status(
    job_id=job["job_id"],
    status="running",
    provider_job_id="provider-test-001",
    provider_status="submitted",
)
assert updated["updated"] is True
assert updated["status"] == "running"
assert updated["provider_job_id"] == "provider-test-001"

retry = mark_async_provider_job_retry(job["job_id"], "temporary_provider_error")
assert retry["updated"] is True
assert retry["retry_count"] == 1
assert retry["status"] == "queued"

listed = list_async_provider_jobs(tenant_id="test-tenant")
assert listed["job_runtime"] == "async_provider_job_runtime_v1"
assert listed["job_count"] >= 1
assert listed["credential_values_exposed"] is False

print("ASYNC_PROVIDER_JOB_RUNTIME_TEST_PASSED")
print("job_id =", job["job_id"])
print("job_count =", listed["job_count"])
