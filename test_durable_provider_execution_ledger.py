import os
from datetime import datetime, timedelta, timezone

from backend.app.runtime import durable_provider_execution_ledger as ledger


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
ledger.reset_dev_provider_ledger_for_tests()

ready = ledger.ensure_provider_ledger_tables()
assert_true(ready["success"], "dev provider ledger should be ready")
assert_true(ready["storage_mode"] == "dev_memory", "dev provider ledger should identify dev memory")
assert_true(ready["dev_only"] is True, "dev provider ledger should be marked dev_only")
assert_true(ready["not_production_durable"] is True, "dev provider ledger should be marked not durable")

execution = ledger.create_provider_execution_record(
    tenant_id="tenant_001",
    project_id="project_001",
    agent_id="agent_001",
    provider="openai",
    capability="text",
    action_type="generate_copy",
    status="created",
    request_payload={"prompt": "hello"},
    idempotency_key="idem_provider_001",
)
assert_true(execution["success"], "execution record should create")
execution_id = execution["execution_id"]

duplicate = ledger.create_provider_execution_record(
    tenant_id="tenant_001",
    project_id="project_001",
    agent_id="agent_001",
    provider="openai",
    capability="text",
    action_type="generate_copy",
    status="created",
    request_payload={"prompt": "hello duplicate"},
    idempotency_key="idem_provider_001",
)
assert_true(duplicate["idempotent_replay"] is True, "idempotent execution should replay")
assert_true(duplicate["execution_id"] == execution_id, "idempotent execution should not duplicate")

job_created = ledger.create_provider_job(
    execution_id=execution_id,
    provider="openai",
    tenant_id="tenant_001",
    project_id="project_001",
    status="queued",
    max_attempts=2,
)
assert_true(job_created["success"], "provider job should create")
job_id = job_created["provider_job_id"]

running = ledger.update_provider_job_status(job_id, "running")
assert_true(running["success"] and running["job"]["status"] == "running", "job should move to running")

polling = ledger.update_provider_job_status(
    job_id,
    "polling",
    polling_status="polling",
    next_poll_at=(datetime.now(timezone.utc) + timedelta(seconds=30)).isoformat(),
)
assert_true(polling["success"] and polling["job"]["status"] == "polling", "job should move to polling")

polling_state = ledger.record_provider_polling_state(
    provider_job_id=job_id,
    execution_id=execution_id,
    provider="openai",
    polling_status="polling",
    next_poll_at=datetime.now(timezone.utc) + timedelta(seconds=30),
    provider_status="in_progress",
)
assert_true(polling_state["success"], "polling state should persist")

dispatch = ledger.record_provider_dispatch_attempt(
    execution_id=execution_id,
    provider_job_id=job_id,
    provider="openai",
    status="ready",
    idempotency_key="dispatch_001",
    latency_ms=120,
)
assert_true(dispatch["success"], "dispatch should record")
dispatch_duplicate = ledger.record_provider_dispatch_attempt(
    execution_id=execution_id,
    provider_job_id=job_id,
    provider="openai",
    status="ready",
    idempotency_key="dispatch_001",
    latency_ms=200,
)
assert_true(dispatch_duplicate["idempotent_replay"] is True, "dispatch idempotency should replay")
assert_true(
    dispatch_duplicate["attempt"]["dispatch_attempt_id"] == dispatch["attempt"]["dispatch_attempt_id"],
    "dispatch idempotency should not duplicate",
)

retry = ledger.record_provider_retry(
    provider_job_id=job_id,
    execution_id=execution_id,
    retry_reason="temporary_failure",
    attempt_number=1,
    scheduled_for=datetime.now(timezone.utc),
)
assert_true(retry["success"], "retry should record")

failed = ledger.update_provider_job_status(job_id, "manual_review_required", error="retry_limit_reached")
assert_true(failed["success"], "max retry terminal equivalent should update")
assert_true(failed["job"]["status"] == "manual_review_required", "terminal state should be manual review")

completed_job = ledger.create_provider_job(
    execution_id=execution_id,
    provider="openai",
    tenant_id="tenant_001",
    project_id="project_001",
    status="queued",
)
completed_job_id = completed_job["provider_job_id"]
completed = ledger.update_provider_job_status(completed_job_id, "completed")
assert_true(completed["success"] and completed["job"]["status"] == "completed", "job should complete")

result = ledger.record_provider_result(
    provider_job_id=completed_job_id,
    execution_id=execution_id,
    provider="openai",
    result_status="completed",
    result_summary="Customer-safe provider output.",
    asset_id="asset_001",
    asset_url="https://example.test/asset.png",
    metadata={"safe": True},
)
assert_true(result["success"], "result record should persist")

delivery = ledger.record_provider_delivery_packet(
    provider_job_id=completed_job_id,
    execution_id=execution_id,
    asset_id="asset_001",
    delivery_status="ready",
)
assert_true(delivery["success"], "delivery packet should persist")

latency = ledger.record_provider_latency(
    provider="openai",
    capability="text",
    latency_ms=321,
    status="completed",
)
assert_true(latency["success"], "latency metric should persist")

summary = ledger.get_provider_admin_summary(tenant_id="tenant_001")
assert_true(summary["success"], "admin summary should read canonical state")
assert_true(len(summary["jobs"]) >= 2, "admin summary should include durable jobs")
assert_true(summary["credential_values_exposed"] is False, "admin summary must not expose credentials")

ledger.reset_dev_provider_ledger_for_tests()
_clear_env()
os.environ["ENVIRONMENT"] = "production"
prod = ledger.ensure_provider_ledger_tables()
assert_true(prod["success"] is False, "production without DB should fail closed")
assert_true(prod["status"] == "provider_ledger_unavailable", "production should report provider ledger unavailable")
assert_true(prod["production_fail_closed"] is True, "production fail closed flag should be true")
assert_true(prod["credential_values_exposed"] is False, "fail closed response must be credential-safe")

_clear_env()
ledger.reset_dev_provider_ledger_for_tests()

print("DURABLE_PROVIDER_EXECUTION_LEDGER_PASSED")
