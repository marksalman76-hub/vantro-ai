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


def assert_no_live_behavior(decision: dict) -> None:
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
        require(decision.get(key) is False, f"AWS-15E route boundary must not perform live behavior: {key}")


def main() -> int:
    cutover = load_module(
        "backend/app/runtime/aws_option_a_route_cutover_boundary.py",
        "aws_option_a_route_cutover_boundary_under_test",
    )
    catalogue = load_module(
        "backend/app/runtime/real_agent_component_catalogue.py",
        "real_agent_component_catalogue_for_aws15e_test",
    )
    source = read("backend/app/runtime/aws_option_a_route_cutover_boundary.py")
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
        require(marker not in source, f"AWS-15E route boundary must not contain live SDK/network marker: {marker}")

    payload = {
        "job_id": "job_aws15e_cutover",
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

    default_decision = cutover.decide_api_acceptance_route_cutover(payload, env={}, validation_evidence=ready_validation)
    require(default_decision["route_mode"] == "compatibility_runtime_path", "Default route mode must remain compatibility.")
    require(default_decision["selected_runtime_path"] == "existing_compatibility_runtime_path", "Default selected path must be existing compatibility.")
    require(default_decision["route_execution_allowed"] is False, "Default route must not execute AWS path.")
    assert_no_live_behavior(default_decision)

    enabled_only = cutover.decide_api_acceptance_route_cutover(
        payload,
        env={"AWS_OPTION_A_ENABLED": "true"},
        validation_evidence=ready_validation,
    )
    require(enabled_only["route_mode"] == "aws_option_a_live_ready_but_disabled", "AWS_OPTION_A_ENABLED alone must not activate route cutover.")
    require(enabled_only["route_execution_allowed"] is False, "AWS_OPTION_A_ENABLED alone must not allow AWS execution.")
    require("AWS_OPTION_A_ROUTE_CUTOVER_ENABLED" in enabled_only["missing_gates"], "Route cutover flag gate must be explicit.")
    require("AWS_OPTION_A_ACCEPTANCE_CUTOVER_ENABLED" in enabled_only["missing_gates"], "Acceptance cutover flag gate must be explicit.")
    assert_no_live_behavior(enabled_only)

    missing_validation = cutover.decide_api_acceptance_route_cutover(payload, env=ready_env, validation_evidence={})
    require(missing_validation["route_mode"] == "aws_option_a_enabled_missing_validation", "Missing validation must block live AWS route mode.")
    require(missing_validation["route_execution_allowed"] is False, "Missing validation must prevent route execution.")
    for service in ["iam", "rds", "sqs", "s3", "secrets"]:
        require(f"validation_evidence:{service}" in missing_validation["missing_gates"], f"Missing validation gate not reported: {service}")
    assert_no_live_behavior(missing_validation)

    acceptance_ready = cutover.decide_api_acceptance_route_cutover(payload, env=ready_env, validation_evidence=ready_validation)
    require(acceptance_ready["route_mode"] == "aws_option_a_enabled_ready", "All gates/evidence should allow acceptance readiness.")
    require(acceptance_ready["selected_runtime_path"] == "aws_option_a_durable_acceptance_path", "Acceptance path should select durable acceptance.")
    require(acceptance_ready["route_execution_allowed"] is True, "Acceptance route should be executable only after all gates pass.")
    assert_no_live_behavior(acceptance_ready)

    status_disabled_env = dict(ready_env)
    status_disabled_env["AWS_OPTION_A_STATUS_CUTOVER_ENABLED"] = "false"
    status_disabled = cutover.decide_api_status_route_cutover(payload, env=status_disabled_env, validation_evidence=ready_validation)
    require(status_disabled["route_mode"] == "aws_option_a_live_ready_but_disabled", "Status cutover must be independently gated.")
    require("AWS_OPTION_A_STATUS_CUTOVER_ENABLED" in status_disabled["missing_gates"], "Status cutover flag must be required for status reads.")
    require(status_disabled["route_execution_allowed"] is False, "Disabled status cutover must not execute.")

    acceptance_disabled_env = dict(ready_env)
    acceptance_disabled_env["AWS_OPTION_A_ACCEPTANCE_CUTOVER_ENABLED"] = "false"
    acceptance_disabled = cutover.decide_api_acceptance_route_cutover(payload, env=acceptance_disabled_env, validation_evidence=ready_validation)
    require(acceptance_disabled["route_mode"] == "aws_option_a_live_ready_but_disabled", "Acceptance cutover must be independently gated.")
    require("AWS_OPTION_A_ACCEPTANCE_CUTOVER_ENABLED" in acceptance_disabled["missing_gates"], "Acceptance cutover flag must be required for job acceptance.")
    require(acceptance_disabled["route_execution_allowed"] is False, "Disabled acceptance cutover must not execute.")

    dry_run_payload = dict(payload)
    dry_run_payload["dry_run"] = True
    dry_run_decision = cutover.decide_api_acceptance_route_cutover(
        dry_run_payload,
        env={"AWS_OPTION_A_ENABLED": "true"},
        validation_evidence={},
    )
    require(dry_run_decision["route_mode"] == "aws_option_a_dry_run_path", "Dry-run mode should be explicit and non-live.")
    require(dry_run_decision["selected_runtime_path"] == "aws_option_a_dry_run_planning_path", "Dry-run should select planning path.")
    require(dry_run_decision["route_execution_allowed"] is False, "Dry-run must not execute live AWS route.")
    assert_no_live_behavior(dry_run_decision)

    client_payload = dict(payload)
    client_payload.update({
        "actor_role": "client",
        "package_name": "starter",
        "entitlement_status": "missing",
        "active_agents": [],
    })
    client_blocked = cutover.decide_api_acceptance_route_cutover(client_payload, env=ready_env, validation_evidence=ready_validation)
    require(client_blocked["route_mode"] == "aws_option_a_enabled_ready", "Environment can be route-ready even when client entitlement blocks request.")
    require(client_blocked["route_execution_allowed"] is False, "Client package/credit/approval authority must still block execution.")
    require(client_blocked["request_authority_allowed"] is False, "Client authority denial must be recorded.")
    require("api_acceptance_entitlement_allowed" in client_blocked["missing_gates"], "Authority gate must be explicit.")
    assert_no_live_behavior(client_blocked)

    admin_view = acceptance_ready["admin_view"]
    client_view = acceptance_ready["client_view"]
    require("validation_summary" in admin_view, "Admin view must include safe validation diagnostics.")
    require("safe_config_metadata" in admin_view, "Admin view must include redacted config metadata.")
    require("flags" in admin_view, "Admin view must include cutover flag diagnostics.")
    require("validation_summary" not in client_view, "Client view must hide validation diagnostics.")
    require("safe_config_metadata" not in client_view, "Client view must hide config metadata.")
    require("flags" not in client_view, "Client view must hide flag internals.")

    combined_text = str(acceptance_ready)
    client_text = str(client_view).lower()
    for forbidden_value in [
        "123456789012",
        "DB_SECRET_SHOULD_NOT_LEAK",
        "QUEUE_SHOULD_NOT_LEAK",
        "DLQ_SHOULD_NOT_LEAK",
        "MEDIA_BUCKET_SHOULD_NOT_LEAK",
        "UPLOAD_BUCKET_SHOULD_NOT_LEAK",
        "SECRET_PREFIX_SHOULD_NOT_LEAK",
        "postgres://SHOULD_NOT_LEAK",
    ]:
        require(forbidden_value not in combined_text, f"AWS-15E leaked secret/internal value: {forbidden_value}")
    for forbidden_client_marker in [
        "aws",
        "sqs",
        "bucket",
        "secret",
        "database",
        "queue_url",
        "arn:",
        "table",
        "validation_summary",
        "safe_config_metadata",
    ]:
        require(forbidden_client_marker not in client_text, f"Client view exposed AWS/internal marker: {forbidden_client_marker}")

    final_catalogue = acceptance_ready["final_visible_agent_catalogue"]
    visible = catalogue.list_final_approved_visible_agents()
    enterprise_selectable = catalogue.list_client_selectable_agents("enterprise")
    system_keys = {agent["key"] for agent in catalogue.SYSTEM_AGENTS}
    selectable_keys = {agent["key"] for agent in enterprise_selectable["agents"]}
    require(final_catalogue["actual_visible_count"] == 27, "AWS-15E must preserve final 27 visible catalogue.")
    require(final_catalogue["system_agents_visible_or_selectable"] is False, "AWS-15E must keep system agents internal-only.")
    require(visible["count"] == 27, "Visible catalogue count must remain 27.")
    require(enterprise_selectable["count"] == 27, "Enterprise selectable count must remain 27.")
    require(not system_keys.intersection(selectable_keys), "SYSTEM_AGENTS must not become client selectable.")

    for marker in [
        "AWS_OPTION_A_ROUTE_CUTOVER_ENABLED",
        "AWS_OPTION_A_ACCEPTANCE_CUTOVER_ENABLED",
        "AWS_OPTION_A_STATUS_CUTOVER_ENABLED",
        "compatibility_runtime_path",
        "aws_option_a_dry_run_path",
        "aws_option_a_live_ready_but_disabled",
        "aws_option_a_enabled_missing_validation",
        "aws_option_a_enabled_ready",
        "decide_api_acceptance_route_cutover",
        "decide_api_status_route_cutover",
    ]:
        require(marker in source, f"AWS-15E source missing marker: {marker}")

    row_ids = [int(match) for match in re.findall(r"AWS-(\d+)", matrix)]
    require(row_ids, "Migration matrix must contain AWS rows.")
    require(max(row_ids) <= 20, "Migration matrix must remain contained to AWS-15 through AWS-20.")
    require("AWS-21" not in matrix, "Migration matrix must not contain AWS-21 or later.")
    for marker in [
        "AWS-15",
        "API/status route cutover boundary",
        "verify_aws_option_a_route_cutover_boundary.py",
        "AWS_OPTION_A_ROUTE_CUTOVER_ENABLED",
        "AWS_OPTION_A_ACCEPTANCE_CUTOVER_ENABLED",
        "AWS_OPTION_A_STATUS_CUTOVER_ENABLED",
    ]:
        require(marker in matrix, f"Migration matrix missing AWS-15E marker: {marker}")

    print("AWS_OPTION_A_ROUTE_CUTOVER_BOUNDARY_VERIFICATION_PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
