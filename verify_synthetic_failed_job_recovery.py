from __future__ import annotations

from pathlib import Path
import importlib.util
import sys
from typing import Any


ROOT = Path(__file__).resolve().parent


FORBIDDEN_VALUES = [
    "RUNWAY_SECRET_SHOULD_NOT_LEAK",
    "ELEVEN_SECRET_SHOULD_NOT_LEAK",
    "STRIPE_SECRET_SHOULD_NOT_LEAK",
    "DATABASE_SECRET_SHOULD_NOT_LEAK",
    "QUEUE_SECRET_SHOULD_NOT_LEAK",
    "DLQ_SECRET_SHOULD_NOT_LEAK",
    "MEDIA_BUCKET_SHOULD_NOT_LEAK",
    "UPLOAD_BUCKET_SHOULD_NOT_LEAK",
    "PROVIDER_SECRET_SHOULD_NOT_LEAK",
    "RDS_PASSWORD_SHOULD_NOT_LEAK",
    "123456789012",
    "arn:aws:secretsmanager",
    "postgres://",
    "postgresql://",
    "DATABASE_URL=postgres",
    "AWS_SECRET_ACCESS_KEY=",
    "AWS_SESSION_TOKEN=",
    "https://sqs.example",
    "stripe_secret_key=",
    "runway_api_key=",
]


FORBIDDEN_SIDE_EFFECT_TRUE_KEYS = [
    "live_worker_loop_started",
    "worker_started",
    "worker_loop_started",
    "customer_queue_message_consumed",
    "customer_queue_consumed",
    "aws_call_attempted",
    "rds_write_attempted",
    "sqs_send_attempted",
    "s3_upload_attempted",
    "provider_call_attempted",
    "paid_provider_calls_started",
    "media_generation_attempted",
    "ffmpeg_invoked",
    "stripe_call_attempted",
    "billing_mutation_attempted",
    "credit_mutation_attempted",
    "customer_traffic_started",
    "public_cutover_enabled",
    "public_production_cutover_enabled",
    "secret_fetch_attempted",
    "secrets_manager_value_retrieved",
    "live_recovery_execution_attempted",
]


REQUIRED_TRUE_FIELDS = [
    "synthetic_failed_job_recovery_attempted",
    "synthetic_failed_job_recovery_passed",
    "failure_classification_passed",
    "retry_exhaustion_represented",
    "dlq_shape_present",
    "dlq_reference_redacted",
    "admin_recovery_action_represented",
    "client_safe_failed_status_redacted",
    "admin_diagnostics_redacted",
    "recovered_or_requeued_state_represented",
    "terminal_failed_readback_passed",
    "terminal_recovered_or_completed_represented",
    "rollback_controls_blocked_when_enabled",
]


