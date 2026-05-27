import os
from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)

os.environ.pop("OPENAI_API_KEY", None)
os.environ.pop("REAL_PROVIDER_HTTP_DISPATCH_ENABLED", None)

reset = client.post("/provider-execution-ledger/reset-for-tests").json()
assert reset["reset"] is True
assert reset["credential_values_exposed"] is False

initial = client.get("/provider-execution-ledger/status").json()
assert initial["persistence_runtime_ready"] is True
assert initial["storage_mode"] == "in_memory_safe_fallback"
assert initial["execution_record_count"] == 0

created = client.post(
    "/provider-execution-ledger/create-record",
    json={
        "tenant_id": "tenant-test",
        "request_id": "request-test",
        "provider_key": "openai",
        "task_type": "image_generation",
        "execution_status": "created",
        "worker_job_id": "worker-123",
    },
).json()
assert created["execution_status"] == "created"
assert created["credential_values_exposed"] is False

updated = client.post(
    f"/provider-execution-ledger/update-record/{created['execution_id']}",
    json={
        "execution_status": "dispatch_blocked",
        "provider_job_id": "provider-job-123",
        "extra": {
            "safe_note": "ok",
            "api_key": "must-not-store",
            "token": "must-not-store",
        },
    },
).json()
assert updated["execution_status"] == "dispatch_blocked"
assert "api_key" not in updated.get("extra", {})
assert "token" not in updated.get("extra", {})

fetched = client.get(f"/provider-execution-ledger/record/{created['execution_id']}").json()
assert fetched["execution_id"] == created["execution_id"]

records = client.get("/provider-execution-ledger/records?tenant_id=tenant-test").json()
assert records["count"] == 1

worker_blocked = client.post(
    "/provider-worker-foundation/create-job/openai",
    json={
        "tenant_id": "tenant-test",
        "request_id": "request-worker-test",
        "task_type": "image_generation",
        "payload": {"prompt": "test"},
        "live_execution_requested": True,
        "owner_governed_execution_confirmed": True,
    },
).json()
assert worker_blocked["worker_state"] == "dispatch_blocked"
assert "execution_record" in worker_blocked
assert "ledger_entry" in worker_blocked
assert "dispatch_attempt" in worker_blocked
assert "latency_metric" in worker_blocked
assert worker_blocked["credential_values_exposed"] is False

worker_events = client.get("/provider-execution-ledger/worker-events?tenant_id=tenant-test").json()
assert worker_events["count"] >= 1

attempts = client.get("/provider-execution-ledger/dispatch-attempts?tenant_id=tenant-test").json()
assert attempts["count"] >= 1

latencies = client.get("/provider-execution-ledger/latency-metrics?tenant_id=tenant-test&provider_key=openai").json()
assert latencies["count"] >= 1

advanced_retry = client.post(
    "/provider-worker-foundation/advance-job/openai",
    json={
        "worker_job_id": worker_blocked["worker_job_id"],
        "tenant_id": "tenant-test",
        "request_id": "request-worker-test",
        "current_state": "dispatch_blocked",
        "attempt_count": 1,
        "failure_code": "provider_timeout",
    },
).json()
assert advanced_retry["next_state"] == "retry_queued"
assert "execution_record" in advanced_retry
assert "ledger_entry" in advanced_retry
assert "retry_record" in advanced_retry
assert advanced_retry["credential_values_exposed"] is False

retries = client.get("/provider-execution-ledger/retry-history?tenant_id=tenant-test").json()
assert retries["count"] >= 1

final = client.get("/provider-execution-ledger/status").json()
assert final["execution_record_count"] >= 3
assert final["worker_event_count"] >= 2
assert final["dispatch_attempt_count"] >= 1
assert final["retry_history_count"] >= 1
assert final["latency_metric_count"] >= 1
assert final["credential_values_exposed"] is False

print("PROVIDER_EXECUTION_LEDGER_ROUTES_WORKER_BRIDGE_DIRECT_TESTS_PASSED")
print("created_execution", created["execution_id"])
print("updated_status", updated["execution_status"])
print("worker_state", worker_blocked["worker_state"])
print("worker_events", worker_events["count"])
print("attempts", attempts["count"])
print("latencies", latencies["count"])
print("retry_state", advanced_retry["next_state"])
print("retries", retries["count"])
print("final_counts", final["execution_record_count"], final["worker_event_count"], final["dispatch_attempt_count"], final["retry_history_count"], final["latency_metric_count"])
