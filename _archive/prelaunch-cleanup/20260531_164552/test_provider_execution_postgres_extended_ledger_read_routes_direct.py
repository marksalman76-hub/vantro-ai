import os
from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)

os.environ.pop("DATABASE_URL", None)

status = client.get("/provider-postgres-extended-ledger-reads/status").json()
assert status["extended_ledger_read_ready"] is True
assert status["fallback_storage_active"] is True
assert status["credential_values_exposed"] is False

record = client.post(
    "/provider-postgres-read-write/execution-record",
    json={
        "tenant_id": "tenant-test",
        "request_id": "request-test",
        "provider_key": "openai",
        "task_type": "image_generation",
        "execution_status": "created",
        "worker_job_id": "worker-123",
    },
).json()
execution_id = record["record"]["execution_id"]

client.post(
    "/provider-postgres-extended-ledger-writes/worker-event",
    json={
        "tenant_id": "tenant-test",
        "request_id": "request-test",
        "execution_id": execution_id,
        "worker_job_id": "worker-123",
        "provider_key": "openai",
        "event_type": "worker_prepared",
        "status": "dispatch_blocked",
        "details": {"safe": True},
    },
)

client.post(
    "/provider-postgres-extended-ledger-writes/dispatch-attempt",
    json={
        "tenant_id": "tenant-test",
        "request_id": "request-test",
        "execution_id": execution_id,
        "worker_job_id": "worker-123",
        "provider_key": "openai",
        "attempt_number": 1,
        "allowed_by_policy": False,
        "result_status": "blocked",
        "reason": "dispatch_disabled",
    },
)

client.post(
    "/provider-postgres-extended-ledger-writes/retry-history",
    json={
        "tenant_id": "tenant-test",
        "request_id": "request-test",
        "execution_id": execution_id,
        "worker_job_id": "worker-123",
        "provider_key": "openai",
        "attempt_number": 1,
        "failure_code": "provider_timeout",
        "retry_allowed": True,
        "next_action": "queue_retry",
    },
)

client.post(
    "/provider-postgres-extended-ledger-writes/latency-metric",
    json={
        "tenant_id": "tenant-test",
        "request_id": "request-test",
        "execution_id": execution_id,
        "provider_key": "openai",
        "latency_ms": 1500,
        "operation": "dispatch_prepare",
    },
)

events = client.get("/provider-postgres-extended-ledger-reads/worker-events?tenant_id=tenant-test").json()
assert events["count"] >= 1
assert events["postgres_read_attempted"] is False
assert events["credential_values_exposed"] is False

attempts = client.get("/provider-postgres-extended-ledger-reads/dispatch-attempts?tenant_id=tenant-test").json()
assert attempts["count"] >= 1
assert attempts["credential_values_exposed"] is False

retries = client.get("/provider-postgres-extended-ledger-reads/retry-history?tenant_id=tenant-test").json()
assert retries["count"] >= 1
assert retries["credential_values_exposed"] is False

latencies = client.get("/provider-postgres-extended-ledger-reads/latency-metrics?tenant_id=tenant-test&provider_key=openai").json()
assert latencies["count"] >= 1
assert latencies["average_latency_ms"] is not None
assert latencies["credential_values_exposed"] is False

os.environ["DATABASE_URL"] = "postgresql://user:pass@example.com/db"

events_db = client.get("/provider-postgres-extended-ledger-reads/worker-events?tenant_id=tenant-test").json()
assert events_db["postgres_read_attempted"] is True
assert events_db["credential_values_exposed"] is False

print("PROVIDER_POSTGRES_EXTENDED_LEDGER_READ_ROUTES_DIRECT_TESTS_PASSED")
print("events", events["count"])
print("attempts", attempts["count"])
print("retries", retries["count"])
print("latencies", latencies["count"], latencies["average_latency_ms"])
print("events_db_attempted", events_db["postgres_read_attempted"])
