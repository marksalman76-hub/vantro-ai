from backend.app.runtime.provider_execution_persistence_ledger import (
    append_worker_event_ledger_entry,
    create_provider_execution_record,
    get_provider_execution_record,
    list_dispatch_attempt_records,
    list_provider_execution_records,
    list_provider_latency_metrics,
    list_retry_history_records,
    list_worker_event_ledger,
    provider_execution_persistence_status,
    record_dispatch_attempt,
    record_provider_latency_metric,
    record_retry_history,
    reset_provider_execution_ledger_for_tests,
    update_provider_execution_record,
)

reset = reset_provider_execution_ledger_for_tests()
assert reset["reset"] is True
assert reset["credential_values_exposed"] is False

created = create_provider_execution_record(
    tenant_id="tenant-test",
    request_id="request-test",
    provider_key="openai",
    task_type="image_generation",
    execution_status="created",
    worker_job_id="worker-123",
)
assert created["execution_status"] == "created"
assert created["live_external_call_executed"] is False
assert created["credential_values_exposed"] is False

updated = update_provider_execution_record(
    execution_id=created["execution_id"],
    execution_status="dispatch_blocked",
    provider_job_id="provider-job-123",
    extra={
        "safe_note": "ok",
        "api_key": "must-not-store",
        "token": "must-not-store",
    },
)
assert updated["execution_status"] == "dispatch_blocked"
assert updated["provider_job_id"] == "provider-job-123"
assert "api_key" not in updated.get("extra", {})
assert "token" not in updated.get("extra", {})

fetched = get_provider_execution_record(created["execution_id"])
assert fetched["execution_id"] == created["execution_id"]

listed = list_provider_execution_records(tenant_id="tenant-test")
assert listed["count"] == 1
assert listed["records"][0]["provider_key"] == "openai"

ledger = append_worker_event_ledger_entry(
    tenant_id="tenant-test",
    request_id="request-test",
    execution_id=created["execution_id"],
    worker_job_id="worker-123",
    provider_key="openai",
    event_type="worker_prepared",
    status="dispatch_blocked",
    details={"safe": True, "secret": "must-not-store"},
)
assert ledger["event_type"] == "worker_prepared"
assert "secret" not in ledger["details"]
assert ledger["credential_values_exposed"] is False

ledger_list = list_worker_event_ledger(execution_id=created["execution_id"])
assert ledger_list["count"] == 1

attempt = record_dispatch_attempt(
    tenant_id="tenant-test",
    request_id="request-test",
    execution_id=created["execution_id"],
    worker_job_id="worker-123",
    provider_key="openai",
    attempt_number=1,
    allowed_by_policy=False,
    result_status="blocked",
    reason="real_provider_http_dispatch_globally_disabled",
)
assert attempt["allowed_by_policy"] is False
assert attempt["live_external_call_executed"] is False

attempts = list_dispatch_attempt_records(execution_id=created["execution_id"])
assert attempts["count"] == 1

retry = record_retry_history(
    tenant_id="tenant-test",
    request_id="request-test",
    execution_id=created["execution_id"],
    worker_job_id="worker-123",
    provider_key="openai",
    attempt_number=1,
    failure_code="provider_timeout",
    retry_allowed=True,
    next_action="queue_retry",
)
assert retry["retry_allowed"] is True
assert retry["next_action"] == "queue_retry"

retries = list_retry_history_records(execution_id=created["execution_id"])
assert retries["count"] == 1

latency1 = record_provider_latency_metric(
    tenant_id="tenant-test",
    request_id="request-test",
    execution_id=created["execution_id"],
    provider_key="openai",
    latency_ms=1000,
    operation="request_build",
)
latency2 = record_provider_latency_metric(
    tenant_id="tenant-test",
    request_id="request-test",
    execution_id=created["execution_id"],
    provider_key="openai",
    latency_ms=2000,
    operation="dispatch_prepare",
)
assert latency1["latency_ms"] == 1000
assert latency2["latency_ms"] == 2000

latencies = list_provider_latency_metrics(tenant_id="tenant-test", provider_key="openai")
assert latencies["count"] == 2
assert latencies["average_latency_ms"] == 1500
assert latencies["max_latency_ms"] == 2000
assert latencies["min_latency_ms"] == 1000

status = provider_execution_persistence_status()
assert status["persistence_runtime_ready"] is True
assert status["storage_mode"] == "in_memory_safe_fallback"
assert status["execution_record_count"] == 1
assert status["worker_event_count"] == 1
assert status["dispatch_attempt_count"] == 1
assert status["retry_history_count"] == 1
assert status["latency_metric_count"] == 2
assert status["credential_values_exposed"] is False

print("PROVIDER_EXECUTION_PERSISTENCE_LEDGER_DIRECT_TESTS_PASSED")
print("execution_id", created["execution_id"])
print("execution_status", updated["execution_status"])
print("ledger_count", ledger_list["count"])
print("attempt_count", attempts["count"])
print("retry_count", retries["count"])
print("latency_average", latencies["average_latency_ms"])
print("storage_mode", status["storage_mode"])
