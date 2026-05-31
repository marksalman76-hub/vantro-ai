
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.runtime.provider_job_persistence_runtime import create_provider_job

client = TestClient(app)

status = client.get("/provider-retry-timeout/status")
assert status.status_code == 200
status_json = status.json()
assert status_json["provider_retry_timeout_orchestration_ready"] is True

created = create_provider_job({
    "tenant_id": "retry-route-tenant",
    "provider": "openai",
    "job_type": "image_generation",
    "requested_asset_type": "image",
})

job_id = created["job"]["job_id"]

retry = client.post(
    "/provider-retry-timeout/schedule-retry",
    json={
        "job_id": job_id,
        "reason": "provider_rate_limit",
        "delay_seconds": 1,
    },
)
assert retry.status_code == 200
retry_json = retry.json()
assert retry_json["status"] == "retry_scheduled"

ready = client.get("/provider-retry-timeout/retry-ready")
assert ready.status_code == 200
ready_json = ready.json()
assert ready_json["success"] is True

requeue = client.post(
    "/provider-retry-timeout/requeue",
    json={"limit": 5},
)
assert requeue.status_code == 200
requeue_json = requeue.json()
assert requeue_json["status"] == "requeued"

timeout = client.post(
    "/provider-retry-timeout/mark-timeout",
    json={
        "job_id": job_id,
        "reason": "provider_timeout",
    },
)
assert timeout.status_code == 200
timeout_json = timeout.json()
assert timeout_json["status"] == "timed_out"

scan = client.post(
    "/provider-retry-timeout/scan-timeouts",
    json={"timeout_seconds": 1},
)
assert scan.status_code == 200
scan_json = scan.json()
assert scan_json["status"] == "timeout_scan_completed"

print("PROVIDER_RETRY_TIMEOUT_ROUTES_TESTS_PASSED")
print("status_ready", status_json["provider_retry_timeout_orchestration_ready"])
print("retry_status", retry_json["status"])
print("ready_success", ready_json["success"])
print("requeue_status", requeue_json["status"])
print("timeout_status", timeout_json["status"])
print("scan_status", scan_json["status"])
