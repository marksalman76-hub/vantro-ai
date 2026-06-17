from __future__ import annotations

from pathlib import Path
import importlib.util
import json
import os
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
    "RAW_RECEIPT_HANDLE_SHOULD_NOT_LEAK",
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


FORBIDDEN_SIDE_EFFECT_KEYS = [
    "live_worker_loop_started",
    "worker_loop_started",
    "customer_queue_message_consumed",
    "customer_queue_consumed",
    "provider_call_attempted",
    "paid_provider_calls_started",
    "media_generation_attempted",
    "ffmpeg_invoked",
    "stripe_call_attempted",
    "billing_mutation_attempted",
    "credit_mutation_attempted",
    "customer_traffic_attempted",
    "customer_traffic_started",
    "public_cutover_enabled",
    "public_production_cutover_enabled",
    "secret_fetch_attempted",
    "secrets_manager_value_retrieved",
]


SAFE_DEFAULT_LIVE_SIDE_EFFECT_KEYS = [
    "aws_backed_dlq_recovery_attempted",
    "live_durable_status_attempted",
    "db_connection_attempted",
    "rds_write_attempted",
    "recovery_or_requeue_attempted",
]


REQUIRED_TRUE_FIELDS = [
    "aws_backed_dlq_recovery_attempted",
    "aws_backed_dlq_recovery_passed",
    "owner_flags_required",
    "synthetic_dlq_message_present",
    "dlq_message_non_customer",
    "dlq_message_non_executable",
    "dlq_reference_redacted",
    "failure_classification_passed",
    "retry_exhaustion_or_failed_terminal_represented",
    "admin_recovery_action_represented",
    "recovery_or_requeue_attempted",
    "recovery_or_requeue_passed",
    "client_safe_failed_or_recovered_status_redacted",
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
    for forbidden_fragment in [
        "ReceiptHandle",
        "receipt_handle': '",
        '"receipt_handle": "',
        "QueueUrl",
        "DATABASE_URL",
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY",
        "AWS_SESSION_TOKEN",
    ]:
        require(forbidden_fragment not in text, f"{label} leaked raw internal marker: {forbidden_fragment}")


def assert_no_forbidden_values_allowing_env_names(value: object, label: str) -> None:
    text = str(value)
    for forbidden in FORBIDDEN_VALUES:
        require(forbidden not in text, f"{label} leaked forbidden value: {forbidden}")
    for forbidden_fragment in [
        "ReceiptHandle",
        "receipt_handle': '",
        '"receipt_handle": "',
        "QueueUrl",
        "AWS_ACCESS_KEY_ID=",
        "AWS_SECRET_ACCESS_KEY=",
        "AWS_SESSION_TOKEN=",
    ]:
        require(forbidden_fragment not in text, f"{label} leaked raw internal marker: {forbidden_fragment}")


def assert_forbidden_side_effects_disabled(result: dict, label: str) -> None:
    for key in FORBIDDEN_SIDE_EFFECT_KEYS:
        require(result.get(key) is False, f"{label} attempted forbidden side effect: {key}")


def assert_no_safe_default_live_side_effects(value: Any, label: str) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if key in SAFE_DEFAULT_LIVE_SIDE_EFFECT_KEYS:
                require(item is False, f"{label} attempted live side effect before gates: {key}")
            assert_no_safe_default_live_side_effects(item, label)
    elif isinstance(value, list):
        for item in value:
            assert_no_safe_default_live_side_effects(item, label)


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
        "receipt",
        "claim_token",
        "claimed_by",
        "internal_status",
        "provider_diagnostics",
        "database",
        "queue",
        "dlq",
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


def dangerous_env(helper) -> dict:
    return {
        "AWS_REGION": "ap-southeast-2",
        "DATABASE_URL": "postgres://DATABASE_SECRET_SHOULD_NOT_LEAK",
        "AWS_MEDIA_QUEUE_URL": "https://sqs.example/QUEUE_SECRET_SHOULD_NOT_LEAK",
        "AWS_MEDIA_DLQ_URL": "https://sqs.example/DLQ_SECRET_SHOULD_NOT_LEAK",
        "AWS_MEDIA_S3_BUCKET": "MEDIA_BUCKET_SHOULD_NOT_LEAK",
        "AWS_PROVIDER_SECRETS_PREFIX": "/provider/PROVIDER_SECRET_SHOULD_NOT_LEAK",
        helper.AWS_BACKED_DLQ_RECOVERY_ENABLED_FLAG: "true",
        helper.AWS_BACKED_DLQ_RECOVERY_OWNER_APPROVED_FLAG: "true",
        helper.AWS_BACKED_DLQ_RECOVERY_VALIDATION_CONFIRMED_FLAG: "true",
        helper.AWS_BACKED_DLQ_RECOVERY_STATUS_READBACK_ENABLED_FLAG: "true",
        helper.AWS_BACKED_DLQ_RECOVERY_ACTION_ENABLED_FLAG: "true",
        helper.AWS_BACKED_DLQ_RECOVERY_CLEANUP_ENABLED_FLAG: "true",
    }


def run_safe_default_tests(helper) -> None:
    base = helper.build_aws_backed_synthetic_dlq_recovery_proof(env={}, actor_role="admin")
    require(base["status"] == "safe_default_no_aws_backed_dlq_recovery", "Default mode must not run live DLQ proof.")
    require(base["blocked_reason"] == "blocked_dlq_recovery_not_enabled", "Default must be blocked by recovery flag.")
    require(base["owner_flags_required"] is True, "Owner flags must be required.")
    require(base["rollback_controls_blocked_when_enabled"] is True, "Rollback proof marker must be true.")
    assert_no_safe_default_live_side_effects(base, "default DLQ recovery proof")
    assert_forbidden_side_effects_disabled(base, "default DLQ recovery proof")
    assert_no_forbidden_values(base, "default DLQ recovery proof")

    missing_owner = dangerous_env(helper)
    missing_owner[helper.AWS_BACKED_DLQ_RECOVERY_OWNER_APPROVED_FLAG] = "false"
    owner_blocked = helper.build_aws_backed_synthetic_dlq_recovery_proof(env=missing_owner, actor_role="admin")
    require(owner_blocked["blocked_reason"] == "blocked_owner_approval_required", "Owner approval must be required.")
    assert_no_safe_default_live_side_effects(owner_blocked, "owner-blocked DLQ recovery proof")
    assert_no_forbidden_values(owner_blocked, "owner-blocked DLQ recovery proof")

    client_blocked = dangerous_env(helper)
    client_result = helper.build_aws_backed_synthetic_dlq_recovery_proof(env=client_blocked, actor_role="client")
    require(client_result["blocked_reason"] == "blocked_client_not_authorized", "Client must not trigger live DLQ proof.")
    assert_no_safe_default_live_side_effects(client_result, "client-blocked DLQ recovery proof")

    validation_blocked = dangerous_env(helper)
    validation_blocked[helper.AWS_BACKED_DLQ_RECOVERY_VALIDATION_CONFIRMED_FLAG] = "false"
    validation_result = helper.build_aws_backed_synthetic_dlq_recovery_proof(env=validation_blocked, actor_role="admin")
    require(
        validation_result["blocked_reason"] == "blocked_validation_confirmation_required",
        "Validation confirmation must be required.",
    )
    assert_no_safe_default_live_side_effects(validation_result, "validation-blocked DLQ recovery proof")

    status_blocked = dangerous_env(helper)
    status_blocked[helper.AWS_BACKED_DLQ_RECOVERY_STATUS_READBACK_ENABLED_FLAG] = "false"
    status_result = helper.build_aws_backed_synthetic_dlq_recovery_proof(env=status_blocked, actor_role="admin")
    require(status_result["blocked_reason"] == "blocked_status_readback_flag_required", "Status flag required.")
    assert_no_safe_default_live_side_effects(status_result, "status-blocked DLQ recovery proof")

    action_blocked = dangerous_env(helper)
    action_blocked[helper.AWS_BACKED_DLQ_RECOVERY_ACTION_ENABLED_FLAG] = "false"
    action_result = helper.build_aws_backed_synthetic_dlq_recovery_proof(env=action_blocked, actor_role="admin")
    require(action_result["blocked_reason"] == "blocked_recovery_action_flag_required", "Action flag required.")
    assert_no_safe_default_live_side_effects(action_result, "action-blocked DLQ recovery proof")

    cleanup_blocked = dangerous_env(helper)
    cleanup_blocked[helper.AWS_BACKED_DLQ_RECOVERY_CLEANUP_ENABLED_FLAG] = "false"
    cleanup_result = helper.build_aws_backed_synthetic_dlq_recovery_proof(env=cleanup_blocked, actor_role="admin")
    require(cleanup_result["blocked_reason"] == "blocked_cleanup_required", "Cleanup flag must be required.")
    assert_no_safe_default_live_side_effects(cleanup_result, "cleanup-blocked DLQ recovery proof")

    rollback_env = dangerous_env(helper)
    rollback_env["AWS_OPTION_A_KILL_SWITCH_ENABLED"] = "true"
    rollback_result = helper.build_aws_backed_synthetic_dlq_recovery_proof(env=rollback_env, actor_role="admin")
    require(rollback_result["blocked_reason"] == "blocked_by_rollback_control", "Kill switch must block DLQ proof.")
    assert_no_safe_default_live_side_effects(rollback_result, "rollback-blocked DLQ recovery proof")

    forbidden_env = dangerous_env(helper)
    forbidden_env["PROVIDER_EXECUTION_ENABLED"] = "true"
    forbidden_result = helper.build_aws_backed_synthetic_dlq_recovery_proof(env=forbidden_env, actor_role="admin")
    require(
        forbidden_result["blocked_reason"] == "blocked_forbidden_live_execution_flag_active",
        "Provider/billing/live worker flags must block.",
    )
    assert_no_safe_default_live_side_effects(forbidden_result, "forbidden-flag DLQ recovery proof")

    for result in [
        base,
        owner_blocked,
        client_result,
        validation_result,
        status_result,
        action_result,
        cleanup_result,
        rollback_result,
        forbidden_result,
    ]:
        require(result["client_safe_failed_or_recovered_status_redacted"] is True, "Client-safe status marker true.")
        require(result["admin_diagnostics_redacted"] is True, "Admin diagnostics marker true.")
        assert_client_safe(result.get("client_safe_status") or {}, "safe-default client status")
        assert_forbidden_side_effects_disabled(result, "safe-default DLQ recovery proof")
        assert_no_forbidden_values(result, "safe-default DLQ recovery proof")


def load_local_env_if_requested(helper) -> None:
    if not helper.enabled(os.environ.get(helper.AWS_BACKED_DLQ_RECOVERY_LOAD_LOCAL_ENV_FLAG)):
        return
    validator = load_module("live_validate_aws_option_a_environment.py", "live_validate_env_for_dlq_recovery")
    metadata = validator.load_local_validation_env(os.environ, ROOT)
    assert_no_forbidden_values_allowing_env_names(metadata, "local env metadata")


def live_mode_requested(helper) -> bool:
    env = os.environ
    return any(
        helper.enabled(env.get(flag))
        for flag in [
            helper.AWS_BACKED_DLQ_RECOVERY_ENABLED_FLAG,
            helper.AWS_BACKED_DLQ_RECOVERY_OWNER_APPROVED_FLAG,
            helper.AWS_BACKED_DLQ_RECOVERY_STATUS_READBACK_ENABLED_FLAG,
            helper.AWS_BACKED_DLQ_RECOVERY_ACTION_ENABLED_FLAG,
        ]
    )


def compact_live_result(result: dict) -> dict:
    admin = result.get("admin_safe_diagnostics") or {}
    return {
        "aws_backed_dlq_recovery_attempted": result.get("aws_backed_dlq_recovery_attempted"),
        "aws_backed_dlq_recovery_passed": result.get("aws_backed_dlq_recovery_passed"),
        "owner_flags_required": result.get("owner_flags_required"),
        "synthetic_dlq_message_present": result.get("synthetic_dlq_message_present"),
        "dlq_message_non_customer": result.get("dlq_message_non_customer"),
        "dlq_message_non_executable": result.get("dlq_message_non_executable"),
        "dlq_reference_redacted": result.get("dlq_reference_redacted"),
        "failure_classification_passed": result.get("failure_classification_passed"),
        "retry_exhaustion_or_failed_terminal_represented": result.get(
            "retry_exhaustion_or_failed_terminal_represented"
        ),
        "admin_recovery_action_represented": result.get("admin_recovery_action_represented"),
        "recovery_or_requeue_attempted": result.get("recovery_or_requeue_attempted"),
        "recovery_or_requeue_passed": result.get("recovery_or_requeue_passed"),
        "client_safe_failed_or_recovered_status_redacted": result.get(
            "client_safe_failed_or_recovered_status_redacted"
        ),
        "admin_diagnostics_redacted": result.get("admin_diagnostics_redacted"),
        "rollback_controls_blocked_when_enabled": result.get("rollback_controls_blocked_when_enabled"),
        "customer_queue_message_consumed": result.get("customer_queue_message_consumed"),
        "provider_call_attempted": result.get("provider_call_attempted"),
        "media_generation_attempted": result.get("media_generation_attempted"),
        "stripe_call_attempted": result.get("stripe_call_attempted"),
        "billing_mutation_attempted": result.get("billing_mutation_attempted"),
        "credit_mutation_attempted": result.get("credit_mutation_attempted"),
        "customer_traffic_attempted": result.get("customer_traffic_attempted"),
        "public_cutover_enabled": result.get("public_cutover_enabled"),
        "synthetic_job_reference_hash": result.get("job_reference_hash") or admin.get("job_reference_hash"),
        "dlq_reference_hash": admin.get("dlq_reference_hash"),
    }


def run_owner_approved_live_mode_if_requested(helper) -> str:
    if not live_mode_requested(helper):
        return "AWS_BACKED_SYNTHETIC_DLQ_RECOVERY_SKIPPED_SAFE_DEFAULT_MODE"

    required_flags = [
        helper.AWS_BACKED_DLQ_RECOVERY_ENABLED_FLAG,
        helper.AWS_BACKED_DLQ_RECOVERY_OWNER_APPROVED_FLAG,
        helper.AWS_BACKED_DLQ_RECOVERY_VALIDATION_CONFIRMED_FLAG,
        helper.AWS_BACKED_DLQ_RECOVERY_STATUS_READBACK_ENABLED_FLAG,
        helper.AWS_BACKED_DLQ_RECOVERY_ACTION_ENABLED_FLAG,
        helper.AWS_BACKED_DLQ_RECOVERY_CLEANUP_ENABLED_FLAG,
    ]
    missing = [flag for flag in required_flags if not helper.enabled(os.environ.get(flag))]
    require(not missing, f"Owner-approved live mode requires every DLQ proof gate: {', '.join(missing)}")

    result = helper.build_aws_backed_synthetic_dlq_recovery_proof(env=os.environ, actor_role="admin")
    print("AWS_BACKED_SYNTHETIC_DLQ_RECOVERY_SANITIZED_RESULT:" + json.dumps(compact_live_result(result), sort_keys=True))
    assert_no_forbidden_values(result, "owner-approved AWS-backed DLQ recovery proof")
    assert_forbidden_side_effects_disabled(result, "owner-approved AWS-backed DLQ recovery proof")

    require(result["status"] == "aws_backed_dlq_recovery_passed", "AWS-backed DLQ recovery proof did not pass.")
    for key in REQUIRED_TRUE_FIELDS:
        require(result.get(key) is True, f"Live proof field must be true: {key}")
    for key in FORBIDDEN_SIDE_EFFECT_KEYS:
        require(result.get(key) is False, f"Live proof forbidden field must be false: {key}")
    assert_client_safe(result.get("client_safe_status") or {}, "live client status")
    admin = result.get("admin_safe_diagnostics") or {}
    require(admin.get("admin_diagnostics_redacted") is True, "Admin diagnostics must be redacted.")
    require(admin.get("recovery_or_requeue_passed") is True, "Admin diagnostics must show recovery proof.")

    rollback_env = dict(os.environ)
    rollback_env["AWS_OPTION_A_KILL_SWITCH_ENABLED"] = "true"
    blocked = helper.build_aws_backed_synthetic_dlq_recovery_proof(env=rollback_env, actor_role="admin")
    require(blocked["blocked_reason"] == "blocked_by_rollback_control", "Rollback must block DLQ recovery proof.")
    assert_no_safe_default_live_side_effects(blocked, "post-live rollback block")
    return "AWS_BACKED_SYNTHETIC_DLQ_RECOVERY_RUN_OWNER_APPROVED_MODE"


def main() -> int:
    helper = load_module(
        "backend/app/runtime/aws_backed_synthetic_dlq_recovery.py",
        "aws_backed_synthetic_dlq_recovery_under_test",
    )
    source = read("backend/app/runtime/aws_backed_synthetic_dlq_recovery.py")

    for forbidden_source_marker in [
        "send_message",
        "receive_message",
        "delete_message",
        "requests.",
        "httpx.",
        "stripe.",
        "runway.",
        "elevenlabs.",
        "kling.",
        "start_worker",
        "run_worker",
        "while True",
    ]:
        require(
            forbidden_source_marker not in source,
            f"AWS-backed DLQ recovery proof must not contain forbidden source marker: {forbidden_source_marker}",
        )
    for marker in [
        "AWS_BACKED_DLQ_RECOVERY_ENABLED",
        "AWS_BACKED_DLQ_RECOVERY_OWNER_APPROVED",
        "AWS_BACKED_DLQ_RECOVERY_VALIDATION_CONFIRMED",
        "AWS_BACKED_DLQ_RECOVERY_STATUS_READBACK_ENABLED",
        "AWS_BACKED_DLQ_RECOVERY_ACTION_ENABLED",
        "AWS_BACKED_DLQ_RECOVERY_CLEANUP_ENABLED",
        "aws_backed_dlq_recovery_attempted",
        "aws_backed_dlq_recovery_passed",
        "owner_flags_required",
        "synthetic_dlq_message_present",
        "dlq_message_non_customer",
        "dlq_message_non_executable",
        "dlq_reference_redacted",
        "failure_classification_passed",
        "retry_exhaustion_or_failed_terminal_represented",
        "admin_recovery_action_represented",
        "recovery_or_requeue_attempted",
        "recovery_or_requeue_passed",
        "client_safe_failed_or_recovered_status_redacted",
        "admin_diagnostics_redacted",
        "rollback_controls_blocked_when_enabled",
        "customer_queue_message_consumed",
        "provider_call_attempted",
        "media_generation_attempted",
        "stripe_call_attempted",
        "billing_mutation_attempted",
        "credit_mutation_attempted",
        "customer_traffic_attempted",
        "public_cutover_enabled",
    ]:
        require(marker in source, f"AWS-backed DLQ recovery source missing marker: {marker}")

    run_safe_default_tests(helper)
    load_local_env_if_requested(helper)
    live_mode_status = run_owner_approved_live_mode_if_requested(helper)

    print(f"AWS_BACKED_SYNTHETIC_DLQ_RECOVERY_VERIFICATION_PASSED:{live_mode_status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
