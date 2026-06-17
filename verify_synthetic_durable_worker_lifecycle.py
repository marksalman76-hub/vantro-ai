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
    "worker_started",
    "worker_loop_started",
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
    "public_cutover_enabled",
    "public_production_cutover_enabled",
    "secret_fetch_attempted",
    "secrets_manager_value_retrieved",
]


REQUIRED_TRUE_FIELDS = [
    "synthetic_worker_lifecycle_attempted",
    "synthetic_worker_lifecycle_passed",
    "queued_status_represented",
    "claim_once_passed",
    "duplicate_claim_blocked",
    "processing_status_passed",
    "retry_state_represented",
    "failure_status_passed",
    "completed_status_represented",
    "terminal_status_readback_passed",
    "dlq_or_recovery_shape_present",
    "client_safe_status_redacted",
    "admin_diagnostics_redacted",
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
        "job_id": "synthetic_worker_lifecycle_non_customer_verifier",
        "customer_id": "synthetic_non_customer",
        "tenant_id": "synthetic_non_customer_tenant",
        "runway_api_key": "RUNWAY_SECRET_SHOULD_NOT_LEAK",
        "provider_credentials": {"elevenlabs_api_key": "ELEVEN_SECRET_SHOULD_NOT_LEAK"},
        "internal_config": {"stripe_secret_key": "STRIPE_SECRET_SHOULD_NOT_LEAK"},
        "database_url": "postgres://DATABASE_SECRET_SHOULD_NOT_LEAK",
        "queue_url": "https://sqs.example/QUEUE_SECRET_SHOULD_NOT_LEAK",
    }


def client_text_without_safe_boolean_keys(value: Any) -> str:
    safe_boolean_keys = {
        "provider_secret_values_visible",
        "credential_values_exposed",
        "internal_config_exposed",
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
    lifecycle = load_module(
        "backend/app/runtime/synthetic_durable_worker_lifecycle.py",
        "synthetic_durable_worker_lifecycle_under_test",
    )
    source = read("backend/app/runtime/synthetic_durable_worker_lifecycle.py")
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
        require(marker not in source, f"Synthetic worker lifecycle must not contain live side-effect marker: {marker}")

    for marker in [
        "synthetic_worker_lifecycle_attempted",
        "synthetic_worker_lifecycle_passed",
        "queued_status_represented",
        "claim_once_passed",
        "duplicate_claim_blocked",
        "processing_status_passed",
        "retry_state_represented",
        "failure_status_passed",
        "completed_status_represented",
        "terminal_status_readback_passed",
        "dlq_or_recovery_shape_present",
        "client_safe_status_redacted",
        "admin_diagnostics_redacted",
        "rollback_controls_blocked_when_enabled",
        "provider_call_attempted",
        "media_generation_attempted",
        "stripe_call_attempted",
        "billing_mutation_attempted",
        "credit_mutation_attempted",
        "public_cutover_enabled",
    ]:
        require(marker in source, f"Synthetic worker lifecycle source missing marker: {marker}")

    result = lifecycle.build_synthetic_durable_worker_lifecycle_proof(payload=synthetic_payload())
    require(result["status"] == "synthetic_durable_worker_lifecycle_passed", "Synthetic lifecycle proof must pass.")
    for key in REQUIRED_TRUE_FIELDS:
        require(result.get(key) is True, f"Proof field must be true: {key}")
        require((result.get("proof") or {}).get(key) is True, f"Nested proof field must be true: {key}")
    assert_no_forbidden_side_effects(result, "synthetic lifecycle proof")
    assert_no_forbidden_values(result, "synthetic lifecycle proof")

    lifecycle_trace = result.get("lifecycle_trace") or []
    statuses = [item.get("status") for item in lifecycle_trace]
    for status in ["queued", "claimed", "processing", "retry_scheduled", "failed_terminal", "completed"]:
        require(status in statuses, f"Lifecycle trace missing status: {status}")

    duplicate = result.get("duplicate_claim_result") or {}
    require(duplicate.get("status") == "already_claimed", "Duplicate claim must return already_claimed.")
    require(duplicate.get("duplicate_claim_blocked") is True, "Duplicate claim must be blocked.")
    require(duplicate.get("existing_claim_token_hash_present") is True, "Duplicate claim must expose only token presence.")

    dlq = result.get("dlq_or_recovery_shape") or {}
    require(dlq.get("dlq_or_recovery_shape_present") is True, "DLQ/recovery shape must exist.")
    require(dlq.get("customer_queue_consumed") is False, "DLQ proof must not consume a customer queue.")
    require(dlq.get("sqs_send_attempted") is False, "DLQ proof must not send SQS.")
    require(dlq.get("provider_call_attempted") is False, "DLQ proof must not call providers.")

    assert_client_safe(result.get("client_safe_failed_status") or {}, "failed client status")
    assert_client_safe(result.get("client_safe_completed_status") or {}, "completed client status")
    admin = result.get("admin_safe_diagnostics") or {}
    require(admin.get("admin_diagnostics_redacted") is True, "Admin diagnostics must be marked redacted.")
    require(admin.get("claim_token_hash_present") is True, "Admin diagnostics may show claim token presence only.")
    require("safe_error_summary" in admin, "Admin diagnostics must include safe error summary.")

    rollback_blocked = lifecycle.build_synthetic_durable_worker_lifecycle_proof(
        env={"AWS_OPTION_A_KILL_SWITCH_ENABLED": "true"},
        payload=synthetic_payload(),
    )
    require(rollback_blocked["status"] == "blocked_by_rollback_control", "Rollback kill switch must block lifecycle proof.")
    require(rollback_blocked["synthetic_worker_lifecycle_attempted"] is False, "Rollback block must not attempt lifecycle.")
    require(rollback_blocked["rollback_controls_blocked_when_enabled"] is True, "Rollback block marker must remain true.")
    assert_no_forbidden_side_effects(rollback_blocked, "rollback blocked lifecycle")
    assert_no_forbidden_values(rollback_blocked, "rollback blocked lifecycle")

    for marker in [
        "Synthetic durable worker lifecycle proof",
        "synthetic_worker_lifecycle_attempted=true",
        "claim_once_passed=true",
        "duplicate_claim_blocked=true",
        "retry_state_represented=true",
        "dlq_or_recovery_shape_present=true",
        "provider_call_attempted=false",
        "media_generation_attempted=false",
        "stripe_call_attempted=false",
        "billing_mutation_attempted=false",
        "credit_mutation_attempted=false",
        "public_cutover_enabled=false",
    ]:
        require(
            marker in master_plan or marker in matrix or marker in audit,
            f"Production docs missing synthetic worker proof marker: {marker}",
        )

    print("SYNTHETIC_DURABLE_WORKER_LIFECYCLE_VERIFICATION_PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
