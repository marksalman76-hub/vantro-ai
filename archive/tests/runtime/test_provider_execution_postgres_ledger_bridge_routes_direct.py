import os
from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)

os.environ.pop("DATABASE_URL", None)

reset = client.post("/provider-postgres-ledger-bridge/reset-for-tests").json()
assert reset["reset"] is True
assert reset["credential_values_exposed"] is False

status = client.get("/provider-postgres-ledger-bridge/status").json()
assert status["bridge_ready"] is True
assert status["database_url_present"] is False
assert status["in_memory_fallback_enabled"] is True
assert status["credential_values_exposed"] is False

schema = client.get("/provider-postgres-ledger-bridge/schema").json()
assert schema["schema_sql_present"] is True
assert "CREATE TABLE IF NOT EXISTS provider_execution_records" in schema["sql"]
assert schema["credential_values_exposed"] is False

apply_no_db = client.post("/provider-postgres-ledger-bridge/apply-schema").json()
assert apply_no_db["status"] == "skipped"
assert apply_no_db["reason"] == "DATABASE_URL_missing"
assert apply_no_db["fallback_storage_active"] is True

record_bridge = client.post(
    "/provider-postgres-ledger-bridge/persist-execution-record",
    json={
        "tenant_id": "tenant-test",
        "request_id": "request-test",
        "provider_key": "openai",
        "task_type": "image_generation",
        "execution_status": "created",
        "worker_job_id": "worker-123",
    },
).json()
record = record_bridge["record"]
assert record_bridge["persistence_mode"] == "in_memory_fallback"
assert record_bridge["postgres_write_attempted"] is False
assert record["execution_status"] == "created"

event_bridge = client.post(
    "/provider-postgres-ledger-bridge/persist-worker-event",
    json={
        "tenant_id": "tenant-test",
        "request_id": "request-test",
        "execution_id": record["execution_id"],
        "worker_job_id": "worker-123",
        "provider_key": "openai",
        "event_type": "worker_prepared",
        "status": "dispatch_blocked",
        "details": {"safe": True, "secret": "must-not-store"},
    },
).json()
assert event_bridge["entry"]["event_type"] == "worker_prepared"
assert "secret" not in event_bridge["entry"]["details"]

attempt_bridge = client.post(
    "/provider-postgres-ledger-bridge/persist-dispatch-attempt",
    json={
        "tenant_id": "tenant-test",
        "request_id": "request-test",
        "execution_id": record["execution_id"],
        "worker_job_id": "worker-123",
        "provider_key": "openai",
        "attempt_number": 1,
        "allowed_by_policy": False,
        "result_status": "blocked",
        "reason": "dispatch_disabled",
    },
).json()
assert attempt_bridge["attempt"]["allowed_by_policy"] is False

retry_bridge = client.post(
    "/provider-postgres-ledger-bridge/persist-retry-history",
    json={
        "tenant_id": "tenant-test",
        "request_id": "request-test",
        "execution_id": record["execution_id"],
        "worker_job_id": "worker-123",
        "provider_key": "openai",
        "attempt_number": 1,
        "failure_code": "provider_timeout",
        "retry_allowed": True,
        "next_action": "queue_retry",
    },
).json()
assert retry_bridge["retry"]["retry_allowed"] is True

metric_bridge = client.post(
    "/provider-postgres-ledger-bridge/persist-latency-metric",
    json={
        "tenant_id": "tenant-test",
        "request_id": "request-test",
        "execution_id": record["execution_id"],
        "provider_key": "openai",
        "latency_ms": 1234,
        "operation": "dispatch_prepare",
    },
).json()
assert metric_bridge["metric"]["latency_ms"] == 1234

summary = client.get("/provider-postgres-ledger-bridge/summary").json()
assert summary["execution_records"]["count"] == 1
assert summary["worker_events"]["count"] == 1
assert summary["dispatch_attempts"]["count"] == 1
assert summary["retry_history"]["count"] == 1
assert summary["latency_metrics"]["count"] == 1
assert summary["credential_values_exposed"] is False

os.environ["DATABASE_URL"] = "postgresql://user:pass@example.com/db"

status_with_db = client.get("/provider-postgres-ledger-bridge/status").json()
assert status_with_db["database_url_present"] is True

apply_with_db = client.post("/provider-postgres-ledger-bridge/apply-schema").json()
assert apply_with_db["status"] == "prepared"
assert apply_with_db["reason"] == "DATABASE_URL_present_driver_application_pending"
assert apply_with_db["applied"] is False

print("PROVIDER_POSTGRES_LEDGER_BRIDGE_ROUTES_DIRECT_TESTS_PASSED")
print("database_url_present_initial", status["database_url_present"])
print("schema_available", schema["schema_sql_present"])
print("apply_without_db", apply_no_db["status"], apply_no_db["reason"])
print("record_mode", record_bridge["persistence_mode"])
print("summary_counts", summary["execution_records"]["count"], summary["worker_events"]["count"], summary["dispatch_attempts"]["count"], summary["retry_history"]["count"], summary["latency_metrics"]["count"])
print("database_url_present_after", status_with_db["database_url_present"])
print("apply_with_db", apply_with_db["status"], apply_with_db["reason"])
