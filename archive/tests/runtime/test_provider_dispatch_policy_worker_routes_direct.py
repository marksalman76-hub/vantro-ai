import os
from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)

os.environ.pop("OPENAI_API_KEY", None)
os.environ.pop("REAL_PROVIDER_HTTP_DISPATCH_ENABLED", None)

status = client.get("/provider-dispatch-policy/status").json()
assert status["real_dispatch_globally_enabled"] is False
assert status["requires_owner_governed_execution_confirmed"] is True
assert status["credential_values_exposed"] is False

policy = client.post(
    "/provider-dispatch-policy/evaluate/openai",
    json={
        "tenant_id": "tenant-test",
        "request_id": "request-test",
        "prompt": "test",
        "live_execution_requested": True,
        "owner_governed_execution_confirmed": True,
    },
).json()
assert policy["dispatch_allowed"] is False
assert policy["reason"] == "real_provider_http_dispatch_globally_disabled"
assert policy["live_external_call_executed"] is False
assert policy["credential_values_exposed"] is False

foundation = client.get("/provider-worker-foundation/status").json()
assert foundation["worker_foundation_ready"] is True
assert foundation["real_background_dispatch_enabled"] is False
assert foundation["credential_values_exposed"] is False

worker_blocked = client.post(
    "/provider-worker-foundation/create-job/openai",
    json={
        "tenant_id": "tenant-test",
        "request_id": "request-test",
        "task_type": "image_generation",
        "payload": {"prompt": "test"},
        "live_execution_requested": True,
        "owner_governed_execution_confirmed": True,
    },
).json()
assert worker_blocked["worker_state"] == "dispatch_blocked"
assert worker_blocked["next_action"] == "hold_for_policy_or_credentials"
assert worker_blocked["live_external_call_executed"] is False
assert worker_blocked["credential_values_exposed"] is False

os.environ["OPENAI_API_KEY"] = "test-secret-not-exposed"

still_blocked = client.post(
    "/provider-worker-foundation/create-job/openai",
    json={
        "tenant_id": "tenant-test",
        "request_id": "request-test",
        "task_type": "image_generation",
        "payload": {"prompt": "test"},
        "live_execution_requested": True,
        "owner_governed_execution_confirmed": True,
    },
).json()
assert still_blocked["worker_state"] == "dispatch_blocked"
assert still_blocked["dispatch_policy"]["http_packet_status"] == "ready_for_real_http_dispatch"
assert still_blocked["dispatch_policy"]["reason"] == "real_provider_http_dispatch_globally_disabled"

os.environ["REAL_PROVIDER_HTTP_DISPATCH_ENABLED"] = "true"

ready_worker = client.post(
    "/provider-worker-foundation/create-job/openai",
    json={
        "tenant_id": "tenant-test",
        "request_id": "request-test",
        "task_type": "image_generation",
        "payload": {"prompt": "test"},
        "live_execution_requested": True,
        "owner_governed_execution_confirmed": True,
    },
).json()
assert ready_worker["worker_state"] == "ready_for_worker_dispatch"
assert ready_worker["next_action"] == "queue_real_provider_dispatch"
assert ready_worker["live_external_call_executed"] is False

advanced = client.post(
    "/provider-worker-foundation/advance-job/openai",
    json={
        "worker_job_id": ready_worker["worker_job_id"],
        "tenant_id": "tenant-test",
        "request_id": "request-test",
        "current_state": ready_worker["worker_state"],
    },
).json()
assert advanced["next_state"] == "dispatch_waiting_final_enablement"
assert advanced["next_action"] == "wait_for_final_policy_enablement"
assert advanced["credential_values_exposed"] is False

retry = client.post(
    "/provider-worker-foundation/advance-job/openai",
    json={
        "worker_job_id": ready_worker["worker_job_id"],
        "tenant_id": "tenant-test",
        "request_id": "request-test",
        "current_state": "dispatch_blocked",
        "attempt_count": 1,
        "failure_code": "provider_timeout",
    },
).json()
assert retry["next_state"] == "retry_queued"
assert retry["next_action"] == "queue_retry"
assert retry["credential_values_exposed"] is False

print("PROVIDER_DISPATCH_POLICY_WORKER_ROUTES_DIRECT_TESTS_PASSED")
print("policy_enabled", status["real_dispatch_globally_enabled"])
print("policy_result", policy["dispatch_allowed"], policy["reason"])
print("foundation_ready", foundation["worker_foundation_ready"])
print("worker_blocked", worker_blocked["worker_state"], worker_blocked["next_action"])
print("still_blocked", still_blocked["dispatch_policy"]["http_packet_status"], still_blocked["dispatch_policy"]["reason"])
print("ready_worker", ready_worker["worker_state"], ready_worker["next_action"])
print("advanced_worker", advanced["next_state"], advanced["next_action"])
print("retry_worker", retry["next_state"], retry["next_action"])
