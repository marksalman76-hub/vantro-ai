import os

from backend.app.runtime.async_provider_orchestration_runtime import (
    advance_provider_polling_state,
    aggregate_provider_latency_metrics,
    build_provider_execution_timeline_event,
    create_provider_orchestration_packet,
    create_retry_escalation_packet,
    prepare_provider_selection_packet,
)


def assert_safe(packet):
    assert packet["credential_values_exposed"] is False


os.environ.pop("OPENAI_API_KEY", None)

blocked = create_provider_orchestration_packet(
    tenant_id="tenant-test",
    request_id="request-test",
    provider_key="openai",
    task_type="image_generation",
    payload={"prompt": "test"},
    live_execution_requested=True,
    owner_governed_execution_confirmed=True,
)

assert blocked["orchestration_status"] == "blocked"
assert blocked["adapter_result"]["reason"] == "provider_credentials_missing"
assert blocked["live_external_call_executed"] is False
assert blocked["customer_safe"] is True
assert_safe(blocked)

os.environ["OPENAI_API_KEY"] = "test-secret-not-exposed"

ready = create_provider_orchestration_packet(
    tenant_id="tenant-test",
    request_id="request-test",
    provider_key="openai",
    task_type="image_generation",
    payload={"prompt": "test"},
    live_execution_requested=True,
    owner_governed_execution_confirmed=True,
)

assert ready["orchestration_status"] == "ready_for_live_provider_call"
assert ready["adapter_result"]["adapter_name"] == "openai_live_execution_adapter_v1"
assert ready["live_external_call_executed"] is False
assert ready["audit_linkage"]["audit_event_type"] == "provider_execution_linkage"
assert_safe(ready)

polling = advance_provider_polling_state(
    provider_key="openai",
    provider_job_id="job-123",
    current_state="running",
    provider_status="succeeded",
    attempt_count=1,
)
assert polling["mapped_state"] == "completed"
assert polling["next_action"] == "mark_completed"
assert_safe(polling)

retry = create_retry_escalation_packet(
    tenant_id="tenant-test",
    request_id="request-test",
    provider_key="openai",
    failure_code="provider_timeout",
    attempt_count=1,
)
assert retry["retry_allowed"] is True
assert retry["next_action"] == "queue_retry"
assert_safe(retry)

manual = create_retry_escalation_packet(
    tenant_id="tenant-test",
    request_id="request-test",
    provider_key="openai",
    failure_code="provider_timeout",
    attempt_count=3,
)
assert manual["retry_allowed"] is False
assert manual["next_action"] == "owner_review_required"
assert manual["owner_review_required"] is True
assert_safe(manual)

event1 = build_provider_execution_timeline_event(
    tenant_id="tenant-test",
    request_id="request-test",
    execution_id=ready["execution_id"],
    provider_key="openai",
    event_type="provider_execution_started",
    status="running",
    latency_ms=1200,
)
event2 = build_provider_execution_timeline_event(
    tenant_id="tenant-test",
    request_id="request-test",
    execution_id=ready["execution_id"],
    provider_key="openai",
    event_type="provider_execution_completed",
    status="completed",
    latency_ms=2400,
)

metrics = aggregate_provider_latency_metrics([event1, event2])
assert metrics["event_count"] == 2
assert metrics["average_latency_ms"] == 1800
assert metrics["max_latency_ms"] == 2400

selection = prepare_provider_selection_packet(
    requested_provider="runway",
    available_providers=["openai", "runway"],
    provider_health={
        "openai": {"success_count": 10, "failure_count": 0, "timeout_count": 0, "average_latency_ms": 2000},
        "runway": {"success_count": 1, "failure_count": 4, "timeout_count": 1, "average_latency_ms": 90000},
    },
)
assert selection["selected_provider"] == "openai"
assert selection["customer_safe"] is True
assert_safe(selection)

print("ASYNC_PROVIDER_ORCHESTRATION_RUNTIME_DIRECT_TESTS_PASSED")
print("blocked_status", blocked["orchestration_status"], blocked["adapter_result"]["reason"])
print("ready_status", ready["orchestration_status"], ready["adapter_result"]["adapter_name"])
print("polling_next_action", polling["next_action"])
print("retry_next_action", retry["next_action"])
print("manual_next_action", manual["next_action"])
print("average_latency_ms", metrics["average_latency_ms"])
print("selected_provider", selection["selected_provider"])
