import os
from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)

os.environ.pop("DATABASE_URL", None)

status_no_db = client.get("/provider-postgres-extended-ledger-writes/status").json()
assert status_no_db["extended_ledger_write_ready"] is True
assert status_no_db["database_url_present"] is False
assert status_no_db["fallback_storage_active"] is True
assert status_no_db["credential_values_exposed"] is False

event_no_db = client.post(
    "/provider-postgres-extended-ledger-writes/worker-event",
    json={
        "tenant_id": "tenant-test",
        "request_id": "request-test",
        "execution_id": "execution-123",
        "worker_job_id": "worker-123",
        "provider_key": "openai",
        "event_type": "worker_prepared",
        "status": "dispatch_blocked",
        "details": {"safe": True, "secret": "must-not-store"},
    },
).json()
assert event_no_db["persistence_mode"] == "in_memory_fallback"
assert event_no_db["postgres_write_attempted"] is False
assert "secret" not in event_no_db["entry"]["details"]

attempt_no_db = client.post(
    "/provider-postgres-extended-ledger-writes/dispatch-attempt",
    json={
        "tenant_id": "tenant-test",
        "request_id": "request-test",
        "execution_id": "execution-123",
        "worker_job_id": "worker-123",
        "provider_key": "openai",
        "attempt_number": 1,
        "allowed_by_policy": False,
        "result_status": "blocked",
        "reason": "dispatch_disabled",
    },
).json()
assert attempt_no_db["persistence_mode"] == "in_memory_fallback"
assert attempt_no_db["postgres_write_attempted"] is False

retry_no_db = client.post(
    "/provider-postgres-extended-ledger-writes/retry-history",
    json={
        "tenant_id": "tenant-test",
        "request_id": "request-test",
        "execution_id": "execution-123",
        "worker_job_id": "worker-123",
        "provider_key": "openai",
        "attempt_number": 1,
        "failure_code": "provider_timeout",
        "retry_allowed": True,
        "next_action": "queue_retry",
    },
).json()
assert retry_no_db["persistence_mode"] == "in_memory_fallback"

latency_no_db = client.post(
    "/provider-postgres-extended-ledger-writes/latency-metric",
    json={
        "tenant_id": "tenant-test",
        "request_id": "request-test",
        "execution_id": "execution-123",
        "provider_key": "openai",
        "latency_ms": 1234,
        "operation": "dispatch_prepare",
    },
).json()
assert latency_no_db["persistence_mode"] == "in_memory_fallback"

os.environ["DATABASE_URL"] = "postgresql://user:pass@example.com/db"

status_with_db = client.get("/provider-postgres-extended-ledger-writes/status").json()
assert status_with_db["database_url_present"] is True
assert status_with_db["credential_values_exposed"] is False

event_bad_db = client.post(
    "/provider-postgres-extended-ledger-writes/worker-event",
    json={
        "tenant_id": "tenant-test-db",
        "request_id": "request-test-db",
        "execution_id": "execution-456",
        "worker_job_id": "worker-456",
        "provider_key": "openai",
        "event_type": "worker_prepared",
        "status": "dispatch_blocked",
        "details": {"safe": True},
    },
).json()
assert event_bad_db["postgres_write_attempted"] is True
assert event_bad_db["persistence_mode"] in {"postgres", "in_memory_fallback"}
assert event_bad_db["credential_values_exposed"] is False

attempt_bad_db = client.post(
    "/provider-postgres-extended-ledger-writes/dispatch-attempt",
    json={
        "tenant_id": "tenant-test-db",
        "request_id": "request-test-db",
        "execution_id": "execution-456",
        "worker_job_id": "worker-456",
        "provider_key": "openai",
        "attempt_number": 1,
        "allowed_by_policy": False,
        "result_status": "blocked",
        "reason": "dispatch_disabled",
    },
).json()
assert attempt_bad_db["postgres_write_attempted"] is True

retry_bad_db = client.post(
    "/provider-postgres-extended-ledger-writes/retry-history",
    json={
        "tenant_id": "tenant-test-db",
        "request_id": "request-test-db",
        "execution_id": "execution-456",
        "worker_job_id": "worker-456",
        "provider_key": "openai",
        "attempt_number": 1,
        "failure_code": "provider_timeout",
        "retry_allowed": True,
        "next_action": "queue_retry",
    },
).json()
assert retry_bad_db["postgres_write_attempted"] is True

latency_bad_db = client.post(
    "/provider-postgres-extended-ledger-writes/latency-metric",
    json={
        "tenant_id": "tenant-test-db",
        "request_id": "request-test-db",
        "execution_id": "execution-456",
        "provider_key": "openai",
        "latency_ms": 2222,
        "operation": "dispatch_prepare",
    },
).json()
assert latency_bad_db["postgres_write_attempted"] is True

print("PROVIDER_POSTGRES_EXTENDED_LEDGER_WRITE_ROUTES_DIRECT_TESTS_PASSED")
print("status_no_db", status_no_db["database_url_present"], status_no_db["fallback_storage_active"])
print("event_no_db", event_no_db["persistence_mode"], event_no_db["postgres_write_attempted"])
print("attempt_no_db", attempt_no_db["persistence_mode"], attempt_no_db["postgres_write_attempted"])
print("retry_no_db", retry_no_db["persistence_mode"])
print("latency_no_db", latency_no_db["persistence_mode"])
print("status_with_db", status_with_db["database_url_present"], status_with_db["postgres_driver_available"])
print("event_bad_db", event_bad_db["persistence_mode"], event_bad_db["postgres_write_attempted"])
print("attempt_bad_db", attempt_bad_db["persistence_mode"], attempt_bad_db["postgres_write_attempted"])
print("retry_bad_db", retry_bad_db["persistence_mode"], retry_bad_db["postgres_write_attempted"])
print("latency_bad_db", latency_bad_db["persistence_mode"], latency_bad_db["postgres_write_attempted"])
