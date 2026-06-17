from __future__ import annotations

from pathlib import Path
import importlib.util
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
        "RDS_PASSWORD_SHOULD_NOT_LEAK",
        "123456789012",
        "arn:aws:secretsmanager",
        "postgres://",
        "DATABASE_URL=postgres",
        "stripe_secret_key=",
        "runway_api_key=",
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


def rollback_reason() -> str:
    return (
        "Incident rollback: DATABASE_URL=postgres://DATABASE_SECRET_SHOULD_NOT_LEAK "
        "runway_api_key=RUNWAY_SECRET_SHOULD_NOT_LEAK "
        "stripe_secret_key=STRIPE_SECRET_SHOULD_NOT_LEAK "
        "RDS_PASSWORD=RDS_PASSWORD_SHOULD_NOT_LEAK "
        "arn:aws:secretsmanager:ap-southeast-2:123456789012:secret:PROVIDER_SECRET_SHOULD_NOT_LEAK"
    )


def media_payload() -> dict:
    return {
        "job_id": "job_aws18_rollback",
        "customer_id": "customer_aws18",
        "tenant_id": "tenant_aws18",
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
        "video_provider": "future_video_provider",
        "audio_provider": "future_audio_provider",
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
        "aws_option_a_route_integration_aws18_under_test",
    )
    rollback = load_module(
        "backend/app/runtime/aws_option_a_rollback_controls.py",
        "aws_option_a_rollback_controls_under_test",
    )
    catalogue = load_module(
        "backend/app/runtime/real_agent_component_catalogue.py",
        "real_agent_component_catalogue_aws18_under_test",
    )
    integration_source = read("backend/app/runtime/aws_option_a_route_integration.py")
    rollback_source = read("backend/app/runtime/aws_option_a_rollback_controls.py")
    matrix = read("AWS_OPTION_A_MEDIA_MIGRATION_MATRIX.md")

    for source_name, source in {
        "route integration": integration_source,
        "rollback controls": rollback_source,
    }.items():
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
            require(marker not in source, f"AWS-18 {source_name} must not contain live SDK/network marker: {marker}")

    payload = media_payload()
    validation = ready_validation()
    env = ready_env()

    default_eval = integration.evaluate_acceptance_route_mode(payload, env={}, validation_evidence=validation)
    require(default_eval["route_mode"] == "compatibility_runtime_path", "Flags-off default must remain compatibility.")
    require(default_eval["default_response_unchanged"] is True, "Flags-off default response must remain unchanged.")
    require(default_eval["short_circuit_route"] is False, "Flags-off default must not short-circuit.")
    require(default_eval["rollback_control_active"] is False, "Rollback control must be inactive by default.")
    assert_no_live_side_effects(default_eval, "default compatibility")

    ready_eval = integration.evaluate_acceptance_route_mode(payload, env=env, validation_evidence=validation)
    require(ready_eval["route_mode"] == "aws_option_a_enabled_ready", "Ready route should remain ready when rollback is clear.")
    require(ready_eval["route_execution_allowed"] is True, "Ready route should allow dry-run path when rollback is clear.")
    require(ready_eval["rollback_control_active"] is False, "Rollback should be clear.")
    require(ready_eval["aws17_durable_enqueue"]["durable_repository"]["prepared"] is True, "AWS-17 repository dry-run should still prepare when rollback is clear.")
    require(ready_eval["aws17_durable_enqueue"]["queue_enqueue"]["prepared"] is True, "AWS-17 queue dry-run should still prepare when rollback is clear.")
    assert_no_live_side_effects(ready_eval, "ready no rollback")

    kill_env = dict(env)
    kill_env.update({
        "AWS_OPTION_A_KILL_SWITCH_ENABLED": "true",
        "AWS_OPTION_A_DURABLE_WRITE_ENABLED": "true",
        "AWS_OPTION_A_QUEUE_SEND_ENABLED": "true",
        "AWS_OPTION_A_ROLLBACK_REASON": rollback_reason(),
    })
    killed = integration.evaluate_acceptance_route_mode(payload, env=kill_env, validation_evidence=validation)
    require(killed["status"] == "aws_option_a_kill_switch_active", "Kill switch must produce kill-switch status.")
    require(killed["route_execution_allowed_before_rollback"] is True, "Test must prove rollback blocks an otherwise ready route.")
    require(killed["route_execution_allowed"] is False, "Kill switch must block AWS route execution.")
    require(killed["rollback_control_active"] is True, "Rollback control must be active.")
    require(killed["kill_switch_active"] is True, "Kill switch marker must be active.")
    require(killed["aws_route_blocked_by_rollback"] is True, "AWS route must be blocked by rollback.")
    require(killed["compatibility_fallback_selected"] is True, "Kill switch must select compatibility fallback.")
    require(killed["selected_runtime_path"] == "existing_compatibility_runtime_path", "Kill switch must force compatibility path.")
    require(killed["short_circuit_route"] is True, "Kill switch must short-circuit before runtime execution.")
    require(killed["aws17_durable_enqueue"]["durable_repository"]["prepared"] is False, "Kill switch must block repository planning.")
    require(killed["aws17_durable_enqueue"]["queue_enqueue"]["prepared"] is False, "Kill switch must block queue planning.")
    require(killed["aws17_durable_enqueue"]["durable_repository"]["reason"] == "aws_route_blocked_by_rollback", "Repository block reason must be rollback.")
    require(killed["aws17_durable_enqueue"]["queue_enqueue"]["reason"] == "aws_route_blocked_by_rollback", "Queue block reason must be rollback.")
    assert_no_live_side_effects(killed, "kill switch")

    admin_response = integration.build_admin_route_mode_response(killed)
    require(admin_response["success"] is False, "Kill-switch admin response must not claim success.")
    require(admin_response["rollback_control_active"] is True, "Admin response must show rollback active.")
    require(admin_response["kill_switch_active"] is True, "Admin response must show kill switch active.")
    require(admin_response["rollback_reason_present"] is True, "Admin response must show reason presence.")
    require("[redacted" in admin_response["rollback_reason_sanitized"], "Rollback reason must be sanitized.")
    require(admin_response["rds_write_attempted"] is False, "Admin response must not write RDS.")
    require(admin_response["sqs_send_attempted"] is False, "Admin response must not send SQS.")
    require("DATABASE_URL" not in str(admin_response), "Rollback admin response must not expose DATABASE_URL marker.")
    assert_no_forbidden_values(admin_response, "kill-switch admin response")

    client_response = integration.build_client_route_mode_response(killed)
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
        "rollback",
        "kill",
    ]:
        require(forbidden_client_marker not in client_text, f"Client rollback view exposed internal marker: {forbidden_client_marker}")
    assert_no_forbidden_values(client_response, "client response")

    forced_env = dict(env)
    forced_env.update({
        "AWS_OPTION_A_FORCE_COMPATIBILITY_FALLBACK": "true",
        "AWS_OPTION_A_DURABLE_WRITE_ENABLED": "true",
        "AWS_OPTION_A_QUEUE_SEND_ENABLED": "true",
        "AWS_OPTION_A_ROLLBACK_REASON": "Owner requested fallback during launch check.",
    })
    forced = integration.evaluate_acceptance_route_mode(payload, env=forced_env, validation_evidence=validation)
    require(forced["status"] == "aws_option_a_compatibility_fallback_forced", "Forced fallback must produce fallback status.")
    require(forced["force_compatibility_fallback"] is True, "Forced fallback marker must be active.")
    require(forced["kill_switch_active"] is False, "Forced fallback should not claim kill switch.")
    require(forced["route_execution_allowed"] is False, "Forced fallback must block AWS route execution.")
    require(forced["selected_runtime_path"] == "existing_compatibility_runtime_path", "Forced fallback must select compatibility path.")
    require(forced["aws17_durable_enqueue"]["durable_repository"]["prepared"] is False, "Forced fallback must block repository planning.")
    require(forced["aws17_durable_enqueue"]["queue_enqueue"]["prepared"] is False, "Forced fallback must block queue planning.")
    assert_no_live_side_effects(forced, "forced compatibility fallback")

    status_killed = integration.evaluate_status_route_mode(
        {"job_id": "job_aws18_rollback", "actor_role": "admin", "package_name": "enterprise", "entitlement_status": "active"},
        env=kill_env,
        validation_evidence=validation,
    )
    require(status_killed["route_kind"] == "status", "Status route must remain status kind.")
    require(status_killed["aws_route_blocked_by_rollback"] is True, "Status route must obey kill switch.")
    require(status_killed["aws17_durable_enqueue"]["status_persistence"]["prepared"] is False, "Status route must not prepare durable read under kill switch.")
    assert_no_live_side_effects(status_killed, "status kill switch")

    direct_control = rollback.build_aws_option_a_rollback_control_decision(
        env={
            "AWS_OPTION_A_KILL_SWITCH_ENABLED": "true",
            "AWS_OPTION_A_ROLLBACK_REASON": rollback_reason(),
        },
        route_kind="acceptance",
        route_intent=True,
        route_execution_allowed=True,
        selected_runtime_path="aws_option_a_durable_acceptance_path",
        route_mode="aws_option_a_enabled_ready",
    )
    require(direct_control["aws_route_blocked_by_rollback"] is True, "Direct rollback helper must block ready route.")
    require(direct_control["route_execution_allowed_after_rollback"] is False, "Direct rollback helper must deny execution after rollback.")
    require(direct_control["client_bypass_allowed"] is False, "Client bypass must never be allowed.")
    assert_no_forbidden_values(direct_control, "direct rollback control")

    require(len(catalogue.CLIENT_FACING_AGENTS) == catalogue.FINAL_APPROVED_VISIBLE_AGENT_COUNT, "Final 27 visible catalogue must remain intact.")
    row_ids = [int(match) for match in re.findall(r"AWS-(\d+)", matrix)]
    require(row_ids and max(row_ids) <= 20, "Migration matrix must remain contained through AWS-20.")
    require("AWS-21" not in matrix, "Migration matrix must not add AWS-21 or later.")
    for marker in [
        "AWS-18",
        "rollback and kill-switch control boundary",
        "aws_option_a_rollback_controls.py",
        "verify_aws_option_a_rollback_controls.py",
        "rollback controls are implemented/tested",
        "AWS-17 through AWS-20",
    ]:
        require(marker in matrix, f"Migration matrix missing AWS-18 marker: {marker}")
    for marker in [
        "AWS_OPTION_A_KILL_SWITCH_ENABLED",
        "AWS_OPTION_A_FORCE_COMPATIBILITY_FALLBACK",
        "AWS_OPTION_A_ROLLBACK_REASON",
        "sanitize_rollback_reason",
        "aws18_rollback_control_boundary",
    ]:
        require(marker in rollback_source + integration_source, f"AWS-18 source missing marker: {marker}")

    print("AWS_OPTION_A_ROLLBACK_CONTROLS_VERIFICATION_PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
