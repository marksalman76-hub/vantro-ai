import os

from backend.app.runtime.provider_execution_postgres_ledger_bridge import (
    persist_dispatch_attempt_bridge,
    persist_latency_metric_bridge,
    persist_provider_execution_record_bridge,
    persist_retry_history_bridge,
    persist_worker_event_bridge,
    provider_postgres_extended_ledger_read_status,
    postgres_read_dispatch_attempts,
    postgres_read_latency_metrics,
    postgres_read_retry_history,
    postgres_read_worker_events,
    reset_provider_postgres_bridge_fallback_for_tests,
)

reset_provider_postgres_bridge_fallback_for_tests()
os.environ.pop("DATABASE_URL", None)

status = provider_postgres_extended_ledger_read_status()
assert status["extended_ledger_read_ready"] is True
assert status["fallback_storage_active"] is True
assert status["credential_values_exposed"] is False

record = persist_provider_execution_record_bridge(
    tenant_id="tenant-test",
    request_id="request-test",
    provider_key="openai",
    task_type="image_generation",
    execution_status="created",
    worker_job_id="worker-123",
)
execution_id = record["record"]["execution_id"]

persist_worker_event_bridge(
    tenant_id="tenant-test",
    request_id="request-test",
    execution_id=execution_id,
    worker_job_id="worker-123",
    provider_key="openai",
    event_type="worker_prepared",
    status="dispatch_blocked",
    details={"safe": True},
)

persist_dispatch_attempt_bridge(
    tenant_id="tenant-test",
    request_id="request-test",
    execution_id=execution_id,
    worker_job_id="worker-123",
    provider_key="openai",
    attempt_number=1,
    allowed_by_policy=False,
    result_status="blocked",
    reason="dispatch_disabled",
)

persist_retry_history_bridge(
    tenant_id="tenant-test",
    request_id="request-test",
    execution_id=execution_id,
    worker_job_id="worker-123",
    provider_key="openai",
    attempt_number=1,
    failure_code="provider_timeout",
    retry_allowed=True,
    next_action="queue_retry",
)

persist_latency_metric_bridge(
    tenant_id="tenant-test",
    request_id="request-test",
    execution_id=execution_id,
    provider_key="openai",
    latency_ms=1500,
    operation="dispatch_prepare",
)

events = postgres_read_worker_events(tenant_id="tenant-test")
assert events["count"] == 1
assert events["postgres_read_attempted"] is False

attempts = postgres_read_dispatch_attempts(tenant_id="tenant-test")
assert attempts["count"] == 1

retries = postgres_read_retry_history(tenant_id="tenant-test")
assert retries["count"] == 1

latencies = postgres_read_latency_metrics(tenant_id="tenant-test", provider_key="openai")
assert latencies["count"] == 1
assert latencies["average_latency_ms"] == 1500

os.environ["DATABASE_URL"] = "postgresql://user:pass@example.com/db"

events_db = postgres_read_worker_events(tenant_id="tenant-test")
assert events_db["postgres_read_attempted"] is True
assert events_db["credential_values_exposed"] is False

print("PROVIDER_EXECUTION_POSTGRES_EXTENDED_LEDGER_READS_DIRECT_TESTS_PASSED")
print("events", events["count"])
print("attempts", attempts["count"])
print("retries", retries["count"])
print("latencies", latencies["count"], latencies["average_latency_ms"])
print("events_db_attempted", events_db["postgres_read_attempted"])
