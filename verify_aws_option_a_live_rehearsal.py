from __future__ import annotations

from pathlib import Path
import importlib.util
import json
import os
import re
import sys


ROOT = Path(__file__).resolve().parent


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


def assert_no_live_side_effects(result: dict, label: str) -> None:
    for key in [
        "rds_write_attempted",
        "db_connection_attempted",
        "sqs_send_attempted",
        "s3_upload_attempted",
        "network_call_attempted",
        "secret_fetch_attempted",
        "provider_call_attempted",
        "stripe_call_attempted",
        "billing_mutation_attempted",
        "credit_mutation_attempted",
        "media_worker_started",
        "live_routes_switched",
    ]:
        require(result.get(key) is False, f"{label} attempted live side effect: {key}")


def assert_no_provider_finance_side_effects(result: dict, label: str) -> None:
    for key in [
        "provider_call_attempted",
        "stripe_call_attempted",
        "billing_mutation_attempted",
        "credit_mutation_attempted",
        "media_worker_started",
        "secret_fetch_attempted",
        "secrets_manager_value_retrieved",
        "live_routes_switched",
        "public_production_cutover_enabled",
    ]:
        require(result.get(key) is False, f"{label} attempted forbidden side effect: {key}")


def assert_no_forbidden_values(value: object, label: str) -> None:
    text = str(value)
    for forbidden in [
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
        "https://sqs.example",
        "postgres://",
        "DATABASE_URL=postgres",
        "DATABASE_URL",
        "AWS_MEDIA_QUEUE_URL",
        "AWS_MEDIA_DLQ_URL",
        "stripe_secret_key=",
        "runway_api_key=",
    ]:
        require(forbidden not in text, f"{label} leaked forbidden value: {forbidden}")


def print_sanitized_live_result(result: dict) -> None:
    print("AWS_OPTION_A_LIVE_REHEARSAL_SANITIZED_RESULT:" + json.dumps(result, sort_keys=True))


def dangerous_env() -> dict:
    return {
        "AWS_OPTION_A_ENABLED": "true",
        "AWS_OPTION_A_ROUTE_CUTOVER_ENABLED": "true",
        "AWS_OPTION_A_ACCEPTANCE_CUTOVER_ENABLED": "true",
        "AWS_OPTION_A_STATUS_CUTOVER_ENABLED": "true",
        "AWS_OPTION_A_DURABLE_WRITE_ENABLED": "true",
        "AWS_OPTION_A_QUEUE_SEND_ENABLED": "true",
        "AWS_REGION": "ap-southeast-2",
        "DATABASE_URL": "postgres://DATABASE_SECRET_SHOULD_NOT_LEAK",
        "AWS_RDS_SECRET_ARN": "arn:aws:secretsmanager:ap-southeast-2:123456789012:secret:DATABASE_SECRET_SHOULD_NOT_LEAK",
        "AWS_MEDIA_QUEUE_URL": "https://sqs.example/QUEUE_SECRET_SHOULD_NOT_LEAK",
        "AWS_MEDIA_DLQ_URL": "https://sqs.example/DLQ_SECRET_SHOULD_NOT_LEAK",
        "AWS_MEDIA_S3_BUCKET": "MEDIA_BUCKET_SHOULD_NOT_LEAK",
        "AWS_UPLOADS_S3_BUCKET": "UPLOAD_BUCKET_SHOULD_NOT_LEAK",
        "AWS_PROVIDER_SECRETS_PREFIX": "/provider/PROVIDER_SECRET_SHOULD_NOT_LEAK",
    }


def rehearsal_payload() -> dict:
    return {
        "job_id": "aws20_rehearsal_non_customer_verifier",
        "customer_id": "aws20_rehearsal_non_customer",
        "task_type": "aws20_rehearsal_non_customer",
        "workflow_type": "aws20_live_rehearsal",
        "non_executable": True,
        "do_not_process": True,
        "provider_call_allowed": False,
        "media_generation_allowed": False,
        "runway_api_key": "RUNWAY_SECRET_SHOULD_NOT_LEAK",
        "internal_config": {"stripe_secret_key": "STRIPE_SECRET_SHOULD_NOT_LEAK"},
    }


