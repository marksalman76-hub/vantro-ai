import os

from backend.app.runtime.background_worker_loop_foundation import (
    background_worker_loop_foundation_status,
    enqueue_background_provider_job,
    list_background_worker_queue,
    reconcile_background_worker_completion,
    reset_background_worker_loop_for_tests,
    run_background_worker_cycle_once,
    run_background_worker_dispatch_check,
    run_background_worker_polling_cycle,
    run_background_worker_retry_scheduler,
)

reset = reset_background_worker_loop_for_tests()
assert reset["reset"] is True

os.environ.pop("OPENAI_API_KEY", None)
os.environ.pop("REAL_PROVIDER_HTTP_DISPATCH_ENABLED", None)

status = background_worker_loop_foundation_status()
assert status["background_worker_loop_ready"] is True
assert status["real_external_dispatch_enabled"] is False
assert status["credential_values_exposed"] is False

enqueued = enqueue_background_provider_job(
    tenant_id="tenant-test",
    request_id="request-test",
    provider_key="openai",
    task_type="image_generation",
    payload={"prompt": "test"},
    live_execution_requested=True,
    owner_governed_execution_confirmed=True,
)
assert enqueued["enqueued"] is True
assert enqueued["queue_size"] == 1
assert enqueued["live_external_call_executed"] is False

queue_item = enqueued["queue_item"]

dispatch = run_background_worker_dispatch_check(queue_item)
assert dispatch["next_state"] == "dispatch_blocked"
assert dispatch["dispatch_allowed"] is False
assert dispatch["live_external_call_executed"] is False

polling = run_background_worker_polling_cycle(
    queue_item=queue_item,
    provider_job_id="provider-job-123",
    provider_status="succeeded",
)
assert polling["mapped_state"] == "completed"
assert polling["terminal"] is True

retry = run_background_worker_retry_scheduler(queue_item, failure_code="provider_timeout")
assert retry["attempt_count"] == 1
assert retry["retry_allowed"] is True
assert retry["next_state"] == "retry_queued"

complete = reconcile_background_worker_completion(
    queue_item=queue_item,
    final_status="completed",
    latency_ms=2500,
)
assert complete["reconciled_status"] == "completed"
assert complete["terminal"] is True

listed = list_background_worker_queue(tenant_id="tenant-test")
assert listed["count"] == 1

cycle = run_background_worker_cycle_once()
assert cycle["queue_size"] == 1
assert cycle["live_external_call_executed"] is False
assert cycle["credential_values_exposed"] is False

final_status = background_worker_loop_foundation_status()
assert final_status["queue_size"] == 1

print("BACKGROUND_WORKER_LOOP_FOUNDATION_DIRECT_TESTS_PASSED")
print("queue_size", listed["count"])
print("dispatch", dispatch["next_state"], dispatch["dispatch_allowed"])
print("polling", polling["mapped_state"], polling["terminal"])
print("retry", retry["next_state"], retry["next_action"])
print("complete", complete["reconciled_status"])
print("cycle_processed", cycle["processed_count"])
