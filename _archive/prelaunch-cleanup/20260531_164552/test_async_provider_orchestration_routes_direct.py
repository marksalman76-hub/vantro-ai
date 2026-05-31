import os
from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)

os.environ.pop("OPENAI_API_KEY", None)

blocked = client.post(
    "/async-provider-orchestration/packet",
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

assert blocked["orchestration_status"] == "blocked"
assert blocked["adapter_result"]["reason"] == "provider_credentials_missing"
assert blocked["live_external_call_executed"] is False
assert blocked["customer_safe"] is True
assert blocked["credential_values_exposed"] is False

os.environ["OPENAI_API_KEY"] = "test-secret-not-exposed"

ready = client.post(
    "/async-provider-orchestration/packet",
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

assert ready["orchestration_status"] == "ready_for_live_provider_call"
assert ready["adapter_result"]["adapter_name"] == "openai_live_execution_adapter_v1"
assert ready["live_external_call_executed"] is False
assert ready["audit_linkage"]["audit_event_type"] == "provider_execution_linkage"
assert ready["credential_values_exposed"] is False

polling = client.post(
    "/async-provider-orchestration/polling-state",
    json={
        "provider_key": "openai",
        "provider_job_id": "job-123",
        "current_state": "running",
        "provider_status": "succeeded",
        "attempt_count": 1,
    },
).json()

assert polling["mapped_state"] == "completed"
assert polling["next_action"] == "mark_completed"
assert polling["credential_values_exposed"] is False

retry = client.post(
    "/async-provider-orchestration/retry-escalation",
    json={
        "tenant_id": "tenant-test",
        "request_id": "request-test",
        "provider_key": "openai",
        "failure_code": "provider_timeout",
        "attempt_count": 1,
    },
).json()

assert retry["retry_allowed"] is True
assert retry["next_action"] == "queue_retry"
assert retry["credential_values_exposed"] is False

manual = client.post(
    "/async-provider-orchestration/retry-escalation",
    json={
        "tenant_id": "tenant-test",
        "request_id": "request-test",
        "provider_key": "openai",
        "failure_code": "provider_timeout",
        "attempt_count": 3,
    },
).json()

assert manual["retry_allowed"] is False
assert manual["next_action"] == "owner_review_required"
assert manual["owner_review_required"] is True
assert manual["credential_values_exposed"] is False

event = client.post(
    "/async-provider-orchestration/timeline-event",
    json={
        "tenant_id": "tenant-test",
        "request_id": "request-test",
        "execution_id": ready["execution_id"],
        "provider_key": "openai",
        "event_type": "provider_execution_started",
        "status": "running",
        "latency_ms": 1200,
    },
).json()

assert event["event_scope"] == "provider_orchestration"
assert event["customer_safe"] is True
assert event["credential_values_exposed"] is False

metrics = client.post(
    "/async-provider-orchestration/latency-metrics",
    json={
        "events": [
            {"latency_ms": 1200},
            {"latency_ms": 2400},
        ]
    },
).json()

assert metrics["event_count"] == 2
assert metrics["average_latency_ms"] == 1800
assert metrics["credential_values_exposed"] is False

selection = client.post(
    "/async-provider-orchestration/provider-selection",
    json={
        "requested_provider": "runway",
        "available_providers": ["openai", "runway"],
        "provider_health": {
            "openai": {
                "success_count": 10,
                "failure_count": 0,
                "timeout_count": 0,
                "average_latency_ms": 2000,
            },
            "runway": {
                "success_count": 1,
                "failure_count": 4,
                "timeout_count": 1,
                "average_latency_ms": 90000,
            },
        },
    },
).json()

assert selection["selected_provider"] == "openai"
assert selection["customer_safe"] is True
assert selection["credential_values_exposed"] is False

print("ASYNC_PROVIDER_ORCHESTRATION_ROUTES_DIRECT_TESTS_PASSED")
print("blocked_status", blocked["orchestration_status"], blocked["adapter_result"]["reason"])
print("ready_status", ready["orchestration_status"], ready["adapter_result"]["adapter_name"])
print("polling_next_action", polling["next_action"])
print("retry_next_action", retry["next_action"])
print("manual_next_action", manual["next_action"])
print("average_latency_ms", metrics["average_latency_ms"])
print("selected_provider", selection["selected_provider"])
