from __future__ import annotations

from pathlib import Path
import importlib.util
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
        "live_routes_switched",
        "rds_write_attempted",
        "db_connection_attempted",
        "migration_attempted",
        "sqs_send_attempted",
        "s3_upload_attempted",
        "secret_fetch_attempted",
        "aws_call_attempted",
        "provider_call_attempted",
        "stripe_call_attempted",
        "billing_mutation_attempted",
        "credit_mutation_attempted",
    ]:
        require(result.get(key) is False, f"{label} attempted live side effect: {key}")


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
        "123456789012",
        "arn:aws:secretsmanager",
        "postgres://",
    ]:
        require(forbidden not in text, f"{label} leaked forbidden value: {forbidden}")


def ready_validation() -> dict:
    return {
        "status": "completed",
        "service_results": {
            "iam": {"status": "passed", "account": "123456789012"},
            "rds": {"status": "passed", "database_url": "postgres://DATABASE_SECRET_SHOULD_NOT_LEAK"},
            "sqs": {"status": "passed", "queue_url": "https://sqs.example/QUEUE_SECRET_SHOULD_NOT_LEAK"},
            "s3": {"status": "passed", "media_bucket": "MEDIA_BUCKET_SHOULD_NOT_LEAK"},
            "secrets": {"status": "passed", "arn": "arn:aws:secretsmanager:ap-southeast-2:123456789012:secret:PROVIDER_SECRET_SHOULD_NOT_LEAK"},
        },
    }


def ready_env() -> dict:
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


def media_payload() -> dict:
    return {
        "job_id": "job_aws17_durable_enqueue",
        "customer_id": "customer_aws17",
        "tenant_id": "tenant_aws17",
        "actor_role": "admin",
        "requested_by_role": "owner",
        "role": "owner",
        "package_name": "enterprise",
        "entitlement_status": "active",
        "requested_from": "complete_media_popup",
        "task_type": "media_generation",
        "workflow_type": "universal_complete_media",
        "media_type": "complete_video",
        "asset_type": "video",
        "output_type": "complete_video",
        "duration_seconds": 25,
        "aspect_ratio": "9:16",
        "selected_agent": "creative_director_agent",
        "selected_agents": ["creative_director_agent", "media_producer_agent"],
        "agent_ids": ["creative_director_agent", "media_producer_agent"],
        "active_agents": ["creative_director_agent", "media_producer_agent"],
        "multi_agent_media_execution": True,
        "video_provider": "runway",
        "audio_provider": "elevenlabs",
        "prompt": "Create a premium epoxy flooring promo.",
        "media_prompt": "Show polished epoxy floor reveal with CTA text.",
        "approval_status": "admin_unrestricted",
        "credit_reservation_status": "not_required",
        "runway_api_key": "RUNWAY_SECRET_SHOULD_NOT_LEAK",
        "provider_credentials": {"elevenlabs_api_key": "ELEVEN_SECRET_SHOULD_NOT_LEAK"},
        "internal_config": {"stripe_secret_key": "STRIPE_SECRET_SHOULD_NOT_LEAK"},
    }


