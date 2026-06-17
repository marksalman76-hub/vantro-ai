from __future__ import annotations

from pathlib import Path
import importlib.util
import sys
from typing import Any


ROOT = Path(__file__).resolve().parent


SIDE_EFFECT_KEYS = {
    "live_routes_switched",
    "rds_write_attempted",
    "rds_read_attempted",
    "db_connection_attempted",
    "migration_attempted",
    "sqs_send_attempted",
    "s3_upload_attempted",
    "s3_delete_attempted",
    "secret_fetch_attempted",
    "secrets_manager_value_retrieved",
    "aws_call_attempted",
    "provider_call_attempted",
    "paid_provider_calls_started",
    "stripe_call_attempted",
    "billing_mutation_attempted",
    "credit_mutation_attempted",
    "media_worker_started",
    "worker_started",
    "public_production_cutover_enabled",
}


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
    "123456789012",
    "arn:aws:secretsmanager",
    "postgres://",
    "https://sqs.example",
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


def assert_no_live_side_effects(value: Any, label: str) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if key in SIDE_EFFECT_KEYS:
                require(item is False, f"{label} attempted live side effect: {key}")
            assert_no_live_side_effects(item, label)
    elif isinstance(value, list):
        for item in value:
            assert_no_live_side_effects(item, label)


