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


SIDE_EFFECT_KEYS = {
    "live_durable_write_attempted",
    "live_status_readback_attempted",
    "live_queue_send_attempted",
    "rds_write_attempted",
    "db_connection_attempted",
    "sqs_send_attempted",
    "s3_upload_attempted",
    "secret_fetch_attempted",
    "secrets_manager_value_retrieved",
    "provider_call_attempted",
    "paid_provider_calls_started",
    "stripe_call_attempted",
    "billing_mutation_attempted",
    "credit_mutation_attempted",
    "media_worker_started",
    "worker_started",
    "public_cutover_enabled",
    "public_production_cutover_enabled",
}


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


def assert_no_live_side_effects(value: Any, label: str) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if key in SIDE_EFFECT_KEYS:
                require(item is False, f"{label} attempted live side effect: {key}")
            assert_no_live_side_effects(item, label)
    elif isinstance(value, list):
        for item in value:
            assert_no_live_side_effects(item, label)


def assert_forbidden_paid_side_effects_disabled(result: dict, label: str) -> None:
    for key in [
        "worker_started",
        "media_worker_started",
        "provider_call_attempted",
        "paid_provider_calls_started",
        "stripe_call_attempted",
        "billing_mutation_attempted",
        "credit_mutation_attempted",
        "public_cutover_enabled",
        "public_production_cutover_enabled",
        "secret_fetch_attempted",
        "secrets_manager_value_retrieved",
    ]:
        require(result.get(key) is False, f"{label} enabled forbidden live side effect: {key}")


def dangerous_env() -> dict:
    return {
        "AWS_OPTION_A_ENABLED": "true",
        "AWS_OPTION_A_ROUTE_CUTOVER_ENABLED": "true",
        "AWS_OPTION_A_ACCEPTANCE_CUTOVER_ENABLED": "true",
        "AWS_OPTION_A_STATUS_CUTOVER_ENABLED": "true",
        "AWS_REGION": "ap-southeast-2",
        "DATABASE_URL": "postgres://DATABASE_SECRET_SHOULD_NOT_LEAK",
        "AWS_RDS_SECRET_ARN": "arn:aws:secretsmanager:ap-southeast-2:123456789012:secret:DATABASE_SECRET_SHOULD_NOT_LEAK",
        "AWS_MEDIA_QUEUE_URL": "https://sqs.example/QUEUE_SECRET_SHOULD_NOT_LEAK",
        "AWS_MEDIA_DLQ_URL": "https://sqs.example/DLQ_SECRET_SHOULD_NOT_LEAK",
        "AWS_MEDIA_S3_BUCKET": "MEDIA_BUCKET_SHOULD_NOT_LEAK",
        "AWS_UPLOADS_S3_BUCKET": "UPLOAD_BUCKET_SHOULD_NOT_LEAK",
        "AWS_PROVIDER_SECRETS_PREFIX": "/provider/PROVIDER_SECRET_SHOULD_NOT_LEAK",
    }


def payload() -> dict:
    return {
        "job_id": "aws_live_handoff_non_customer_verifier",
        "actor_role": "admin",
        "provider_credentials": {"elevenlabs_api_key": "ELEVEN_SECRET_SHOULD_NOT_LEAK"},
        "internal_config": {"stripe_secret_key": "STRIPE_SECRET_SHOULD_NOT_LEAK"},
        "runway_api_key": "RUNWAY_SECRET_SHOULD_NOT_LEAK",
    }


def live_flags(helper) -> dict:
    env = dangerous_env()
    env.update({
        helper.AWS_OPTION_A_LIVE_DURABLE_HANDOFF_ENABLED_FLAG: "true",
        helper.AWS_OPTION_A_LIVE_DURABLE_HANDOFF_OWNER_APPROVED_FLAG: "true",
        helper.AWS_OPTION_A_LIVE_DURABLE_VALIDATION_CONFIRMED_FLAG: "true",
        helper.AWS_OPTION_A_LIVE_DURABLE_WRITE_ENABLED_FLAG: "true",
        helper.AWS_OPTION_A_LIVE_DURABLE_QUEUE_SEND_ENABLED_FLAG: "true",
        helper.AWS_OPTION_A_LIVE_DURABLE_STATUS_READ_ENABLED_FLAG: "true",
        helper.AWS_OPTION_A_LIVE_DURABLE_CLEANUP_ENABLED_FLAG: "true",
    })
    return env


