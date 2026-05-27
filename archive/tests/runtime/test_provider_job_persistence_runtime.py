
from backend.app.runtime.provider_job_persistence_runtime import (
    create_provider_job,
    get_provider_job,
    get_provider_job_persistence_status,
    list_provider_job_events,
    list_provider_jobs,
    update_provider_job_status,
)

status = get_provider_job_persistence_status()
assert status["provider_job_persistence_ready"] is True
assert status["credential_values_exposed"] is False

created = create_provider_job({
    "tenant_id": "test-provider-job-tenant",
    "execution_id": "execution_001",
    "provider": "openai",
    "job_type": "image_generation",
    "requested_asset_type": "image",
    "request_payload": {"prompt": "Safe commercial product image test"},
})
assert created["success"] is True
assert created["status"] == "queued"
assert created["job"]["credential_values_exposed"] is False

job_id = created["job"]["job_id"]

running = update_provider_job_status(
    job_id,
    "running",
    provider_job_reference="provider_ref_001",
)
assert running["success"] is True
assert running["status"] == "running"
assert running["job"]["attempt_count"] == 1

completed = update_provider_job_status(
    job_id,
    "completed",
    result_payload={"provider_status": "succeeded"},
    asset_records=[
        {
            "asset_id": "asset_001",
            "asset_type": "image",
            "delivery_status": "ready",
            "credential_values_exposed": False,
            "customer_safe": True,
        }
    ],
)
assert completed["success"] is True
assert completed["status"] == "completed"
assert len(completed["job"]["asset_records"]) == 1

found = get_provider_job(job_id)
assert found["success"] is True
assert found["job"]["status"] == "completed"

listed = list_provider_jobs(status="completed")
assert listed["success"] is True
assert listed["job_count"] >= 1

events = list_provider_job_events(job_id)
assert events["success"] is True
assert events["event_count"] >= 3
assert events["credential_values_exposed"] is False

invalid = update_provider_job_status(job_id, "bad_status")
assert invalid["success"] is False
assert invalid["error"] == "invalid_provider_job_status"

print("PROVIDER_JOB_PERSISTENCE_RUNTIME_TESTS_PASSED")
print("status_ready", status["provider_job_persistence_ready"])
print("created_status", created["status"])
print("running_status", running["status"])
print("completed_status", completed["status"])
print("listed_job_count", listed["job_count"])
print("event_count", events["event_count"])
print("invalid_error", invalid["error"])