def read(relative: str) -> str:
    path = ROOT / relative
    if not path.exists():
        raise AssertionError(f"Missing required file: {relative}")
    return path.read_text(encoding="utf-8", errors="ignore")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load_module(relative: str, name: str):
    path = ROOT / relative
    spec = importlib.util.spec_from_file_location(name, path)
    if not spec or not spec.loader:
        raise AssertionError(f"Could not load module: {relative}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def assert_no_forbidden_values(value: object, label: str) -> None:
    text = str(value)
    for forbidden in FORBIDDEN_VALUES:
        require(forbidden not in text, f"{label} leaked forbidden value: {forbidden}")


def assert_no_forbidden_side_effects(result: dict, label: str) -> None:
    for key in FORBIDDEN_SIDE_EFFECT_TRUE_KEYS:
        require(result.get(key) is False, f"{label} attempted forbidden side effect: {key}")


def synthetic_payload() -> dict:
    return {
        "job_id": "synthetic_failed_recovery_non_customer_verifier",
        "customer_id": "synthetic_non_customer",
        "tenant_id": "synthetic_non_customer_tenant",
        "runway_api_key": "RUNWAY_SECRET_SHOULD_NOT_LEAK",
        "provider_credentials": {"elevenlabs_api_key": "ELEVEN_SECRET_SHOULD_NOT_LEAK"},
        "internal_config": {"stripe_secret_key": "STRIPE_SECRET_SHOULD_NOT_LEAK"},
        "database_url": "postgres://DATABASE_SECRET_SHOULD_NOT_LEAK",
        "queue_url": "https://sqs.example/QUEUE_SECRET_SHOULD_NOT_LEAK",
        "dlq_url": "https://sqs.example/DLQ_SECRET_SHOULD_NOT_LEAK",
        "media_bucket": "MEDIA_BUCKET_SHOULD_NOT_LEAK",
    }


def client_text_without_safe_boolean_keys(value: Any) -> str:
    safe_boolean_keys = {
        "provider_secret_values_visible",
        "credential_values_exposed",
        "internal_config_exposed",
        "admin_diagnostics_visible",
    }
    if isinstance(value, dict):
        return str({
            key: client_text_without_safe_boolean_keys(item)
            for key, item in value.items()
            if key not in safe_boolean_keys
        }).lower()
    if isinstance(value, list):
        return str([client_text_without_safe_boolean_keys(item) for item in value]).lower()
    return str(value).lower()


def assert_client_safe(value: dict, label: str) -> None:
    text = client_text_without_safe_boolean_keys(value)
    for forbidden in [
        "claim_token",
        "claimed_by",
        "internal_status",
        "provider_diagnostics",
        "database",
        "queue_url",
        "dlq_url",
        "secret",
        "credential",
        "stripe",
        "runway",
        "eleven",
        "arn:",
    ]:
        require(forbidden not in text, f"{label} exposed internal marker: {forbidden}")
    require(value.get("customer_safe") is True, f"{label} must be customer safe.")
    require(value.get("internal_config_exposed") is False, f"{label} must hide internal config.")


def main() -> int:
    recovery = load_module(
        "backend/app/runtime/synthetic_failed_job_recovery.py",
        "synthetic_failed_job_recovery_under_test",
    )
    source = read("backend/app/runtime/synthetic_failed_job_recovery.py")
    master_plan = read("PRODUCTION_COMPLETION_MASTER_PLAN.md")
    matrix = read("AWS_OPTION_A_MEDIA_MIGRATION_MATRIX.md")
    audit = read("PRODUCTION_FINISH_AUDIT_AND_GAP_PLAN.md")

    for marker in [
        "boto3",
        "psycopg",
        "requests.",
        "httpx.",
        "stripe.",
        "subprocess",
        "Popen",
        "start_worker",
        "run_worker",
        "send_message",
        "put_object",
        "get_secret_value",
        "provider_execution_started=True",
    ]:
        require(marker not in source, f"Synthetic failed-job recovery must not contain live side-effect marker: {marker}")

    for marker in [
        "synthetic_failed_job_recovery_attempted",
        "synthetic_failed_job_recovery_passed",
        "failure_classification_passed",
        "retry_exhaustion_represented",
        "dlq_shape_present",
        "dlq_reference_redacted",
        "admin_recovery_action_represented",
        "client_safe_failed_status_redacted",
        "admin_diagnostics_redacted",
        "recovered_or_requeued_state_represented",
        "terminal_failed_readback_passed",
        "terminal_recovered_or_completed_represented",
        "rollback_controls_blocked_when_enabled",
        "provider_call_attempted",
        "media_generation_attempted",
        "stripe_call_attempted",
        "billing_mutation_attempted",
        "credit_mutation_attempted",
        "public_cutover_enabled",
    ]:
        require(marker in source, f"Synthetic failed-job recovery source missing marker: {marker}")

    result = recovery.build_synthetic_failed_job_recovery_proof(payload=synthetic_payload())
    require(result["status"] == "synthetic_failed_job_recovery_passed", "Synthetic failed-job recovery proof must pass.")
    for key in REQUIRED_TRUE_FIELDS:
        require(result.get(key) is True, f"Proof field must be true: {key}")
        require((result.get("proof") or {}).get(key) is True, f"Nested proof field must be true: {key}")
    assert_no_forbidden_side_effects(result, "synthetic failed-job recovery proof")
    assert_no_forbidden_values(result, "synthetic failed-job recovery proof")

    failure = result.get("failure_classification") or {}
    require(failure.get("classification") == "synthetic_worker_execution_failure", "Failure must be classified safely.")
    require(failure.get("provider_execution_attempted") is False, "Failure classification must not imply provider execution.")

    retry = result.get("retry_exhaustion") or {}
    require(retry.get("retry_exhausted") is True, "Retry exhaustion must be represented.")
    require(retry.get("attempts_represented") == retry.get("max_attempts"), "Retry attempts must reach max attempts.")
    for attempt in retry.get("retry_history") or []:
        require(attempt.get("provider_call_attempted") is False, "Retry history must not call providers.")
        require(attempt.get("billing_mutation_attempted") is False, "Retry history must not mutate billing.")
        require(attempt.get("credit_mutation_attempted") is False, "Retry history must not mutate credits.")

    dlq = result.get("dlq_shape") or {}
    require(dlq.get("dlq_shape_present") is True, "DLQ shape must exist.")
    require(dlq.get("dlq_reference_redacted") is True, "DLQ reference must be redacted.")
    require(bool(dlq.get("dlq_reference_hash")), "DLQ reference hash must be present.")
    require(dlq.get("dlq_message_non_customer") is True, "DLQ message must be non-customer.")
    require(dlq.get("dlq_message_non_executable") is True, "DLQ message must be non-executable.")
    require(dlq.get("customer_queue_message_consumed") is False, "DLQ proof must not consume customer messages.")

    recovery_action = result.get("admin_recovery_action") or {}
    require(recovery_action.get("action_represented") is True, "Admin recovery action must be represented.")
    require(
        recovery_action.get("execution_mode") == "represented_only_no_live_requeue",
        "Admin recovery must not execute a live requeue.",
    )
    require(recovery_action.get("requires_owner_approval_for_live_execution") is True, "Live recovery must require approval.")

    assert_client_safe(result.get("client_safe_failed_status") or {}, "failed client status")
    admin = result.get("admin_safe_diagnostics") or {}
    require(admin.get("admin_diagnostics_redacted") is True, "Admin diagnostics must be marked redacted.")
    require(admin.get("dlq_reference_redacted") is True, "Admin diagnostics must use redacted DLQ references.")
    require(admin.get("retry_exhausted") is True, "Admin diagnostics must show retry exhaustion.")
    require("recommended_operator_next_step" in admin, "Admin diagnostics must include operator next step.")
    assert_no_forbidden_values(admin, "admin diagnostics")

    terminal_failed = result.get("terminal_failed_readback") or {}
    require(terminal_failed.get("status") == "failed_terminal", "Terminal failed readback must be represented.")
    require(terminal_failed.get("terminal_state_readback") is True, "Terminal failed readback marker must be true.")
    recovered = result.get("recovered_or_requeued_state") or {}
    require(recovered.get("status") == "requeued_synthetic", "Recovered/requeued state must be represented.")
    terminal_recovered = result.get("terminal_recovered_or_completed") or {}
    require(
        terminal_recovered.get("status") == "completed_synthetic_recovery",
        "Terminal recovered/completed status must be synthetic.",
    )
    require(terminal_recovered.get("synthetic_output_only") is True, "Terminal recovered output must be synthetic only.")

    rollback_blocked = recovery.build_synthetic_failed_job_recovery_proof(
        env={"AWS_OPTION_A_KILL_SWITCH_ENABLED": "true"},
        payload=synthetic_payload(),
    )
    require(rollback_blocked["status"] == "blocked_by_rollback_control", "Rollback kill switch must block recovery proof.")
    require(
        rollback_blocked["synthetic_failed_job_recovery_attempted"] is False,
        "Rollback block must not attempt recovery proof.",
    )
    require(
        rollback_blocked["rollback_controls_blocked_when_enabled"] is True,
        "Rollback block marker must remain true.",
    )
    assert_no_forbidden_side_effects(rollback_blocked, "rollback blocked recovery")
    assert_no_forbidden_values(rollback_blocked, "rollback blocked recovery")

    for marker in [
        "Synthetic failed-job and DLQ recovery proof",
        "synthetic_failed_job_recovery_attempted=true",
        "failure_classification_passed=true",
        "retry_exhaustion_represented=true",
        "dlq_shape_present=true",
        "dlq_reference_redacted=true",
        "admin_recovery_action_represented=true",
        "client_safe_failed_status_redacted=true",
        "admin_diagnostics_redacted=true",
        "recovered_or_requeued_state_represented=true",
        "terminal_failed_readback_passed=true",
        "terminal_recovered_or_completed_represented=true",
        "provider_call_attempted=false",
        "media_generation_attempted=false",
        "stripe_call_attempted=false",
        "billing_mutation_attempted=false",
        "credit_mutation_attempted=false",
        "public_cutover_enabled=false",
    ]:
        require(
            marker in master_plan or marker in matrix or marker in audit,
            f"Production docs missing synthetic failed-job recovery marker: {marker}",
        )

    print("SYNTHETIC_FAILED_JOB_RECOVERY_VERIFICATION_PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