def run_safe_default_tests(helper) -> None:
    base = helper.build_live_synthetic_durable_handoff(env={}, actor_role="admin", payload=payload())
    require(base["status"] == "safe_default_no_live_handoff", "Default mode must not run live handoff.")
    require(base["blocked_reason"] == "blocked_live_durable_handoff_not_enabled", "Default must be blocked by handoff flag.")
    require(base["rollback_controls_blocked_when_enabled"] is True, "Rollback controls must be proven to block when enabled.")
    assert_no_live_side_effects(base, "default handoff")
    assert_no_forbidden_values(base, "default handoff")

    route_only = helper.build_live_synthetic_durable_handoff(env=dangerous_env(), actor_role="admin", payload=payload())
    require(route_only["blocked_reason"] == "blocked_live_durable_handoff_not_enabled", "Route flags alone must not run handoff.")
    assert_no_live_side_effects(route_only, "route-only handoff")
    assert_no_forbidden_values(route_only, "route-only handoff")

    missing_owner = dict(dangerous_env())
    missing_owner.update({
        helper.AWS_OPTION_A_LIVE_DURABLE_HANDOFF_ENABLED_FLAG: "true",
        helper.AWS_OPTION_A_LIVE_DURABLE_WRITE_ENABLED_FLAG: "true",
        helper.AWS_OPTION_A_LIVE_DURABLE_QUEUE_SEND_ENABLED_FLAG: "true",
        helper.AWS_OPTION_A_LIVE_DURABLE_STATUS_READ_ENABLED_FLAG: "true",
        helper.AWS_OPTION_A_LIVE_DURABLE_CLEANUP_ENABLED_FLAG: "true",
    })
    owner_blocked = helper.build_live_synthetic_durable_handoff(env=missing_owner, actor_role="admin", payload=payload())
    require(owner_blocked["blocked_reason"] == "blocked_owner_approval_required", "Owner approval must be required.")
    assert_no_live_side_effects(owner_blocked, "owner-blocked handoff")

    client_blocked = dict(missing_owner)
    client_blocked[helper.AWS_OPTION_A_LIVE_DURABLE_HANDOFF_OWNER_APPROVED_FLAG] = "true"
    client_result = helper.build_live_synthetic_durable_handoff(env=client_blocked, actor_role="client", payload=payload())
    require(client_result["blocked_reason"] == "blocked_client_not_authorized", "Client must not trigger live handoff.")
    assert_no_live_side_effects(client_result, "client-blocked handoff")

    missing_validation = dict(client_blocked)
    validation_result = helper.build_live_synthetic_durable_handoff(env=missing_validation, actor_role="admin", payload=payload())
    require(validation_result["blocked_reason"] == "blocked_validation_confirmation_required", "Validation acknowledgement must be required.")
    assert_no_live_side_effects(validation_result, "validation-blocked handoff")

    cleanup_missing = live_flags(helper)
    cleanup_missing[helper.AWS_OPTION_A_LIVE_DURABLE_CLEANUP_ENABLED_FLAG] = "false"
    cleanup_result = helper.build_live_synthetic_durable_handoff(env=cleanup_missing, actor_role="admin", payload=payload())
    require(cleanup_result["blocked_reason"] == "blocked_cleanup_required", "Cleanup flag must be required for live DB proof.")
    assert_no_live_side_effects(cleanup_result, "cleanup-blocked handoff")

    rollback_env = live_flags(helper)
    rollback_env["AWS_OPTION_A_KILL_SWITCH_ENABLED"] = "true"
    rollback_result = helper.build_live_synthetic_durable_handoff(env=rollback_env, actor_role="admin", payload=payload())
    require(rollback_result["blocked_reason"] == "blocked_by_rollback_control", "Kill switch must block live handoff.")
    assert_no_live_side_effects(rollback_result, "rollback-blocked handoff")

    forbidden_env = live_flags(helper)
    forbidden_env["AWS_MEDIA_WORKER_ENABLED"] = "true"
    forbidden_result = helper.build_live_synthetic_durable_handoff(env=forbidden_env, actor_role="admin", payload=payload())
    require(forbidden_result["blocked_reason"] == "blocked_forbidden_live_execution_flag_active", "Worker/provider/billing flags must block.")
    assert_no_live_side_effects(forbidden_result, "forbidden-flag handoff")

    for result in [
        base,
        route_only,
        owner_blocked,
        client_result,
        validation_result,
        cleanup_result,
        rollback_result,
        forbidden_result,
    ]:
        require(result["synthetic_non_customer_job"] is True, "Handoff must use synthetic non-customer job.")
        require(result["queue_packet_non_customer"] is True, "Queue packet marker must remain non-customer.")
        require(result["queue_packet_non_executable"] is True, "Queue packet marker must remain non-executable.")
        require(result["client_safe_status_redacted"] is True, "Client-safe status must be redacted.")
        require(result["admin_diagnostics_redacted"] is True, "Admin diagnostics must be redacted.")
        assert_forbidden_paid_side_effects_disabled(result, "safe default handoff")
        assert_no_forbidden_values(result, "safe default handoff")


