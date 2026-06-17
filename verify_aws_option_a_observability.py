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
        "Incident observability rollback: DATABASE_URL=postgres://DATABASE_SECRET_SHOULD_NOT_LEAK "
        "runway_api_key=RUNWAY_SECRET_SHOULD_NOT_LEAK "
        "stripe_secret_key=STRIPE_SECRET_SHOULD_NOT_LEAK "
        "RDS_PASSWORD=RDS_PASSWORD_SHOULD_NOT_LEAK "
        "queue_url=https://sqs.example/QUEUE_SECRET_SHOULD_NOT_LEAK "
        "arn:aws:secretsmanager:ap-southeast-2:123456789012:secret:PROVIDER_SECRET_SHOULD_NOT_LEAK"
    )


def media_payload() -> dict:
    return {
        "job_id": "job_aws19_observability",
        "customer_id": "customer_aws19",
        "tenant_id": "tenant_aws19",
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
        "aws_option_a_route_integration_aws19_under_test",
    )
    observability = load_module(
        "backend/app/runtime/aws_option_a_observability.py",
        "aws_option_a_observability_under_test",
    )
    catalogue = load_module(
        "backend/app/runtime/real_agent_component_catalogue.py",
        "real_agent_component_catalogue_aws19_under_test",
    )
    integration_source = read("backend/app/runtime/aws_option_a_route_integration.py")
    observability_source = read("backend/app/runtime/aws_option_a_observability.py")
    matrix = read("AWS_OPTION_A_MEDIA_MIGRATION_MATRIX.md")

    for source_name, source in {
        "route integration": integration_source,
        "observability": observability_source,
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
            require(marker not in source, f"AWS-19 {source_name} must not contain live SDK/network marker: {marker}")

    payload = media_payload()
    validation = ready_validation()
    env = ready_env()

    default_eval = integration.evaluate_acceptance_route_mode(payload, env={}, validation_evidence=validation)
    existing_response = {"success": True, "status": "existing_compatibility_result", "job_id": "job_aws19_observability"}
    unchanged = integration.apply_route_mode_to_response(existing_response, default_eval, audience="admin")
    require(unchanged == existing_response, "AWS flags off must keep default compatibility response unchanged.")
    require(default_eval["route_mode"] == "compatibility_runtime_path", "Default route mode must remain compatibility.")
    require(default_eval["aws19_observability"]["admin_diagnostic_snapshot"]["compatibility_default_active"] is True, "Default observability must report compatibility default.")
    require(default_eval["aws19_observability"]["observability_alters_route_decision"] is False, "Observability must not alter decisions.")
    assert_no_live_side_effects(default_eval, "default compatibility")

    ready_eval = integration.evaluate_acceptance_route_mode(payload, env=env, validation_evidence=validation)
    require(ready_eval["route_execution_allowed"] is True, "Ready route should remain allowed.")
    require(ready_eval["aws17_durable_enqueue"]["durable_repository"]["prepared"] is True, "Repository dry-run should prepare when route ready.")
    require(ready_eval["aws17_durable_enqueue"]["queue_enqueue"]["prepared"] is True, "Queue dry-run should prepare when route ready.")
    ready_snapshot = ready_eval["aws19_observability"]["admin_diagnostic_snapshot"]
    require(ready_snapshot["diagnostic_version"] == "aws_option_a_observability_v1", "Admin snapshot must include diagnostic version.")
    require(ready_snapshot["route_mode"] == "aws_option_a_enabled_ready", "Admin snapshot must show route mode.")
    require(ready_snapshot["aws_route_intent_detected"] is True, "Admin snapshot must show route intent.")
    require(ready_snapshot["aws_validation_evidence_present"] is True, "Admin snapshot must show validation evidence present.")
    require(ready_snapshot["aws_route_validation_passed"] is True, "Admin snapshot must show validation passed.")
    require(ready_snapshot["durable_write_flag_enabled"] is False, "Default durable write flag must be disabled.")
    require(ready_snapshot["queue_send_flag_enabled"] is False, "Default queue send flag must be disabled.")
    require(ready_snapshot["durable_dry_run_prepared"] is True, "Admin snapshot must show durable dry-run prepared.")
    require(ready_snapshot["queue_dry_run_prepared"] is True, "Admin snapshot must show queue dry-run prepared.")
    require(ready_snapshot["incident_hint"] == "aws_route_ready_dry_run", "Ready route should get dry-run incident hint.")
    require(ready_snapshot["job_id_present"] is True, "Admin snapshot must show job id presence.")
    require(ready_snapshot["safe_job_reference_hash"], "Admin snapshot must include hashed job reference.")
    require(ready_snapshot["media_type"] == "complete_video", "Admin snapshot must include media_type.")
    require(ready_snapshot["asset_type"] == "video", "Admin snapshot must include asset_type.")
    require(ready_snapshot["agent_id_present"] is True, "Admin snapshot must show agent id presence.")
    require(ready_snapshot["customer_safe"] is True, "Admin snapshot must be customer safe.")
    ready_event = ready_eval["aws19_observability"]["incident_event"]
    require(ready_event["event_type"] == "aws_option_a_route_observability_snapshot_prepared", "Incident event type must be stable.")
    require(ready_event["severity"] == "info", "Ready route event should be info.")
    require(ready_event["external_logging_attempted"] is False, "AWS-19 must not emit external logs.")
    assert_no_live_side_effects(ready_eval, "ready observability")
    assert_no_forbidden_values(integration.build_admin_route_mode_response(ready_eval), "ready admin response")

    future_env = dict(env)
    future_env.update({
        "AWS_OPTION_A_DURABLE_WRITE_ENABLED": "true",
        "AWS_OPTION_A_QUEUE_SEND_ENABLED": "true",
    })
    future_eval = integration.evaluate_acceptance_route_mode(payload, env=future_env, validation_evidence=validation)
    future_snapshot = future_eval["aws19_observability"]["admin_diagnostic_snapshot"]
    require(future_snapshot["durable_write_flag_enabled"] is True, "Admin snapshot must show durable write flag enabled.")
    require(future_snapshot["queue_send_flag_enabled"] is True, "Admin snapshot must show queue send flag enabled.")
    require(future_snapshot["durable_write_would_execute"] is True, "Admin snapshot must surface future durable-write risk.")
    require(future_snapshot["queue_send_would_execute"] is True, "Admin snapshot must surface future queue-send risk.")
    require(future_eval["rds_write_attempted"] is False, "Future flags must not write RDS in AWS-19.")
    require(future_eval["sqs_send_attempted"] is False, "Future flags must not send SQS in AWS-19.")
    assert_no_forbidden_values(future_eval["aws19_observability"], "future flag observability")

    kill_env = dict(future_env)
    kill_env.update({
        "AWS_OPTION_A_KILL_SWITCH_ENABLED": "true",
        "AWS_OPTION_A_ROLLBACK_REASON": rollback_reason(),
    })
    killed = integration.evaluate_acceptance_route_mode(payload, env=kill_env, validation_evidence=validation)
    require(killed["route_execution_allowed_before_rollback"] is True, "Rollback case must be ready before rollback.")
    require(killed["route_execution_allowed"] is False, "Rollback must block route execution.")
    require(killed["aws_route_blocked_by_rollback"] is True, "Rollback must block AWS route.")
    require(killed["aws17_durable_enqueue"]["durable_repository"]["prepared"] is False, "Rollback must block durable planning.")
    require(killed["aws17_durable_enqueue"]["queue_enqueue"]["prepared"] is False, "Rollback must block queue planning.")
    killed_snapshot = killed["aws19_observability"]["admin_diagnostic_snapshot"]
    require(killed_snapshot["rollback_control_active"] is True, "Admin snapshot must show rollback active.")
    require(killed_snapshot["kill_switch_active"] is True, "Admin snapshot must show kill switch active.")
    require(killed_snapshot["aws_route_blocked_by_rollback"] is True, "Admin snapshot must show rollback block.")
    require(killed_snapshot["compatibility_fallback_selected"] is True, "Admin snapshot must show fallback selected.")
    require(killed_snapshot["incident_hint"] == "rollback_kill_switch_active", "Kill switch should have rollback incident hint.")
    require(killed["aws19_observability"]["incident_event"]["severity"] == "warning", "Rollback event should be warning.")
    assert_no_live_side_effects(killed, "kill-switch observability")
    assert_no_forbidden_values(integration.build_admin_route_mode_response(killed), "rollback admin response")

    forced_env = dict(env)
    forced_env.update({"AWS_OPTION_A_FORCE_COMPATIBILITY_FALLBACK": "true"})
    forced = integration.evaluate_acceptance_route_mode(payload, env=forced_env, validation_evidence=validation)
    forced_snapshot = forced["aws19_observability"]["admin_diagnostic_snapshot"]
    require(forced_snapshot["force_compatibility_fallback"] is True, "Admin snapshot must show forced compatibility fallback.")
    require(forced_snapshot["incident_hint"] == "force_compatibility_fallback", "Forced fallback should have incident hint.")
    require(forced["aws17_durable_enqueue"]["queue_enqueue"]["prepared"] is False, "Forced fallback must block queue planning.")

    status_eval = integration.evaluate_status_route_mode(
        {"job_id": "job_aws19_observability", "actor_role": "admin", "package_name": "enterprise", "entitlement_status": "active"},
        env=env,
        validation_evidence=validation,
    )
    status_snapshot = status_eval["aws19_observability"]["admin_diagnostic_snapshot"]
    require(status_snapshot["status_read_source_planned"] == "durable_status_read_dry_run_prepared", "Status route must report status read dry-run.")
    require(status_snapshot["incident_hint"] == "status_read_dry_run", "Status route should get status-read incident hint.")
    require(status_eval["rds_write_attempted"] is False, "Status observability must not write RDS.")

    client_eval = integration.evaluate_acceptance_route_mode(
        {**payload, "include_route_mode_diagnostics": True},
        env=kill_env,
        validation_evidence=validation,
        audience="client",
    )
    client_response = integration.build_client_route_mode_response(client_eval)
    client_diagnostics = integration.build_client_route_diagnostics(client_eval)
    for label, value in {"client response": client_response, "client diagnostics": client_diagnostics}.items():
        text = str(value).lower()
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
            "route gate",
        ]:
            require(forbidden_client_marker not in text, f"{label} exposed internal marker: {forbidden_client_marker}")
        assert_no_forbidden_values(value, label)

    direct_bundle = observability.build_aws_option_a_observability_bundle(payload=payload, evaluation=ready_eval)
    require(direct_bundle["observability_alters_route_decision"] is False, "Direct observability must be non-mutating.")
    require(direct_bundle["cloudwatch_put_attempted"] is False, "Direct observability must not call CloudWatch.")
    require(direct_bundle["rds_write_attempted"] is False, "Direct observability must not write RDS.")
    require(direct_bundle["sqs_send_attempted"] is False, "Direct observability must not send SQS.")
    require(direct_bundle["secret_fetch_attempted"] is False, "Direct observability must not fetch secrets.")
    assert_no_forbidden_values(direct_bundle, "direct observability bundle")

    require(len(catalogue.CLIENT_FACING_AGENTS) == catalogue.FINAL_APPROVED_VISIBLE_AGENT_COUNT, "Final 27 visible catalogue must remain intact.")
    row_ids = [int(match) for match in re.findall(r"AWS-(\d+)", matrix)]
    require(row_ids and max(row_ids) <= 20, "Migration matrix must remain contained through AWS-20.")
    require("AWS-21" not in matrix, "Migration matrix must not add AWS-21 or later.")
    for marker in [
        "AWS-19",
        "observability and incident diagnostics boundary",
        "aws_option_a_observability.py",
        "verify_aws_option_a_observability.py",
        "AWS-19 observability is implemented/tested",
        "AWS-17 through AWS-20",
    ]:
        require(marker in matrix, f"Migration matrix missing AWS-19 marker: {marker}")
    for marker in [
        "DIAGNOSTIC_VERSION",
        "build_admin_diagnostic_snapshot",
        "build_client_diagnostic_snapshot",
        "build_incident_event",
        "build_aws_option_a_observability_bundle",
        "aws19_observability_boundary",
    ]:
        require(marker in observability_source + integration_source, f"AWS-19 source missing marker: {marker}")

    print("AWS_OPTION_A_OBSERVABILITY_VERIFICATION_PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