def client_text_without_safe_boolean_keys(value: Any) -> str:
    safe_boolean_keys = {
        "provider_secret_values_visible",
        "credential_values_exposed",
        "sensitive_values_exposed",
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
    require(value.get("customer_safe") is True, f"{label} must be customer_safe.")
    text = client_text_without_safe_boolean_keys(value)
    for forbidden in [
        "aws",
        "rds",
        "sqs",
        "database",
        "queue_url",
        "bucket",
        "secret",
        "credential",
        "arn:",
        "validation",
        "diagnostic",
        "provider_diagnostics",
        "internal_status",
        "internal_config",
    ]:
        require(forbidden not in text, f"{label} exposed internal marker: {forbidden}")
    assert_no_forbidden_values(value, label)


def ready_validation() -> dict:
    return {
        "status": "completed",
        "service_results": {
            "iam": {"status": "passed", "account": "123456789012"},
            "rds": {"status": "passed", "database_url": "postgres://DATABASE_SECRET_SHOULD_NOT_LEAK"},
            "sqs": {"status": "passed", "queue_url": "https://sqs.example/QUEUE_SECRET_SHOULD_NOT_LEAK"},
            "s3": {"status": "passed", "media_bucket": "MEDIA_BUCKET_SHOULD_NOT_LEAK"},
            "secrets": {
                "status": "passed",
                "arn": "arn:aws:secretsmanager:ap-southeast-2:123456789012:secret:PROVIDER_SECRET_SHOULD_NOT_LEAK",
            },
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


def synthetic_payload() -> dict:
    return {
        "job_id": "synthetic_non_customer_handoff_job",
        "customer_id": "synthetic_non_customer",
        "tenant_id": "synthetic_non_customer_tenant",
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
        "duration_seconds": 10,
        "aspect_ratio": "9:16",
        "selected_agent": "creative_director_agent",
        "selected_agents": ["creative_director_agent", "media_producer_agent"],
        "agent_ids": ["creative_director_agent", "media_producer_agent"],
        "multi_agent_media_execution": True,
        "video_provider": "runway",
        "audio_provider": "elevenlabs",
        "prompt": "Synthetic non-customer route-gated durable handoff proof.",
        "media_prompt": "Synthetic non-customer route-gated durable handoff proof.",
        "approval_status": "admin_unrestricted",
        "credit_reservation_status": "not_required",
        "provider_credentials": {"elevenlabs_api_key": "ELEVEN_SECRET_SHOULD_NOT_LEAK"},
        "internal_config": {"stripe_secret_key": "STRIPE_SECRET_SHOULD_NOT_LEAK"},
        "dry_run": False,
        "preflight_only": False,
        "smoke_test_mode": False,
    }


def main() -> int:
    integration = load_module(
        "backend/app/runtime/aws_option_a_route_integration.py",
        "aws_option_a_route_integration_handoff_under_test",
    )
    status_adapter = load_module(
        "backend/app/runtime/durable_media_job_status_adapter.py",
        "durable_media_job_status_adapter_handoff_under_test",
    )

    route_source = read("backend/app/runtime/aws_option_a_route_integration.py")
    matrix = read("AWS_OPTION_A_MEDIA_MIGRATION_MATRIX.md")
    master_plan = read("PRODUCTION_COMPLETION_MASTER_PLAN.md")

    for forbidden_source_marker in [
        "boto3.",
        "psycopg.connect",
        "requests.",
        "httpx.",
        "stripe.",
        "trigger_next_creative_media_job",
        "trigger_all_creative_media_jobs",
        "start_worker",
        "run_worker",
    ]:
        require(
            forbidden_source_marker not in route_source,
            f"Route-gated handoff boundary must not contain live/worker marker: {forbidden_source_marker}",
        )

    payload = synthetic_payload()
    validation = ready_validation()
    env = ready_env()

    default_eval = integration.evaluate_acceptance_route_mode(payload, env={}, validation_evidence=validation)
    require(default_eval["route_mode"] == "compatibility_runtime_path", "Default route must stay on compatibility path.")
    require(default_eval["route_execution_allowed"] is False, "Default route must not allow durable handoff.")
    default_boundary = default_eval["aws17_durable_enqueue"]
    require(default_boundary["durable_repository"]["prepared"] is False, "Default route must not prepare durable record.")
    require(default_boundary["queue_enqueue"]["prepared"] is False, "Default route must not prepare queue packet.")
    assert_no_live_side_effects(default_eval, "default route")

    missing_validation = integration.evaluate_acceptance_route_mode(payload, env=env, validation_evidence={})
    require(missing_validation["route_execution_allowed"] is False, "Missing validation must block durable handoff.")
    require(missing_validation["aws17_durable_enqueue"]["durable_repository"]["prepared"] is False, "Missing validation must not prepare repository.")
    require(missing_validation["aws17_durable_enqueue"]["queue_enqueue"]["prepared"] is False, "Missing validation must not prepare queue.")
    assert_no_live_side_effects(missing_validation, "missing validation route")

    ready_eval = integration.evaluate_acceptance_route_mode(payload, env=env, validation_evidence=validation)
    require(ready_eval["route_mode"] == "aws_option_a_enabled_ready", "All explicit gates must mark route ready.")
    require(ready_eval["route_execution_allowed"] is True, "Explicit route gates must allow the dry-run handoff boundary.")
    require(ready_eval["short_circuit_route"] is True, "Route-gated handoff should short-circuit compatibility execution.")
    ready_boundary = ready_eval["aws17_durable_enqueue"]
    repository_plan = ready_boundary["durable_repository"]
    queue_plan = ready_boundary["queue_enqueue"]
    require(repository_plan["status"] == "durable_repository_dry_run_prepared", "Repository proof must be prepared in dry-run mode.")
    require(repository_plan["record_shape"]["job_id"] == payload["job_id"], "Durable proof record must preserve synthetic job id.")
    require(repository_plan["record_shape"]["status"] == "accepted", "Durable proof record must use accepted status.")
    require(repository_plan["record_shape"]["customer_safe"] is True, "Durable proof record must be customer_safe.")
    require(repository_plan["durable_job_record"]["customer_id"] == "synthetic_non_customer", "Durable record must remain synthetic.")
    require(repository_plan["repository_operations"], "Repository proof must include rollback-safe placeholder operations.")
    for operation in repository_plan["repository_operations"]:
        require(operation["mutation_mode"] == "no_db_write_placeholder", "Repository operation must be rollback-safe/no-write.")
        require(operation["rds_write_attempted"] is False, "Repository proof operation must not write RDS.")
        require(operation["db_connection_attempted"] is False, "Repository proof operation must not connect to DB.")

    require(queue_plan["status"] == "queue_enqueue_dry_run_prepared", "Queue proof must be prepared in dry-run mode.")
    require(queue_plan["queue_message_validation"]["valid"] is True, "Queue packet must validate.")
    require(queue_plan["queue_packet"]["job_id"] == payload["job_id"], "Queue packet must preserve synthetic job id.")
    require(queue_plan["queue_packet"]["customer_safe"] is True, "Queue packet must be customer_safe.")
    require(queue_plan["queue_packet"]["paid_provider_calls_started"] is False, "Queue packet must not start providers.")
    assert_no_live_side_effects(ready_eval, "ready route")

    future_send_env = dict(env)
    future_send_env["AWS_OPTION_A_DURABLE_WRITE_ENABLED"] = "true"
    future_send_env["AWS_OPTION_A_QUEUE_SEND_ENABLED"] = "true"
    future_eval = integration.evaluate_acceptance_route_mode(payload, env=future_send_env, validation_evidence=validation)
    future_boundary = future_eval["aws17_durable_enqueue"]
    require(
        future_boundary["durable_repository"]["status"] == "durable_repository_write_flag_enabled_but_adapter_not_invoked",
        "Durable write flag must not invoke a live adapter in this proof.",
    )
    require(
        future_boundary["queue_enqueue"]["status"] == "queue_send_flag_enabled_but_adapter_not_invoked",
        "Queue send flag must not invoke a live adapter in this proof.",
    )
    assert_no_live_side_effects(future_eval, "future write/send flags")

    status_eval = integration.evaluate_status_route_mode(
        {"job_id": payload["job_id"], "actor_role": "admin", "package_name": "enterprise", "entitlement_status": "active"},
        env=env,
        validation_evidence=validation,
    )
    require(status_eval["route_kind"] == "status", "Status readback must use status route kind.")
    require(status_eval["route_execution_allowed"] is True, "Status route should be ready behind explicit gates.")
    status_plan = status_eval["aws17_durable_enqueue"]["status_persistence"]
    require(status_plan["status"] == "durable_status_read_dry_run_prepared", "Status readback must be prepared as dry-run.")
    require(status_plan["would_read_durable_status"] is True, "Status readback must prove durable read intent.")
    require(status_plan["job_id"] == payload["job_id"], "Status readback must use synthetic job id.")
    assert_no_live_side_effects(status_eval, "status route")

    durable_record = repository_plan["durable_job_record"]
    admin_status_view = status_adapter.build_admin_media_job_status_view(durable_record)
    client_status_view = status_adapter.build_client_media_job_status_view(durable_record)
    require(admin_status_view["internal_status"] == "accepted", "Admin status view must expose accepted internal status.")
    require(client_status_view["status"] == "queued", "Client-safe status view must map accepted work to queued.")
    assert_client_safe(client_status_view, "client durable status view")
    assert_no_forbidden_values(admin_status_view, "admin durable status view")

    admin_response = integration.build_admin_route_mode_response(ready_eval)
    require("durable_repository" in admin_response, "Admin route response must include durable repository diagnostics.")
    require("queue_enqueue" in admin_response, "Admin route response must include queue diagnostics.")
    require("admin_route_diagnostics" in admin_response, "Admin route response must include actionable diagnostics.")
    require("incident_event" in admin_response, "Admin route response must include incident evidence.")
    require(admin_response["admin_route_diagnostics"]["validation_ready"] is True, "Admin diagnostics must show validation readiness.")
    assert_no_forbidden_values(admin_response, "admin route response")
    assert_no_live_side_effects(admin_response, "admin route response")

    client_route_response = integration.build_client_route_mode_response(ready_eval)
    assert_client_safe(client_route_response, "client route response")

    rollback_env = dict(env)
    rollback_env["AWS_OPTION_A_KILL_SWITCH_ENABLED"] = "true"
    rollback_eval = integration.evaluate_acceptance_route_mode(payload, env=rollback_env, validation_evidence=validation)
    require(rollback_eval["aws_route_blocked_by_rollback"] is True, "Rollback kill switch must block route execution.")
    require(rollback_eval["route_execution_allowed"] is False, "Rollback must prevent durable route execution.")
    rollback_boundary = rollback_eval["aws17_durable_enqueue"]
    require(rollback_boundary["durable_repository"]["prepared"] is False, "Rollback must block durable repository preparation.")
    require(rollback_boundary["queue_enqueue"]["prepared"] is False, "Rollback must block queue preparation.")
    assert_no_live_side_effects(rollback_eval, "rollback route")
    rollback_client = integration.build_client_route_mode_response(rollback_eval)
    assert_client_safe(rollback_client, "rollback client response")

    for marker in [
        "route-gated synthetic durable job handoff",
        "durable_repository_dry_run_prepared",
        "queue_enqueue_dry_run_prepared",
        "durable_status_read_dry_run_prepared",
    ]:
        require(marker in master_plan or marker in matrix, f"Production docs missing route handoff marker: {marker}")

    print("ROUTE_GATED_DURABLE_JOB_HANDOFF_VERIFICATION_PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