def load_local_env_if_requested(helper) -> None:
    if not helper.enabled(os.environ.get(helper.AWS_OPTION_A_LIVE_DURABLE_HANDOFF_LOAD_LOCAL_ENV_FLAG)):
        return
    validator = load_module("live_validate_aws_option_a_environment.py", "live_validate_env_for_handoff")
    metadata = validator.load_local_validation_env(os.environ, ROOT)
    assert_no_forbidden_values(metadata, "local env metadata")


def live_mode_requested(helper) -> bool:
    env = os.environ
    return (
        helper.enabled(env.get(helper.AWS_OPTION_A_LIVE_DURABLE_HANDOFF_ENABLED_FLAG))
        or helper.enabled(env.get(helper.AWS_OPTION_A_LIVE_DURABLE_HANDOFF_OWNER_APPROVED_FLAG))
        or helper.enabled(env.get(helper.AWS_OPTION_A_LIVE_DURABLE_WRITE_ENABLED_FLAG))
        or helper.enabled(env.get(helper.AWS_OPTION_A_LIVE_DURABLE_QUEUE_SEND_ENABLED_FLAG))
        or helper.enabled(env.get(helper.AWS_OPTION_A_LIVE_DURABLE_STATUS_READ_ENABLED_FLAG))
    )


def print_sanitized_live_result(result: dict) -> None:
    print("LIVE_SYNTHETIC_DURABLE_HANDOFF_SANITIZED_RESULT:" + json.dumps(result, sort_keys=True))


