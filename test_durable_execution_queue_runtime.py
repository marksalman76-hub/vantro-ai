import os
from datetime import datetime, timedelta, timezone

from backend.app.runtime import durable_execution_queue_runtime as queue


def _clear_env():
    for key in (
        "DATABASE_URL",
        "POSTGRES_URL",
        "ENVIRONMENT",
        "APP_ENV",
        "FASTAPI_ENV",
        "NODE_ENV",
        "RENDER",
        "VERCEL_ENV",
        "PRODUCTION",
    ):
        os.environ.pop(key, None)


def assert_true(value, message):
    if not value:
        raise AssertionError(message)


_clear_env()
queue.reset_dev_execution_queue_for_tests()

ready = queue.ensure_execution_queue_tables()
assert_true(ready["success"], "dev fallback should be available")
assert_true(ready["storage_mode"] == "dev_memory", "dev fallback should identify dev_memory")
assert_true(ready["dev_only"] is True, "dev fallback should be marked dev_only")

first = queue.enqueue_execution_job(
    queue_name="execution_queue",
    tenant_id="tenant_001",
    project_id="project_001",
    agent_id="copy_agent",
    action_type="generate_copy",
    payload={"task": "write product copy"},
    idempotency_key="idem_001",
)
assert_true(first["success"], "enqueue should succeed")
assert_true(first["status"] == "queued", "new job should be queued")

second = queue.enqueue_execution_job(
    queue_name="execution_queue",
    tenant_id="tenant_001",
    project_id="project_001",
    agent_id="copy_agent",
    action_type="generate_copy",
    payload={"task": "write product copy duplicate"},
    idempotency_key="idem_001",
)
assert_true(second["success"], "idempotent enqueue should succeed")
assert_true(second["idempotent_replay"] is True, "idempotent enqueue should replay existing job")
assert_true(second["job_id"] == first["job_id"], "idempotent enqueue must not duplicate")
assert_true(queue.list_execution_jobs(status="queued")["count"] == 1, "only one queued job should exist")

claimed = queue.claim_next_execution_job(queue_name="execution_queue", worker_id="worker_a")
assert_true(claimed["success"], "claim should succeed")
assert_true(claimed["status"] == "leased", "claimed job should be leased")
assert_true(claimed["job"]["leased_by"] == "worker_a", "leased_by should be worker id")

heartbeat = queue.heartbeat_execution_job(claimed["job_id"], worker_id="worker_a")
assert_true(heartbeat["success"], "heartbeat should succeed")
assert_true(heartbeat["status"] == "heartbeat_recorded", "heartbeat should be recorded")

completed = queue.complete_execution_job(claimed["job_id"], worker_id="worker_a", result={"ok": True})
assert_true(completed["success"], "complete should succeed")
assert_true(completed["status"] == "completed", "job should be completed")

retry_job = queue.enqueue_execution_job(
    queue_name="execution_queue",
    tenant_id="tenant_001",
    project_id="project_001",
    agent_id="ops_agent",
    action_type="retry_test",
    payload={"task": "retry"},
    idempotency_key="idem_retry",
    max_attempts=2,
)
retry_claim = queue.claim_next_execution_job(queue_name="execution_queue", worker_id="worker_retry")
retry_one = queue.fail_execution_job(
    retry_claim["job_id"],
    error="temporary_failure",
    worker_id="worker_retry",
    retry_delay_seconds=0,
)
assert_true(retry_one["success"], "first failure should schedule retry")
assert_true(retry_one["status"] == "retry_scheduled", "first failure should retry")
assert_true(retry_one["job"]["attempt_count"] == 1, "attempt_count should increment")

retry_claim_two = queue.claim_next_execution_job(queue_name="execution_queue", worker_id="worker_retry")
dead = queue.fail_execution_job(
    retry_claim_two["job_id"],
    error="permanent_failure",
    worker_id="worker_retry",
    retry_delay_seconds=0,
)
assert_true(dead["success"], "max retry failure should succeed as a transition")
assert_true(dead["status"] == "dead_letter", "max attempts should move to dead_letter")
assert_true(dead["job"]["credential_values_exposed"] is False, "dead-letter response must not expose credentials")

lease_job = queue.enqueue_execution_job(
    queue_name="execution_queue",
    tenant_id="tenant_001",
    project_id="project_001",
    agent_id="lease_agent",
    action_type="lease_test",
    payload={"task": "lease"},
    idempotency_key="idem_lease",
)
lease_claim = queue.claim_next_execution_job(queue_name="execution_queue", worker_id="worker_old")
queue._DEV_JOBS[lease_claim["job_id"]]["lease_expires_at"] = (
    datetime.now(timezone.utc) - timedelta(seconds=1)
).isoformat()
released = queue.release_expired_execution_leases(queue_name="execution_queue")
assert_true(released["success"], "expired lease release should succeed")
assert_true(released["released_count"] == 1, "one expired lease should be released")
reclaimed = queue.claim_next_execution_job(queue_name="execution_queue", worker_id="worker_new")
assert_true(reclaimed["success"], "reclaim should succeed")
assert_true(reclaimed["job_id"] == lease_job["job_id"], "expired lease should be reclaimable")
assert_true(reclaimed["job"]["leased_by"] == "worker_new", "new worker should own lease")

status = queue.get_execution_queue_status(queue_name="execution_queue")
assert_true(status["success"], "queue status should succeed")
assert_true(status["retry_scheduling_enabled"] is True, "status should expose retry support")
assert_true(status["dead_letter_enabled"] is True, "status should expose dead-letter support")
assert_true(status["idempotency_keys_enabled"] is True, "status should expose idempotency support")

queue.reset_dev_execution_queue_for_tests()
_clear_env()
os.environ["ENVIRONMENT"] = "production"
prod_status = queue.ensure_execution_queue_tables()
assert_true(prod_status["success"] is False, "production without DB should fail closed")
assert_true(prod_status["status"] == "durable_queue_unavailable", "production should report durable_queue_unavailable")
assert_true(prod_status["production_fail_closed"] is True, "production fail-closed flag should be true")
assert_true(prod_status["credential_values_exposed"] is False, "fail-closed response must not expose credentials")

_clear_env()
queue.reset_dev_execution_queue_for_tests()

print("DURABLE_EXECUTION_QUEUE_RUNTIME_PASSED")
