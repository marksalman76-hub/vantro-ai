import os

from backend.app.runtime.provider_dispatch_policy_worker_foundation import (
    advance_provider_worker_job,
    create_provider_worker_job_packet,
    evaluate_provider_dispatch_policy,
    provider_dispatch_policy_status,
    provider_worker_foundation_status,
)

os.environ.pop("OPENAI_API_KEY", None)
os.environ.pop("REAL_PROVIDER_HTTP_DISPATCH_ENABLED", None)

policy_status = provider_dispatch_policy_status()
assert policy_status["real_dispatch_globally_enabled"] is False
assert policy_status["requires_owner_governed_execution_confirmed"] is True
assert policy_status["credential_values_exposed"] is False

blocked_policy = evaluate_provider_dispatch_policy(
    provider_key="openai",
    payload={
        "tenant_id": "tenant-test",
        "request_id": "request-test",
        "prompt": "test",
        "live_execution_requested": True,
        "owner_governed_execution_confirmed": True,
    },
)
assert blocked_policy["dispatch_allowed"] is False
assert blocked_policy["reason"] == "real_provider_http_dispatch_globally_disabled"
assert blocked_policy["live_external_call_executed"] is False
assert blocked_policy["credential_values_exposed"] is False

worker_blocked = create_provider_worker_job_packet(
    tenant_id="tenant-test",
    request_id="request-test",
    provider_key="openai",
    task_type="image_generation",
    payload={"prompt": "test"},
    live_execution_requested=True,
    owner_governed_execution_confirmed=True,
)
assert worker_blocked["worker_state"] == "dispatch_blocked"
assert worker_blocked["next_action"] == "hold_for_policy_or_credentials"
assert worker_blocked["live_external_call_executed"] is False
assert worker_blocked["credential_values_exposed"] is False

os.environ["OPENAI_API_KEY"] = "test-secret-not-exposed"

still_blocked = create_provider_worker_job_packet(
    tenant_id="tenant-test",
    request_id="request-test",
    provider_key="openai",
    task_type="image_generation",
    payload={"prompt": "test"},
    live_execution_requested=True,
    owner_governed_execution_confirmed=True,
)
assert still_blocked["worker_state"] == "dispatch_blocked"
assert still_blocked["dispatch_policy"]["http_packet_status"] == "ready_for_real_http_dispatch"
assert still_blocked["dispatch_policy"]["dispatch_allowed"] is False
assert still_blocked["dispatch_policy"]["reason"] == "real_provider_http_dispatch_globally_disabled"

os.environ["REAL_PROVIDER_HTTP_DISPATCH_ENABLED"] = "true"

ready_worker = create_provider_worker_job_packet(
    tenant_id="tenant-test",
    request_id="request-test",
    provider_key="openai",
    task_type="image_generation",
    payload={"prompt": "test"},
    live_execution_requested=True,
    owner_governed_execution_confirmed=True,
)
assert ready_worker["worker_state"] == "ready_for_worker_dispatch"
assert ready_worker["next_action"] == "queue_real_provider_dispatch"
assert ready_worker["live_external_call_executed"] is False

advanced = advance_provider_worker_job(
    worker_job_id=ready_worker["worker_job_id"],
    tenant_id="tenant-test",
    request_id="request-test",
    provider_key="openai",
    current_state=ready_worker["worker_state"],
)
assert advanced["next_state"] == "dispatch_waiting_final_enablement"
assert advanced["next_action"] == "wait_for_final_policy_enablement"
assert advanced["credential_values_exposed"] is False

retry = advance_provider_worker_job(
    worker_job_id=ready_worker["worker_job_id"],
    tenant_id="tenant-test",
    request_id="request-test",
    provider_key="openai",
    current_state="dispatch_blocked",
    attempt_count=1,
    failure_code="provider_timeout",
)
assert retry["next_state"] == "retry_queued"
assert retry["next_action"] == "queue_retry"

foundation = provider_worker_foundation_status()
assert foundation["worker_foundation_ready"] is True
assert foundation["real_background_dispatch_enabled"] is False
assert foundation["dispatch_policy_layer_enabled"] is True
assert foundation["credential_values_exposed"] is False

print("PROVIDER_DISPATCH_POLICY_WORKER_FOUNDATION_DIRECT_TESTS_PASSED")
print("policy_enabled", policy_status["real_dispatch_globally_enabled"])
print("blocked_policy", blocked_policy["dispatch_allowed"], blocked_policy["reason"])
print("worker_blocked", worker_blocked["worker_state"], worker_blocked["next_action"])
print("still_blocked", still_blocked["dispatch_policy"]["http_packet_status"], still_blocked["dispatch_policy"]["reason"])
print("ready_worker", ready_worker["worker_state"], ready_worker["next_action"])
print("advanced_worker", advanced["next_state"], advanced["next_action"])
print("retry_worker", retry["next_state"], retry["next_action"])
print("foundation_ready", foundation["worker_foundation_ready"])