def run_owner_approved_live_mode_if_requested(helper) -> str:
    if not live_mode_requested(helper):
        return "LIVE_SYNTHETIC_DURABLE_HANDOFF_SKIPPED_SAFE_DEFAULT_MODE"

    env = os.environ
    required_flags = [
        helper.AWS_OPTION_A_LIVE_DURABLE_HANDOFF_ENABLED_FLAG,
        helper.AWS_OPTION_A_LIVE_DURABLE_HANDOFF_OWNER_APPROVED_FLAG,
        helper.AWS_OPTION_A_LIVE_DURABLE_VALIDATION_CONFIRMED_FLAG,
        helper.AWS_OPTION_A_LIVE_DURABLE_WRITE_ENABLED_FLAG,
        helper.AWS_OPTION_A_LIVE_DURABLE_QUEUE_SEND_ENABLED_FLAG,
        helper.AWS_OPTION_A_LIVE_DURABLE_STATUS_READ_ENABLED_FLAG,
        helper.AWS_OPTION_A_LIVE_DURABLE_CLEANUP_ENABLED_FLAG,
        "AWS_OPTION_A_ENABLED",
        "AWS_OPTION_A_ROUTE_CUTOVER_ENABLED",
        "AWS_OPTION_A_ACCEPTANCE_CUTOVER_ENABLED",
        "AWS_OPTION_A_STATUS_CUTOVER_ENABLED",
    ]
    missing = [flag for flag in required_flags if not helper.enabled(env.get(flag))]
    require(not missing, f"Owner-approved live mode requires every handoff gate: {', '.join(missing)}")

    result = helper.build_live_synthetic_durable_handoff(env=os.environ, actor_role="admin", payload={})
    print_sanitized_live_result(result)
    assert_no_forbidden_values(result, "owner-approved live durable handoff")
    assert_forbidden_paid_side_effects_disabled(result, "owner-approved live durable handoff")

    require(result["status"] == "live_synthetic_durable_handoff_passed", "Live durable handoff did not pass.")
    for key in [
        "live_durable_write_attempted",
        "live_durable_write_passed",
        "live_status_readback_attempted",
        "live_status_readback_passed",
        "live_queue_send_attempted",
        "live_queue_send_passed",
        "synthetic_non_customer_job",
        "queue_packet_non_customer",
        "queue_packet_non_executable",
        "rollback_or_cleanup_performed",
        "client_safe_status_redacted",
        "admin_diagnostics_redacted",
        "rollback_controls_blocked_when_enabled",
    ]:
        require(result.get(key) is True, f"Live proof field must be true: {key}")
    for key in [
        "worker_started",
        "provider_call_attempted",
        "stripe_call_attempted",
        "billing_mutation_attempted",
        "credit_mutation_attempted",
        "public_cutover_enabled",
    ]:
        require(result.get(key) is False, f"Live proof forbidden field must be false: {key}")

    db = result["db_result"]
    queue = result["queue_result"]
    require(db["status"] == "passed", "DB live durable handoff must pass.")
    require(db["cleanup_performed"] is True, "DB cleanup must be performed.")
    require(queue["status"] == "passed", "SQS live queue handoff must pass.")
    require(str(queue.get("sqs_message_id_hash_prefix") or "").strip(), "SQS proof must expose only a message hash prefix.")
    require(str(queue.get("sqs_queue_url_hash_prefix") or "").strip(), "SQS proof must expose only a queue hash prefix.")

    rollback_env = dict(os.environ)
    rollback_env["AWS_OPTION_A_KILL_SWITCH_ENABLED"] = "true"
    blocked = helper.build_live_synthetic_durable_handoff(env=rollback_env, actor_role="admin", payload={})
    require(blocked["blocked_reason"] == "blocked_by_rollback_control", "Rollback must block live handoff after proof.")
    assert_no_live_side_effects(blocked, "post-live rollback block")
    return "LIVE_SYNTHETIC_DURABLE_HANDOFF_RUN_OWNER_APPROVED_MODE"


def main() -> int:
    helper = load_module(
        "backend/app/runtime/aws_option_a_live_durable_handoff.py",
        "aws_option_a_live_durable_handoff_under_test",
    )
    source = read("backend/app/runtime/aws_option_a_live_durable_handoff.py")

    for marker in ["requests.", "httpx.", "stripe.", "runway.", "elevenlabs.", "kling."]:
        require(marker not in source, f"Live durable handoff helper must not contain paid provider/Stripe marker: {marker}")
    for marker in [
        "AWS_OPTION_A_LIVE_DURABLE_HANDOFF_ENABLED",
        "AWS_OPTION_A_LIVE_DURABLE_HANDOFF_OWNER_APPROVED",
        "AWS_OPTION_A_LIVE_DURABLE_VALIDATION_CONFIRMED",
        "AWS_OPTION_A_LIVE_DURABLE_WRITE_ENABLED",
        "AWS_OPTION_A_LIVE_DURABLE_QUEUE_SEND_ENABLED",
        "AWS_OPTION_A_LIVE_DURABLE_STATUS_READ_ENABLED",
        "AWS_OPTION_A_LIVE_DURABLE_CLEANUP_ENABLED",
        "live_durable_write_attempted",
        "live_durable_write_passed",
        "live_status_readback_attempted",
        "live_status_readback_passed",
        "live_queue_send_attempted",
        "live_queue_send_passed",
        "synthetic_non_customer_job",
        "queue_packet_non_customer",
        "queue_packet_non_executable",
        "rollback_or_cleanup_performed",
        "client_safe_status_redacted",
        "admin_diagnostics_redacted",
        "rollback_controls_blocked_when_enabled",
        "worker_started",
        "provider_call_attempted",
        "stripe_call_attempted",
        "billing_mutation_attempted",
        "credit_mutation_attempted",
        "public_cutover_enabled",
    ]:
        require(marker in source, f"Live durable handoff source missing marker: {marker}")

    run_safe_default_tests(helper)
    load_local_env_if_requested(helper)
    live_mode_status = run_owner_approved_live_mode_if_requested(helper)
    print(f"LIVE_SYNTHETIC_DURABLE_HANDOFF_VERIFICATION_PASSED:{live_mode_status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
