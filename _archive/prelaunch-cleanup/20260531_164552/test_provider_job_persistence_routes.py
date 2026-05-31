
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

status = client.get("/provider-job-persistence/status")
assert status.status_code == 200
status_json = status.json()
assert status_json["provider_job_persistence_ready"] is True

created = client.post(
    "/provider-job-persistence/create",
    json={
        "tenant_id": "route-test-tenant",
        "provider": "openai",
        "job_type": "image_generation",
        "requested_asset_type": "image",
    },
)
assert created.status_code == 200
created_json = created.json()
assert created_json["success"] is True

job_id = created_json["job"]["job_id"]

updated = client.post(
    "/provider-job-persistence/update",
    json={
        "job_id": job_id,
        "status": "completed",
        "result_payload": {"provider_status": "done"},
    },
)
assert updated.status_code == 200
updated_json = updated.json()
assert updated_json["status"] == "completed"

fetched = client.get(f"/provider-job-persistence/job/{job_id}")
assert fetched.status_code == 200
fetched_json = fetched.json()
assert fetched_json["job"]["status"] == "completed"

listed = client.get("/provider-job-persistence/jobs?status=completed")
assert listed.status_code == 200
listed_json = listed.json()
assert listed_json["job_count"] >= 1

events = client.get(f"/provider-job-persistence/events?job_id={job_id}")
assert events.status_code == 200
events_json = events.json()
assert events_json["event_count"] >= 2

print("PROVIDER_JOB_PERSISTENCE_ROUTES_TESTS_PASSED")
print("status_ready", status_json["provider_job_persistence_ready"])
print("created_success", created_json["success"])
print("updated_status", updated_json["status"])
print("listed_job_count", listed_json["job_count"])
print("event_count", events_json["event_count"])
