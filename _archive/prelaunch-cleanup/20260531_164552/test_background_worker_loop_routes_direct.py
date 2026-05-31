import os
from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)

os.environ.pop("OPENAI_API_KEY", None)
os.environ.pop("REAL_PROVIDER_HTTP_DISPATCH_ENABLED", None)

reset = client.post("/background-worker-loop/reset-for-tests").json()
assert reset["reset"] is True
assert reset["credential_values_exposed"] is False

status = client.get("/background-worker-loop/status").json()
assert status["background_worker_loop_ready"] is True
assert status["real_external_dispatch_enabled"] is False
assert status["credential_values_exposed"] is False

enqueued = client.post(
    "/background-worker-loop/enqueue",
    json={
        "tenant_id": "tenant-test",
        "request_id": "request-test",
        "provider_key": "openai",
        "task_type": "image_generation",
        "payload": {"prompt": "test"},
        "live_execution_requested": True,
        "owner_governed_execution_confirmed": True,
    },
).json()
assert enqueued["enqueued"] is True
assert enqueued["queue_size"] == 1
assert enqueued["live_external_call_executed"] is False
assert enqueued["credential_values_exposed"] is False

queue_item = enqueued["queue_item"]

queue = client.get("/background-worker-loop/queue?tenant_id=tenant-test").json()
assert queue["count"] == 1
assert queue["credential_values_exposed"] is False

dispatch = client.post(
    "/background-worker-loop/dispatch-check",
    json={"queue_item": queue_item},
).json()
assert dispatch["next_state"] == "dispatch_blocked"
assert dispatch["dispatch_allowed"] is False
assert dispatch["live_external_call_executed"] is False

polling = client.post(
    "/background-worker-loop/polling-cycle",
    json={
        "queue_item": queue_item,
        "provider_job_id": "provider-job-123",
        "provider_status": "succeeded",
    },
).json()
assert polling["mapped_state"] == "completed"
assert polling["terminal"] is True
assert polling["credential_values_exposed"] is False

retry = client.post(
    "/background-worker-loop/retry-scheduler",
    json={
        "queue_item": queue_item,
        "failure_code": "provider_timeout",
    },
).json()
assert retry["attempt_count"] == 1
assert retry["retry_allowed"] is True
assert retry["next_state"] == "retry_queued"

complete = client.post(
    "/background-worker-loop/reconcile-completion",
    json={
        "queue_item": queue_item,
        "final_status": "completed",
        "latency_ms": 2500,
    },
).json()
assert complete["reconciled_status"] == "completed"
assert complete["terminal"] is True

cycle = client.post("/background-worker-loop/cycle-once").json()
assert cycle["queue_size"] == 1
assert cycle["live_external_call_executed"] is False
assert cycle["credential_values_exposed"] is False

print("BACKGROUND_WORKER_LOOP_ROUTES_DIRECT_TESTS_PASSED")
print("queue_count", queue["count"])
print("dispatch", dispatch["next_state"], dispatch["dispatch_allowed"])
print("polling", polling["mapped_state"], polling["terminal"])
print("retry", retry["next_state"], retry["next_action"])
print("complete", complete["reconciled_status"])
print("cycle_processed", cycle["processed_count"])