def run_safe_default_tests(helper) -> None:
    payload = rehearsal_payload()
    base = helper.build_aws20_live_rehearsal(env={}, actor_role="admin", payload=payload)
    require(base["status"] == "safe_default_no_live_rehearsal", "Default rehearsal must be safe no-live.")
    require(base["flags"]["live_rehearsal_enabled"] is False, "Rehearsal flag must default false.")
    require(base["flags"]["owner_approved"] is False, "Owner approval must default false.")
    require(base["blocked_reason"] == "blocked_rehearsal_not_enabled", "Default should be blocked by rehearsal flag.")
    assert_no_live_side_effects(base, "default rehearsal")
    assert_no_provider_finance_side_effects(base, "default rehearsal")
    assert_no_forbidden_values(base, "default rehearsal")

    route_only = helper.build_aws20_live_rehearsal(env=dangerous_env(), actor_role="admin", payload=payload)
    require(route_only["blocked_reason"] == "blocked_rehearsal_not_enabled", "Route/durable flags alone must not rehearse.")
    assert_no_live_side_effects(route_only, "route flags only")

    missing_owner = dict(dangerous_env())
    missing_owner.update({
        "AWS_OPTION_A_LIVE_REHEARSAL_ENABLED": "true",
        "AWS_OPTION_A_REHEARSAL_RDS_WRITE_ENABLED": "true",
        "AWS_OPTION_A_REHEARSAL_SQS_SEND_ENABLED": "true",
        "AWS_OPTION_A_REHEARSAL_S3_WRITE_ENABLED": "true",
    })
    owner_blocked = helper.build_aws20_live_rehearsal(env=missing_owner, actor_role="admin", payload=payload)
    require(owner_blocked["blocked_reason"] == "blocked_owner_approval_required", "Owner approval must be required.")
    assert_no_live_side_effects(owner_blocked, "missing owner approval")

    client_blocked_env = dict(missing_owner)
    client_blocked_env["AWS_OPTION_A_LIVE_REHEARSAL_OWNER_APPROVED"] = "true"
    client_blocked = helper.build_aws20_live_rehearsal(env=client_blocked_env, actor_role="client", payload=payload)
    require(client_blocked["blocked_reason"] == "blocked_client_not_authorized", "Client must never trigger rehearsal.")
    require(client_blocked["client_trigger_allowed"] is False, "Client trigger must be false.")
    assert_no_live_side_effects(client_blocked, "client blocked")

    rollback_env = dict(client_blocked_env)
    rollback_env["AWS_OPTION_A_KILL_SWITCH_ENABLED"] = "true"
    rollback_blocked = helper.build_aws20_live_rehearsal(env=rollback_env, actor_role="admin", payload=payload)
    require(rollback_blocked["blocked_reason"] == "blocked_by_rollback_control", "Rollback kill switch must block rehearsal.")
    require(rollback_blocked["kill_switch_active"] is True, "Kill switch state must be visible to admin-safe output.")
    assert_no_live_side_effects(rollback_blocked, "rollback blocked")

    no_resource_flags = dict(dangerous_env())
    no_resource_flags.update({
        "AWS_OPTION_A_LIVE_REHEARSAL_ENABLED": "true",
        "AWS_OPTION_A_LIVE_REHEARSAL_OWNER_APPROVED": "true",
    })
    resources_skipped = helper.build_aws20_live_rehearsal(env=no_resource_flags, actor_role="admin", payload=payload)
    require(resources_skipped["blocked_reason"] == "", "Enabled rehearsal with owner approval but no resources should not be globally blocked.")
    for resource, item in resources_skipped["resource_results"].items():
        require(item["status"] == "skipped_resource_flag_disabled", f"{resource} must require a specific resource flag.")
    assert_no_live_side_effects(resources_skipped, "resource flags disabled")

    for result in [base, route_only, owner_blocked, client_blocked, rollback_blocked, resources_skipped]:
        require(result["rehearsal_artifact_marker"] == "aws20_rehearsal/test/non_customer", "Rehearsal artifacts must be clearly marked.")
        require(result["synthetic_non_customer_job"] is True, "Rehearsal must use synthetic non-customer job.")
        require(result["client_safe_view"]["internal_config_exposed"] is False, "Client safe view must hide internal config.")
        assert_no_forbidden_values(result["client_safe_view"], "client safe view")


