import os

from backend.app.runtime import durable_manual_review_recovery_runtime as review_runtime
from backend.app.runtime import dead_letter_manual_review_runtime as legacy_review
from backend.app.runtime import durable_provider_execution_ledger as provider_ledger
from backend.app.runtime.provider_retry_timeout_orchestration import schedule_provider_job_retry


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
review_runtime.reset_dev_manual_review_recovery_for_tests()
provider_ledger.reset_dev_provider_ledger_for_tests()

ready = review_runtime.ensure_manual_review_recovery_tables()
assert_true(ready["success"], "dev manual review recovery store should be ready")
assert_true(ready["storage_mode"] == "dev_memory", "dev fallback should use memory")
assert_true(ready["dev_only"] is True, "dev fallback should be marked dev_only")
assert_true(ready["not_production_durable"] is True, "dev fallback should be marked not production durable")
assert_true(ready["credential_values_exposed"] is False, "readiness must not expose credentials")

created = review_runtime.create_manual_review_item(
    tenant_id="tenant_001",
    project_id="project_001",
    source_type="provider_job",
    source_id="provider_job_001",
    provider_job_id="provider_job_001",
    provider_execution_id="provider_exec_001",
    orchestration_id="orch_001",
    orchestration_step_id="step_001",
    queue_job_id="queue_001",
    packet_id="packet_001",
    routing_id="route_001",
    execution_id="exec_001",
    review_type="manual_review",
    status="manual_review_required",
    reason="test_review",
    payload={"safe": True, "api_key": "must_not_persist"},
)
assert_true(created["success"], "manual review item should create")
review_id = created["review_id"]
assert_true(created["item"]["credential_values_exposed"] is False, "review item must be credential-safe")
assert_true("api_key" not in created["item"]["payload"], "sensitive payload keys must be scrubbed")

duplicate = review_runtime.create_manual_review_item(
    tenant_id="tenant_001",
    project_id="project_001",
    source_type="provider_job",
    source_id="provider_job_001",
    review_type="manual_review",
    status="manual_review_required",
)
assert_true(duplicate["idempotent_replay"] is True, "same source review should be idempotent")
assert_true(duplicate["review_id"] == review_id, "idempotent review should reuse review id")

decision = review_runtime.record_manual_review_decision(
    review_id=review_id,
    decision="mark_resolved",
    actor_role="admin",
    reason="operator_checked",
)
assert_true(decision["success"], "manual review decision should persist")
assert_true(decision["item"]["status"] == "resolved", "decision should update review state")
assert_true(decision["item"]["resolved_at"], "resolved decision should set resolved_at")

decision_again = review_runtime.record_manual_review_decision(
    review_id=review_id,
    decision="mark_resolved",
    actor_role="admin",
    reason="operator_checked",
)
assert_true(decision_again["idempotent_replay"] is True, "same decision should be idempotent")

dead_letter = review_runtime.create_dead_letter_record(
    tenant_id="tenant_001",
    project_id="project_001",
    source_type="queue_job",
    source_id="queue_dead_001",
    queue_job_id="queue_dead_001",
    reason="retry_exhausted",
    error_summary="Queue retry exhausted.",
    payload={"secret_token": "must_not_persist", "safe": True},
)
assert_true(dead_letter["success"], "dead-letter record should create")
dead_letter_id = dead_letter["dead_letter_id"]
assert_true("secret_token" not in dead_letter["dead_letter"]["payload"], "dead-letter payload should be scrubbed")

dead_letters = review_runtime.list_dead_letter_records(tenant_id="tenant_001")
assert_true(dead_letters["count"] >= 1, "dead-letter list should include created record")

resolved_dead_letter = review_runtime.resolve_dead_letter_record(dead_letter_id, reason="reviewed")
assert_true(resolved_dead_letter["success"], "dead-letter should resolve")
assert_true(resolved_dead_letter["dead_letter"]["status"] == "resolved", "dead-letter status should be resolved")

recovery = review_runtime.create_recovery_action(
    tenant_id="tenant_001",
    project_id="project_001",
    review_id=review_id,
    dead_letter_id=dead_letter_id,
    orchestration_id="orch_001",
    provider_job_id="provider_job_001",
    queue_job_id="queue_001",
    action_type="execution_retry_prepared",
    status="prepared",
    payload={"retry": True},
)
assert_true(recovery["success"], "recovery action should create")

summary = review_runtime.get_review_recovery_summary(tenant_id="tenant_001")
assert_true(summary["success"], "summary should load")
assert_true(summary["review_count"] >= 1, "summary should include review count")
assert_true(summary["dead_letter_count"] >= 1, "summary should include dead-letter count")
assert_true(summary["recovery_action_count"] >= 1, "summary should include recovery action count")

legacy_dead_letter = legacy_review.create_dead_letter_record(
    tenant_id="tenant_legacy",
    agent_id="agent_001",
    action_type="legacy_action",
    failure_reason="legacy_failure",
    payload={"project_id": "project_legacy"},
)
assert_true(legacy_dead_letter["dead_letter_id"], "legacy wrapper should return dead-letter id")

legacy_queue = legacy_review.list_manual_review_queue(tenant_id="tenant_legacy")
assert_true(legacy_queue["count"] >= 1, "legacy wrapper should list durable manual review queue")

provider_job = provider_ledger.create_provider_job(
    payload={"attempt_count": 1},
    execution_id="provider_exec_retry_001",
    provider="openai",
    tenant_id="tenant_retry",
    project_id="project_retry",
    status="failed",
    max_attempts=1,
    provider_job_id="provider_job_retry_001",
)
assert_true(provider_job["success"], "provider job fixture should create")

retry_result = schedule_provider_job_retry("provider_job_retry_001", reason="test_exhausted", delay_seconds=0)
assert_true(retry_result["status"] == "manual_review_required", "exhausted provider retry should require review")
assert_true(retry_result.get("review_item"), "provider retry exhaustion should create review item")

provider_reviews = review_runtime.list_manual_review_items(tenant_id="tenant_retry")
assert_true(provider_reviews["count"] >= 1, "provider retry review should be listed")

review_runtime.reset_dev_manual_review_recovery_for_tests()
provider_ledger.reset_dev_provider_ledger_for_tests()
_clear_env()
os.environ["ENVIRONMENT"] = "production"
prod = review_runtime.ensure_manual_review_recovery_tables()
assert_true(prod["success"] is False, "production without DB should fail closed")
assert_true(prod["status"] == "manual_review_recovery_store_unavailable", "production status should be unavailable")
assert_true(prod["production_fail_closed"] is True, "production fail-closed flag should be true")
assert_true(prod["credential_values_exposed"] is False, "fail-closed response must not expose credentials")

_clear_env()
review_runtime.reset_dev_manual_review_recovery_for_tests()
provider_ledger.reset_dev_provider_ledger_for_tests()

print("DURABLE_MANUAL_REVIEW_RECOVERY_RUNTIME_PASSED")
