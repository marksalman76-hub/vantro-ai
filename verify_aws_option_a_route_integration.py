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


def assert_no_live_behavior(result: dict) -> None:
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
        require(result.get(key) is False, f"AWS-16 route integration must not perform live behavior: {key}")


def main() -> int:
    integration = load_module(
        "backend/app/runtime/aws_option_a_route_integration.py",
        "aws_option_a_route_integration_under_test",
    )
    catalogue = load_module(
        "backend/app/runtime/real_agent_component_catalogue.py",
        "real_agent_component_catalogue_for_aws16_test",
    )
    source = read("backend/app/runtime/aws_option_a_route_integration.py")
    main_source = read("backend/app/main.py")
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
        require(marker not in source, f"AWS-16 route integration must not contain live SDK/network marker: {marker}")

    payload = {
        "job_id": "job_aws16_route_integration",
        "actor_role": "admin",
        "requested_by_role": "owner",
        "package_name": "enterprise",
        "entitlement_status": "active",
        "task_type": "media_generation",
        "workflow_type": "universal_complete_media",
        "selected_agent": "creative_director_agent",
        "selected_agents": ["creative_director_agent", "media_producer_agent"],
        "agent_ids": ["creative_director_agent", "media_producer_agent"],
        "active_agents": ["creative_director_agent", "media_producer_agent"],
        "video_provider": "future_video_provider",
        "audio_provider": "future_audio_provider",
        "duration_seconds": 10,
        "approval_status": "admin_unrestricted",
        "credit_reservation_status": "not_required",
        "runway_api_key": "RUNWAY_SECRET_SHOULD_NOT_LEAK",
        "provider_credentials": {"future_provider_api_key": "PROVIDER_SECRET_SHOULD_NOT_LEAK"},
    }
    ready_validation = {
        "status": "completed",
        "service_results": {
            "iam": {"status": "passed", "account": "123456789012"},
            "rds": {"status": "passed", "database_url": "postgres://SHOULD_NOT_LEAK"},
            "sqs": {"status": "passed", "queue_url": "https://sqs.example/QUEUE_SHOULD_NOT_LEAK"},
            "s3": {"status": "passed", "media_bucket": "MEDIA_BUCKET_SHOULD_NOT_LEAK"},
            "secrets": {"status": "passed", "arn": "arn:aws:secretsmanager:ap-southeast-2:123456789012:secret:SHOULD_NOT_LEAK"},
        },
    }
    ready_env = {
        "AWS_OPTION_A_ENABLED": "true",
        "AWS_OPTION_A_ROUTE_CUTOVER_ENABLED": "true",
        "AWS_OPTION_A_ACCEPTANCE_CUTOVER_ENABLED": "true",
        "AWS_OPTION_A_STATUS_CUTOVER_ENABLED": "true",
        "AWS_REGION": "ap-southeast-2",
        "DATABASE_URL": "postgres://DB_SECRET_SHOULD_NOT_LEAK",
        "AWS_RDS_SECRET_ARN": "arn:aws:secretsmanager:ap-southeast-2:123456789012:secret:DB_SHOULD_NOT_LEAK",
        "AWS_MEDIA_QUEUE_URL": "https://sqs.example/QUEUE_SHOULD_NOT_LEAK",
        "AWS_MEDIA_DLQ_URL": "https://sqs.example/DLQ_SHOULD_NOT_LEAK",
        "AWS_MEDIA_S3_BUCKET": "MEDIA_BUCKET_SHOULD_NOT_LEAK",
        "AWS_UPLOADS_S3_BUCKET": "UPLOAD_BUCKET_SHOULD_NOT_LEAK",
        "AWS_PROVIDER_SECRETS_PREFIX": "/provider/SECRET_PREFIX_SHOULD_NOT_LEAK",
    }

    default_eval = integration.evaluate_acceptance_route_mode(payload, env={}, validation_evidence=ready_validation)
    require(default_eval["route_mode"] == "compatibility_runtime_path", "Default route mode must remain compatibility.")
    require(default_eval["short_circuit_route"] is False, "Default route must not short-circuit existing runtime.")
    require(default_eval["default_response_unchanged"] is True, "Default route output must be unchanged.")
    assert_no_live_behavior(default_eval)

    existing_response = {
        "success": True,
        "status": "existing_compatibility_result",
        "job_id": "job_aws16_route_integration",
    }
    unchanged = integration.apply_route_mode_to_response(existing_response, default_eval, audience="admin")
    require(unchanged == existing_response, "Default integration must not change existing route output.")

    enabled_only = integration.evaluate_acceptance_route_mode(
        payload,
        env={"AWS_OPTION_A_ENABLED": "true"},
        validation_evidence=ready_validation,
    )
    require(enabled_only["route_mode"] == "aws_option_a_live_ready_but_disabled", "AWS_OPTION_A_ENABLED alone must not activate route cutover.")
    require(enabled_only["short_circuit_route"] is False, "AWS_OPTION_A_ENABLED alone must not short-circuit route output.")
    require(enabled_only["default_response_unchanged"] is True, "AWS_OPTION_A_ENABLED alone should preserve compatibility response.")
    assert_no_live_behavior(enabled_only)

    missing_validation = integration.evaluate_acceptance_route_mode(payload, env=ready_env, validation_evidence={})
    require(missing_validation["route_mode"] == "aws_option_a_enabled_missing_validation", "Missing validation must block AWS route mode.")
    require(missing_validation["short_circuit_route"] is True, "Explicit AWS route intent with missing evidence must short-circuit safely.")
    blocked_response = integration.build_admin_route_mode_response(missing_validation)
    require(blocked_response["success"] is False, "Missing validation response must not claim success.")
    require(blocked_response["provider_call_attempted"] is False, "Blocked response must not call providers.")
    require(blocked_response["sqs_send_attempted"] is False, "Blocked response must not send SQS.")
    require("validation_evidence:iam" in blocked_response["missing_gates"], "Blocked response must report missing validation evidence.")
    assert_no_live_behavior(missing_validation)

    acceptance_ready = integration.evaluate_acceptance_route_mode(payload, env=ready_env, validation_evidence=ready_validation)
    require(acceptance_ready["route_mode"] == "aws_option_a_enabled_ready", "All gates/evidence should allow AWS acceptance route readiness.")
    require(acceptance_ready["route_execution_allowed"] is True, "All gates/evidence should mark route execution allowed.")
    require(acceptance_ready["short_circuit_route"] is True, "AWS route mode should short-circuit current compatibility execution until live adapter exists.")
    ready_response = integration.build_admin_route_mode_response(acceptance_ready)
    require(ready_response["success"] is True, "Ready route response should report readiness.")
    require(ready_response["rds_write_attempted"] is False, "Ready route response must not write RDS in AWS-16.")
    require(ready_response["sqs_send_attempted"] is False, "Ready route response must not send SQS in AWS-16.")
    assert_no_live_behavior(acceptance_ready)

    status_disabled_env = dict(ready_env)
    status_disabled_env["AWS_OPTION_A_STATUS_CUTOVER_ENABLED"] = "false"
    status_disabled = integration.evaluate_status_route_mode(payload, env=status_disabled_env, validation_evidence=ready_validation)
    require(status_disabled["route_mode"] == "aws_option_a_live_ready_but_disabled", "Status cutover must be independently gated.")
    require(status_disabled["short_circuit_route"] is True, "Explicit status cutover intent with missing status flag must short-circuit safely.")
    require("AWS_OPTION_A_STATUS_CUTOVER_ENABLED" in status_disabled["decision"]["missing_gates"], "Status flag must be reported missing.")

    acceptance_disabled_env = dict(ready_env)
    acceptance_disabled_env["AWS_OPTION_A_ACCEPTANCE_CUTOVER_ENABLED"] = "false"
    acceptance_disabled = integration.evaluate_acceptance_route_mode(payload, env=acceptance_disabled_env, validation_evidence=ready_validation)
    require(acceptance_disabled["route_mode"] == "aws_option_a_live_ready_but_disabled", "Acceptance cutover must be independently gated.")
    require("AWS_OPTION_A_ACCEPTANCE_CUTOVER_ENABLED" in acceptance_disabled["decision"]["missing_gates"], "Acceptance flag must be reported missing.")

    diagnostics_eval = integration.evaluate_acceptance_route_mode(
        {**payload, "include_route_mode_diagnostics": True},
        env={},
        validation_evidence=ready_validation,
        audience="admin",
    )
    with_admin_diagnostics = integration.apply_route_mode_to_response(existing_response, diagnostics_eval, audience="admin")
    require("aws_option_a_route_mode" in with_admin_diagnostics, "Admin diagnostic request must attach route mode diagnostics.")
    require(with_admin_diagnostics["aws_option_a_route_mode"]["route_mode"] == "compatibility_runtime_path", "Admin diagnostics must show compatibility mode by default.")

    client_eval = integration.evaluate_acceptance_route_mode(
        {**payload, "include_route_mode_diagnostics": True},
        env=ready_env,
        validation_evidence=ready_validation,
        audience="client",
    )
    client_response = integration.build_client_route_mode_response(client_eval)
    client_text = str(client_response).lower()
    for forbidden_client_marker in [
        "aws",
        "sqs",
        "bucket",
        "secret",
        "database",
        "queue_url",
        "arn:",
        "table",
        "validation",
        "credential",
    ]:
        require(forbidden_client_marker not in client_text, f"Client route view exposed internal marker: {forbidden_client_marker}")

    combined_text = str(ready_response) + str(with_admin_diagnostics) + str(acceptance_ready)
    for forbidden_value in [
        "123456789012",
        "RUNWAY_SECRET_SHOULD_NOT_LEAK",
        "PROVIDER_SECRET_SHOULD_NOT_LEAK",
        "DB_SECRET_SHOULD_NOT_LEAK",
        "QUEUE_SHOULD_NOT_LEAK",
        "DLQ_SHOULD_NOT_LEAK",
        "MEDIA_BUCKET_SHOULD_NOT_LEAK",
        "UPLOAD_BUCKET_SHOULD_NOT_LEAK",
        "SECRET_PREFIX_SHOULD_NOT_LEAK",
        "postgres://SHOULD_NOT_LEAK",
    ]:
        require(forbidden_value not in combined_text, f"AWS-16 integration leaked secret/internal value: {forbidden_value}")

    client_payload = dict(payload)
    client_payload.update({
        "actor_role": "client",
        "package_name": "starter",
        "entitlement_status": "missing",
        "active_agents": [],
    })
    client_blocked = integration.evaluate_acceptance_route_mode(client_payload, env=ready_env, validation_evidence=ready_validation)
    require(client_blocked["route_mode"] == "aws_option_a_enabled_ready", "Environment can be ready while client authority blocks request.")
    require(client_blocked["route_execution_allowed"] is False, "Client package/credit/approval authority must still block AWS route execution.")
    require("api_acceptance_entitlement_allowed" in client_blocked["decision"]["missing_gates"], "Authority gate must remain enforced.")

    for marker in [
        "evaluate_acceptance_route_mode",
        "evaluate_status_route_mode",
        "build_admin_route_mode_response",
        "build_client_route_mode_response",
        "apply_route_mode_to_response",
        "aws_route_cutover_intent",
        "compatibility_runtime_passthrough",
        "aws_option_a_route_ready_no_live_mutation",
    ]:
        require(marker in source, f"AWS-16 source missing marker: {marker}")

    for marker in [
        "evaluate_acceptance_route_mode",
        "evaluate_status_route_mode",
        "apply_route_mode_to_response",
        "build_route_mode_response",
        "accept_universal_media_pipeline_job(payload, portal=portal)",
        "get_universal_media_pipeline_status(job_id, audience=audience)",
    ]:
        require(marker in main_source, f"backend/app/main.py missing AWS-16 route integration marker: {marker}")

    visible = catalogue.list_final_approved_visible_agents()
    enterprise_selectable = catalogue.list_client_selectable_agents("enterprise")
    system_keys = {agent["key"] for agent in catalogue.SYSTEM_AGENTS}
    selectable_keys = {agent["key"] for agent in enterprise_selectable["agents"]}
    require(visible["count"] == 27, "AWS-16 must preserve final 27 visible catalogue.")
    require(enterprise_selectable["count"] == 27, "AWS-16 must preserve enterprise selectable count.")
    require(not system_keys.intersection(selectable_keys), "SYSTEM_AGENTS must remain internal-only.")

    row_ids = [int(match) for match in re.findall(r"AWS-(\d+)", matrix)]
    require(row_ids, "Migration matrix must contain AWS rows.")
    require(max(row_ids) <= 20, "Migration matrix must remain contained through AWS-20.")
    require("AWS-21" not in matrix, "Migration matrix must not contain AWS-21 or later.")
    for marker in [
        "AWS-16",
        "backend acceptance/status route integration",
        "aws_option_a_route_integration.py",
        "verify_aws_option_a_route_integration.py",
        "AWS-17 through AWS-20",
    ]:
        require(marker in matrix, f"Migration matrix missing AWS-16 marker: {marker}")

    print("AWS_OPTION_A_ROUTE_INTEGRATION_VERIFICATION_PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