def live_mode_requested(helper) -> bool:
    env = os.environ
    return (
        helper.enabled(env.get(helper.AWS_OPTION_A_LIVE_REHEARSAL_ENABLED_FLAG))
        and helper.enabled(env.get(helper.AWS_OPTION_A_LIVE_REHEARSAL_OWNER_APPROVED_FLAG))
        and (
            helper.enabled(env.get(helper.AWS_OPTION_A_REHEARSAL_RDS_WRITE_ENABLED_FLAG))
            or helper.enabled(env.get(helper.AWS_OPTION_A_REHEARSAL_SQS_SEND_ENABLED_FLAG))
            or helper.enabled(env.get(helper.AWS_OPTION_A_REHEARSAL_S3_WRITE_ENABLED_FLAG))
        )
    )


def run_owner_approved_live_mode_if_requested(helper) -> str:
    if not live_mode_requested(helper):
        return "LIVE_AWS_REHEARSAL_SKIPPED_SAFE_DEFAULT_MODE"

    result = helper.build_aws20_live_rehearsal(env=os.environ, actor_role="admin", payload={})
    assert_no_provider_finance_side_effects(result, "owner-approved live rehearsal")
    assert_no_forbidden_values(result, "owner-approved live rehearsal")
    print_sanitized_live_result(result)
    require(result["status"] == "live_rehearsal_executed", "Owner-approved live mode should execute at least one resource rehearsal.")

    env = os.environ
    resource_results = result["resource_results"]
    if helper.enabled(env.get(helper.AWS_OPTION_A_REHEARSAL_RDS_WRITE_ENABLED_FLAG)):
        require(resource_results["rds"]["status"] == "passed", "RDS rehearsal flag was enabled but did not pass.")
        require(resource_results["rds"]["transaction_rolled_back"] is True, "RDS rehearsal must roll back transaction.")
    if helper.enabled(env.get(helper.AWS_OPTION_A_REHEARSAL_SQS_SEND_ENABLED_FLAG)):
        sqs = resource_results["sqs"]
        for field in [
            "sqs_attempted",
            "sqs_passed",
            "sqs_error_type",
            "sqs_error_code",
            "sqs_error_category",
            "sqs_region_present",
            "sqs_queue_url_present",
            "sqs_queue_url_hash_prefix",
            "sqs_queue_type_standard_or_fifo",
            "sqs_message_group_id_required_or_used",
            "sqs_message_deduplication_id_used",
            "sqs_message_non_customer",
            "sqs_message_non_executable",
            "sqs_message_body_size",
            "sqs_message_id_hash_prefix",
            "next_operator_action",
        ]:
            require(field in sqs, f"SQS diagnostic field missing: {field}")
        require(sqs["sqs_message_non_customer"] is True, "SQS rehearsal message must be non-customer.")
        require(sqs["sqs_message_non_executable"] is True, "SQS rehearsal message must be non-executable.")
        require(str(sqs.get("sqs_queue_url_hash_prefix") or "").strip() != "", "SQS must expose a queue URL hash prefix, not a raw URL.")
        require(resource_results["sqs"]["status"] == "passed", f"SQS rehearsal flag was enabled but did not pass; category={sqs.get('sqs_error_category')}; action={sqs.get('next_operator_action')}")
        require(resource_results["sqs"]["message_marked_non_executable"] is True, "SQS rehearsal message must be non-executable.")
        require(resource_results["sqs"]["sqs_passed"] is True, "SQS diagnostics must mark pass only after send succeeds.")
    if helper.enabled(env.get(helper.AWS_OPTION_A_REHEARSAL_S3_WRITE_ENABLED_FLAG)):
        require(resource_results["s3"]["status"] == "passed", "S3 rehearsal flag was enabled but did not pass.")
        require(resource_results["s3"]["read_back_passed"] is True, "S3 rehearsal must read back marker.")

    rollback_env = dict(os.environ)
    rollback_env["AWS_OPTION_A_KILL_SWITCH_ENABLED"] = "true"
    blocked = helper.build_aws20_live_rehearsal(env=rollback_env, actor_role="admin", payload={})
    require(blocked["blocked_reason"] == "blocked_by_rollback_control", "Rollback must block owner-approved live rehearsal.")
    assert_no_live_side_effects(blocked, "live mode rollback block")
    return "LIVE_AWS_REHEARSAL_RUN_OWNER_APPROVED_MODE"