def main() -> int:
    integration = load_module(
        "backend/app/runtime/aws_option_a_route_integration.py",
        "aws_option_a_route_integration_aws17_under_test",
    )
    catalogue = load_module(
        "backend/app/runtime/real_agent_component_catalogue.py",
        "real_agent_component_catalogue_aws17_under_test",
    )
    source = read("backend/app/runtime/aws_option_a_route_integration.py")
    matrix = read("AWS_OPTION_A_MEDIA_MIGRATION_MATRIX.md")

    for marker in [
        "import boto3",
        "from boto3",
        "psycopg",
        "sqlite3",
        ".connect(",
        ".execute(",
        ".send_message(",
        ".put_object(",
        ".upload_file(",
        "get_secret_value(",
        "requests.",
        "httpx.",
        "stripe.",
    ]:
        require(marker not in source, f"AWS-17 route wiring must not contain live SDK/network marker: {marker}")

    payload = media_payload()
    validation = ready_validation()
    env = ready_env()

    default_eval = integration.evaluate_acceptance_route_mode(payload, env={}, validation_evidence=validation)
    require(default_eval["route_mode"] == "compatibility_runtime_path", "Default route mode must remain compatibility.")
    require(default_eval["default_response_unchanged"] is True, "Default route output must remain unchanged.")
    require(default_eval["short_circuit_route"] is False, "Default route must not short-circuit.")
    assert_no_live_side_effects(default_eval, "default compatibility")
    require(
        default_eval["aws17_durable_enqueue"]["durable_repository"]["prepared"] is False,
        "Default compatibility path must not prepare durable repository work.",
    )
    require(
        default_eval["aws17_durable_enqueue"]["queue_enqueue"]["prepared"] is False,
        "Default compatibility path must not prepare queue work.",
    )

    missing_validation = integration.evaluate_acceptance_route_mode(payload, env=env, validation_evidence={})
    require(missing_validation["route_mode"] == "aws_option_a_enabled_missing_validation", "Missing validation must block route mode.")
    require(missing_validation["short_circuit_route"] is True, "Missing validation with route intent must short-circuit safely.")
    assert_no_live_side_effects(missing_validation, "missing validation")
    missing_boundary = missing_validation["aws17_durable_enqueue"]
    require(missing_boundary["durable_repository"]["prepared"] is False, "Missing validation must not prepare repository write.")
    require(missing_boundary["queue_enqueue"]["prepared"] is False, "Missing validation must not prepare queue send.")
    require(missing_boundary["durable_repository"]["rds_write_attempted"] is False, "Missing validation must not attempt RDS.")
    require(missing_boundary["queue_enqueue"]["sqs_send_attempted"] is False, "Missing validation must not attempt SQS.")

    ready_eval = integration.evaluate_acceptance_route_mode(payload, env=env, validation_evidence=validation)
    require(ready_eval["route_mode"] == "aws_option_a_enabled_ready", "All gates should mark AWS route ready.")
    require(ready_eval["route_execution_allowed"] is True, "Ready route should allow execution at boundary level.")
    assert_no_live_side_effects(ready_eval, "ready dry-run")
    ready_boundary = ready_eval["aws17_durable_enqueue"]
    repository_plan = ready_boundary["durable_repository"]
    queue_plan = ready_boundary["queue_enqueue"]
    require(repository_plan["status"] == "durable_repository_dry_run_prepared", "Repository should be prepared as dry-run by default.")
    require(repository_plan["durable_write_enabled"] is False, "Durable write flag must be disabled by default.")
    require(repository_plan["record_shape"]["job_id"] == "job_aws17_durable_enqueue", "Record shape must preserve job_id.")
    require(repository_plan["record_shape"]["status"] == "accepted", "Record shape must include durable status.")
    require(repository_plan["record_shape"]["media_type"] == "complete_video", "Record shape must include media_type.")
    require(repository_plan["record_shape"]["asset_type"] == "video", "Record shape must include asset_type.")
    require(repository_plan["record_shape"]["agent_id"] == "creative_director_agent", "Record shape must include lead agent_id.")
    require(repository_plan["record_shape"]["created_at"], "Record shape must include created_at.")
    require(repository_plan["record_shape"]["updated_at"], "Record shape must include updated_at.")
    require(repository_plan["record_shape"]["customer_safe"] is True, "Record shape must be customer_safe.")
    require(repository_plan["repository_operations"], "Repository dry-run must include placeholder operations.")
    for operation in repository_plan["repository_operations"]:
        require(operation["mutation_mode"] == "no_db_write_placeholder", "Repository operation must be no-write placeholder.")
        require(operation["rds_write_attempted"] is False, "Repository operation must not attempt RDS write.")
        require(operation["db_connection_attempted"] is False, "Repository operation must not connect to DB.")

    require(queue_plan["status"] == "queue_enqueue_dry_run_prepared", "Queue should be prepared as dry-run by default.")
    require(queue_plan["queue_send_enabled"] is False, "Queue send flag must be disabled by default.")
    require(queue_plan["sqs_send_attempted"] is False, "Queue dry-run must not send SQS.")
    require(queue_plan["queue_message_validation"]["valid"] is True, "Queue message should validate.")
    require(queue_plan["queue_packet"]["job_id"] == "job_aws17_durable_enqueue", "Queue packet must preserve job_id.")
    require(queue_plan["queue_packet"]["selected_agent"] == "creative_director_agent", "Queue packet must preserve selected_agent.")
    require(queue_plan["queue_packet"]["selected_agents"] == payload["selected_agents"], "Queue packet must preserve selected_agents.")
    require(queue_plan["queue_packet"]["agent_ids"] == payload["agent_ids"], "Queue packet must preserve agent_ids.")
    require(queue_plan["queue_packet"]["provider_preferences"]["video_provider"] == "runway", "Queue packet must preserve video provider.")
    require(queue_plan["queue_packet"]["provider_preferences"]["audio_provider"] == "elevenlabs", "Queue packet must preserve audio provider.")

    future_enabled_env = dict(env)
    future_enabled_env["AWS_OPTION_A_DURABLE_WRITE_ENABLED"] = "true"
    future_enabled_env["AWS_OPTION_A_QUEUE_SEND_ENABLED"] = "true"
    future_ready = integration.evaluate_acceptance_route_mode(payload, env=future_enabled_env, validation_evidence=validation)
    future_boundary = future_ready["aws17_durable_enqueue"]
    require(
        future_boundary["durable_repository"]["status"] == "durable_repository_write_flag_enabled_but_adapter_not_invoked",
        "Durable write flag should only mark readiness, not execute in AWS-17.",
    )
    require(
        future_boundary["queue_enqueue"]["status"] == "queue_send_flag_enabled_but_adapter_not_invoked",
        "Queue send flag should only mark readiness, not execute in AWS-17.",
    )
    assert_no_live_side_effects(future_ready, "future write/send flags")
    require(future_boundary["durable_repository"]["rds_write_attempted"] is False, "Durable write flag must still not write in AWS-17.")
    require(future_boundary["queue_enqueue"]["sqs_send_attempted"] is False, "Queue send flag must still not send in AWS-17.")

    status_eval = integration.evaluate_status_route_mode(
        {"job_id": "job_aws17_durable_enqueue", "actor_role": "admin", "package_name": "enterprise", "entitlement_status": "active"},
        env=env,
        validation_evidence=validation,
    )
    require(status_eval["route_kind"] == "status", "Status route must evaluate status kind.")
    require(status_eval["route_execution_allowed"] is True, "Status route should be ready when validation and flags pass.")
    status_plan = status_eval["aws17_durable_enqueue"]["status_persistence"]
    require(status_plan["status"] == "durable_status_read_dry_run_prepared", "Status route should prepare durable read dry-run.")
    require(status_plan["would_read_durable_status"] is True, "Status route should report durable status read readiness.")
    require(status_plan["rds_read_attempted"] is False, "Status route must not read RDS in AWS-17.")
    require(status_plan["db_connection_attempted"] is False, "Status route must not connect to DB in AWS-17.")
    require(status_eval["aws17_durable_enqueue"]["queue_enqueue"]["prepared"] is False, "Status route must not prepare queue enqueue.")

    admin_response = integration.build_admin_route_mode_response(ready_eval)
    require("aws17_durable_enqueue" in admin_response, "Admin response must include AWS-17 dry-run boundary.")
    require("durable_repository" in admin_response, "Admin response must include durable repository diagnostics.")
    require("queue_enqueue" in admin_response, "Admin response must include queue diagnostics.")
    require(admin_response["rds_write_attempted"] is False, "Admin response must not report RDS write.")
    require(admin_response["sqs_send_attempted"] is False, "Admin response must not report SQS send.")
    assert_no_forbidden_values(admin_response, "admin response")

    client_response = integration.build_client_route_mode_response(ready_eval)
    client_text = str(client_response).lower()
    for forbidden_client_marker in [
        "aws",
        "sqs",
        "rds",
        "database",
        "queue",
        "bucket",
        "secret",
        "credential",
        "arn:",
        "validation",
        "diagnostic",
    ]:
        require(forbidden_client_marker not in client_text, f"Client response exposed internal marker: {forbidden_client_marker}")
    assert_no_forbidden_values(client_response, "client response")

    require(len(catalogue.CLIENT_FACING_AGENTS) == catalogue.FINAL_APPROVED_VISIBLE_AGENT_COUNT, "Final 27 visible catalogue must remain intact.")

    for marker in [
        "AWS_DURABLE_WRITE_ENABLED_FLAG",
        "AWS_QUEUE_SEND_ENABLED_FLAG",
        "build_durable_repository_dry_run_plan",
        "build_queue_enqueue_dry_run_plan",
        "build_status_persistence_dry_run_plan",
        "aws17_durable_enqueue_dry_run_boundary",
        "durable_repository_dry_run_prepared",
        "queue_enqueue_dry_run_prepared",
        "durable_status_read_dry_run_prepared",
    ]:
        require(marker in source, f"AWS-17 source missing marker: {marker}")

    for marker in [
        "AWS-17",
        "durable repository/queue adapters",
        "verify_aws_option_a_durable_enqueue_dry_run.py",
        "durable repository and queue packets",
    ]:
        require(marker in matrix, f"Migration matrix missing AWS-17 marker: {marker}")

    print("AWS_OPTION_A_DURABLE_ENQUEUE_DRY_RUN_VERIFICATION_PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
