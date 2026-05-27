import os

from backend.app.runtime.provider_execution_postgres_ledger_bridge import (
    apply_provider_ledger_schema_if_possible,
    get_provider_ledger_schema_sql,
    persist_dispatch_attempt_bridge,
    persist_latency_metric_bridge,
    persist_provider_execution_record_bridge,
    persist_retry_history_bridge,
    persist_worker_event_bridge,
    provider_postgres_bridge_summary,
    provider_postgres_ledger_bridge_status,
    reset_provider_postgres_bridge_fallback_for_tests,
)

os.environ.pop("DATABASE_URL", None)

reset = reset_provider_postgres_bridge_fallback_for_tests()
assert reset["reset"] is True
assert reset["credential_values_exposed"] is False

status = provider_postgres_ledger_bridge_status()
assert status["bridge_ready"] is True
assert status["database_url_present"] is False
assert status["in_memory_fallback_enabled"] is True
assert status["credential_values_exposed"] is False

schema = get_provider_ledger_schema_sql()
assert schema["schema_sql_present"] is True
assert "CREATE TABLE IF NOT EXISTS provider_execution_records" in schema["sql"]
assert schema["credential_values_exposed"] is False

applied = apply_provider_ledger_schema_if_possible()
assert applied["status"] == "skipped"
assert applied["reason"] == "DATABASE_URL_missing"
assert applied["fallback_storage_active"] is True

record_bridge = persist_provider_execution_record_bridge(
    tenant_id="tenant-test",
    request_id="request-test",
    provider_key="openai",
    task_type="image_generation",
    execution_status="created",
    worker_job_id="worker-123",
)
record = record_bridge["record"]
assert record_bridge["persistence_mode"] == "in_memory_fallback"
assert record_bridge["postgres_write_attempted"] is False
assert record["execution_status"] == "created"

event_bridge = persist_worker_event_bridge(
    tenant_id="tenant-test",
    request_id="request-test",
    execution_id=record["execution_id"],
    worker_job_id="worker-123",
    provider_key="openai",
    event_type="worker_prepared",
    status="dispatch_blocked",
    details={"safe": True, "secret": "must-not-store"},
)
assert event_bridge["entry"]["event_type"] == "worker_prepared"
assert "secret" not in event_bridge["entry"]["details"]

attempt_bridge = persist_dispatch_attempt_bridge(
    tenant_id="tenant-test",
    request_id="request-test",
    execution_id=record["execution_id"],
    worker_job_id="worker-123",
    provider_key="openai",
    attempt_number=1,
    allowed_by_policy=False,
    result_status="blocked",
    reason="dispatch_disabled",
)
assert attempt_bridge["attempt"]["allowed_by_policy"] is False

retry_bridge = persist_retry_history_bridge(
    tenant_id="tenant-test",
    request_id="request-test",
    execution_id=record["execution_id"],
    worker_job_id="worker-123",
    provider_key="openai",
    attempt_number=1,
    failure_code="provider_timeout",
    retry_allowed=True,
    next_action="queue_retry",
)
assert retry_bridge["retry"]["retry_allowed"] is True

metric_bridge = persist_latency_metric_bridge(
    tenant_id="tenant-test",
    request_id="request-test",
    execution_id=record["execution_id"],
    provider_key="openai",
    latency_ms=1234,
    operation="dispatch_prepare",
)
assert metric_bridge["metric"]["latency_ms"] == 1234

summary = provider_postgres_bridge_summary()
assert summary["execution_records"]["count"] == 1
assert summary["worker_events"]["count"] == 1
assert summary["dispatch_attempts"]["count"] == 1
assert summary["retry_history"]["count"] == 1
assert summary["latency_metrics"]["count"] == 1
assert summary["credential_values_exposed"] is False

os.environ["DATABASE_URL"] = "postgresql://user:pass@example.com/db"
status_with_db = provider_postgres_ledger_bridge_status()
assert status_with_db["database_url_present"] is True

prepared = apply_provider_ledger_schema_if_possible()
assert prepared["status"] == "prepared"
assert prepared["reason"] == "DATABASE_URL_present_driver_application_pending"
assert prepared["applied"] is False

print("PROVIDER_EXECUTION_POSTGRES_LEDGER_BRIDGE_DIRECT_TESTS_PASSED")
print("database_url_present_initial", status["database_url_present"])
print("schema_available", schema["schema_sql_present"])
print("apply_without_db", applied["status"], applied["reason"])
print("record_mode", record_bridge["persistence_mode"])
print("summary_counts", summary["execution_records"]["count"], summary["worker_events"]["count"], summary["dispatch_attempts"]["count"], summary["retry_history"]["count"], summary["latency_metrics"]["count"])
print("database_url_present_after", status_with_db["database_url_present"])
print("apply_with_db", prepared["status"], prepared["reason"])