def main() -> int:
    helper = load_module(
        "backend/app/runtime/aws_option_a_live_rehearsal.py",
        "aws_option_a_live_rehearsal_under_test",
    )
    catalogue = load_module(
        "backend/app/runtime/real_agent_component_catalogue.py",
        "real_agent_component_catalogue_aws20_under_test",
    )
    source = read("backend/app/runtime/aws_option_a_live_rehearsal.py")
    matrix = read("AWS_OPTION_A_MEDIA_MIGRATION_MATRIX.md")

    for marker in ["requests.", "httpx.", "stripe.", "runway.", "elevenlabs.", "kling."]:
        require(marker not in source, f"AWS-20 helper must not contain provider/Stripe/network library marker: {marker}")
    for marker in [
        "AWS_OPTION_A_LIVE_REHEARSAL_ENABLED",
        "AWS_OPTION_A_LIVE_REHEARSAL_OWNER_APPROVED",
        "AWS_OPTION_A_REHEARSAL_RDS_WRITE_ENABLED",
        "AWS_OPTION_A_REHEARSAL_SQS_SEND_ENABLED",
        "AWS_OPTION_A_REHEARSAL_S3_WRITE_ENABLED",
        "AWS_OPTION_A_REHEARSAL_CLEANUP_ENABLED",
        "AWS_OPTION_A_REHEARSAL_ONLY_SQS",
        "aws20_live_rehearsal_boundary",
        "aws20_rehearsal_non_customer",
        "build_aws20_live_rehearsal",
    ]:
        require(marker in source, f"AWS-20 source missing marker: {marker}")
    for marker in [
        "sqs_attempted",
        "sqs_passed",
        "sqs_error_type",
        "sqs_error_code",
        "sqs_error_category",
        "sqs_region_present",
        "sqs_queue_url_present",
        "sqs_queue_url_hash_prefix",
        "sqs_queue_type_standard_or_fifo",
        "sqs_message_group_id_required_or_used",
        "sqs_message_deduplication_id_used",
        "sqs_message_non_customer",
        "sqs_message_non_executable",
        "sqs_message_body_size",
        "sqs_message_id_hash_prefix",
        "next_operator_action",
        "missing_queue_url",
        "missing_region",
        "invalid_credentials_or_signature",
        "access_denied",
        "nonexistent_queue",
        "region_mismatch",
        "fifo_parameter_missing",
        "queue_policy_denied",
        "malformed_message",
        "network_or_endpoint",
        "missing_boto3_dependency",
        "unknown_sqs_error",
    ]:
        require(marker in source, f"AWS-20 SQS diagnostics missing marker: {marker}")

    run_safe_default_tests(helper)
    live_mode_status = run_owner_approved_live_mode_if_requested(helper)

    require(len(catalogue.CLIENT_FACING_AGENTS) == catalogue.FINAL_APPROVED_VISIBLE_AGENT_COUNT, "Final 27 visible catalogue must remain intact.")
    row_ids = [int(match) for match in re.findall(r"AWS-(\d+)", matrix)]
    require(row_ids and max(row_ids) <= 20, "Migration matrix must remain contained through AWS-20.")
    require("AWS-21" not in matrix, "Migration matrix must not add AWS-21 or later.")
    for marker in [
        "AWS-20",
        "controlled live AWS integration rehearsal boundary",
        "aws_option_a_live_rehearsal.py",
        "verify_aws_option_a_live_rehearsal.py",
        "safe default verifier passes",
        "live rehearsal pending owner-approved mode",
        "AWS-17 through AWS-20",
    ]:
        require(marker in matrix, f"Migration matrix missing AWS-20 marker: {marker}")

    print(f"AWS_OPTION_A_LIVE_REHEARSAL_VERIFICATION_PASSED:{live_mode_status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
