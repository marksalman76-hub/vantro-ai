from __future__ import annotations

from pathlib import Path
import importlib.util
import json
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
    "media_generation_attempted",
    "stripe_call_attempted",
    "billing_mutation_attempted",
    "credit_mutation_attempted",
    "media_worker_started",
    "worker_started",
    "customer_traffic_attempted",
    "public_cutover_enabled",
    "public_production_cutover_enabled",
    "render_removal_attempted",
    "aws21_or_later_work_attempted",
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
    "DURABLE_ASSET_BUCKET_SHOULD_NOT_LEAK",
    "PROVIDER_SECRET_SHOULD_NOT_LEAK",
    "SIGNED_URL_SECRET_SHOULD_NOT_LEAK",
    "123456789012",
    "arn:aws:secretsmanager",
    "postgres://",
    "https://sqs.example",
    "X-Amz-Signature",
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


def assert_no_side_effects(value: Any, label: str) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if key in SIDE_EFFECT_KEYS:
                require(item is False, f"{label} attempted side effect: {key}")
            assert_no_side_effects(item, label)
    elif isinstance(value, list):
        for item in value:
            assert_no_side_effects(item, label)


def client_text_without_safe_boolean_keys(value: Any) -> str:
    safe_boolean_keys = {
        "provider_secret_values_visible",
        "credential_values_exposed",
        "sensitive_values_exposed",
        "internal_config_exposed",
        "signed_url_exposed",
        "raw_storage_identifiers_exposed",
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
        "signed_url",
        "object_key",
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
        "AWS_DURABLE_ASSET_S3_BUCKET": "DURABLE_ASSET_BUCKET_SHOULD_NOT_LEAK",
        "AWS_PROVIDER_SECRETS_PREFIX": "/provider/PROVIDER_SECRET_SHOULD_NOT_LEAK",
    }


def synthetic_payload() -> dict:
    return {
        "job_id": "synthetic_route_cutover_readiness_job",
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
        "prompt": "Synthetic non-customer production route cutover readiness proof.",
        "media_prompt": "Synthetic non-customer production route cutover readiness proof.",
        "approval_status": "admin_unrestricted",
        "credit_reservation_status": "not_required",
        "provider_credentials": {"elevenlabs_api_key": "ELEVEN_SECRET_SHOULD_NOT_LEAK"},
        "internal_config": {"stripe_secret_key": "STRIPE_SECRET_SHOULD_NOT_LEAK"},
        "dry_run": False,
        "preflight_only": False,
        "smoke_test_mode": False,
    }


class FakeBody:
    def __init__(self, body: bytes):
        self.body = body

    def read(self) -> bytes:
        return self.body


class FakeS3Client:
    def __init__(self):
        self.objects: dict[tuple[str, str], dict[str, Any]] = {}
        self.put_count = 0
        self.get_count = 0
        self.delete_count = 0

    def put_object(self, **kwargs: Any) -> dict:
        bucket = kwargs.get("Bucket")
        key = kwargs.get("Key")
        body = kwargs.get("Body") or b""
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.objects[(bucket, key)] = {
            "Body": body,
            "ContentType": kwargs.get("ContentType"),
            "Metadata": kwargs.get("Metadata") or {},
        }
        self.put_count += 1
        return {"ETag": "fake-etag"}

    def get_object(self, **kwargs: Any) -> dict:
        bucket = kwargs.get("Bucket")
        key = kwargs.get("Key")
        if (bucket, key) not in self.objects:
            raise KeyError("NoSuchKey")
        self.get_count += 1
        return {"Body": FakeBody(self.objects[(bucket, key)]["Body"])}

    def delete_object(self, **kwargs: Any) -> dict:
        bucket = kwargs.get("Bucket")
        key = kwargs.get("Key")
        self.objects.pop((bucket, key), None)
        self.delete_count += 1
        return {}

    def head_object(self, **kwargs: Any) -> dict:
        bucket = kwargs.get("Bucket")
        key = kwargs.get("Key")
        if (bucket, key) not in self.objects:
            raise KeyError("NoSuchKey")
        return {"ContentLength": len(self.objects[(bucket, key)]["Body"])}

    def generate_presigned_url(self, *_args: Any, **_kwargs: Any) -> str:
        return "https://signed.example.invalid/download?X-Amz-Signature=SIGNED_URL_SECRET_SHOULD_NOT_LEAK"


def build_injected_asset_result(asset_helper, env: dict, job_id: str) -> dict:
    asset_id = "synthetic_route_cutover_readiness_asset"
    fake_s3 = FakeS3Client()
    live_result = asset_helper.run_s3_durable_asset_delivery_proof(
        env=env,
        job_id=job_id,
        asset_id=asset_id,
        s3_client=fake_s3,
    )
    require(live_result["durable_asset_proof_passed"] is True, "Injected asset metadata proof must pass.")
    require(live_result["asset_job_link_passed"] is True, "Injected asset proof must link asset to job hash.")
    require(live_result["asset_metadata_readback_passed"] is True, "Injected asset metadata readback must pass.")
    require(live_result["asset_open_or_download_proof_passed"] is True, "Injected asset open/download proof must pass.")
    require(live_result["signed_url_exposed"] is False, "Injected proof must not expose signed URL.")
    require(fake_s3.put_count == 2, "Injected asset proof must store asset and metadata fixtures.")
    require(fake_s3.get_count == 2, "Injected asset proof must read asset and metadata fixtures.")
    require(fake_s3.delete_count == 2, "Injected asset proof must clean up fixtures.")
    client_view = asset_helper.build_client_safe_asset_view(live_result, job_id, asset_id)
    admin_view = asset_helper.build_admin_asset_diagnostics(
        job_id=job_id,
        asset_id=asset_id,
        block="",
        flags={},
        live_result=live_result,
        forbidden_flags=[],
    )
    assert_client_safe(client_view, "asset client view")
    assert_no_forbidden_values(admin_view, "asset admin diagnostics")
    return {
        "live_result": live_result,
        "client_view": client_view,
        "admin_view": admin_view,
    }


def build_route_cutover_readiness_proof() -> dict:
    integration = load_module(
        "backend/app/runtime/aws_option_a_route_integration.py",
        "aws_option_a_route_integration_cutover_readiness_under_test",
    )
    asset_helper = load_module(
        "backend/app/runtime/aws_synthetic_durable_asset_delivery.py",
        "aws_synthetic_durable_asset_delivery_cutover_readiness_under_test",
    )

    payload = synthetic_payload()
    validation = ready_validation()
    env = ready_env()

    default_eval = integration.evaluate_acceptance_route_mode(payload, env={}, validation_evidence=validation)
    require(default_eval["route_mode"] == "compatibility_runtime_path", "Default route must remain compatibility.")
    require(default_eval["route_execution_allowed"] is False, "Default route must not execute AWS route.")
    assert_no_side_effects(default_eval, "default route")

    ready_eval = integration.evaluate_acceptance_route_mode(payload, env=env, validation_evidence=validation)
    ready_boundary = ready_eval["aws17_durable_enqueue"]
    repository_plan = ready_boundary["durable_repository"]
    queue_plan = ready_boundary["queue_enqueue"]
    require(ready_eval["route_mode"] == "aws_option_a_enabled_ready", "Route must become ready only with explicit gates.")
    require(ready_eval["selected_runtime_path"] == "aws_option_a_durable_acceptance_path", "Ready route must select durable acceptance path.")
    require(ready_eval["route_execution_allowed"] is True, "Ready synthetic route must allow the AWS durable path.")
    require(repository_plan["status"] == "durable_repository_dry_run_prepared", "Repository plan must be dry-run prepared.")
    require(queue_plan["status"] == "queue_enqueue_dry_run_prepared", "Queue plan must be dry-run prepared.")
    require(queue_plan["queue_message_validation"]["valid"] is True, "Queue packet must validate.")
    require(queue_plan["queue_packet"]["job_id"] == payload["job_id"], "Queue packet must preserve synthetic job ID.")
    require(queue_plan["queue_packet"]["paid_provider_calls_started"] is False, "Queue packet must not start providers.")
    assert_no_side_effects(ready_eval, "ready route")

    status_eval = integration.evaluate_status_route_mode(
        {
            "job_id": payload["job_id"],
            "actor_role": "admin",
            "requested_by_role": "owner",
            "role": "owner",
            "package_name": "enterprise",
            "entitlement_status": "active",
        },
        env=env,
        validation_evidence=validation,
    )
    status_plan = status_eval["aws17_durable_enqueue"]["status_persistence"]
    require(status_eval["route_execution_allowed"] is True, "Synthetic status route must be ready.")
    require(status_plan["status"] == "durable_status_read_dry_run_prepared", "Status readback must be dry-run prepared.")
    require(status_plan["would_read_durable_status"] is True, "Status proof must represent durable readback.")
    require(status_plan["job_id"] == payload["job_id"], "Status readback must use synthetic job ID.")
    assert_no_side_effects(status_eval, "status route")

    rollback_env = dict(env)
    rollback_env["AWS_OPTION_A_KILL_SWITCH_ENABLED"] = "true"
    rollback_eval = integration.evaluate_acceptance_route_mode(payload, env=rollback_env, validation_evidence=validation)
    require(rollback_eval["route_execution_allowed_before_rollback"] is True, "Rollback test must start from otherwise-ready route.")
    require(rollback_eval["aws_route_blocked_by_rollback"] is True, "Kill switch must block route execution.")
    require(rollback_eval["compatibility_fallback_selected"] is True, "Kill switch must select compatibility fallback.")
    require(rollback_eval["selected_runtime_path"] == "existing_compatibility_runtime_path", "Kill switch must force compatibility path.")
    assert_no_side_effects(rollback_eval, "rollback route")

    admin_response = integration.build_admin_route_mode_response(ready_eval)
    client_response = integration.build_client_route_mode_response(ready_eval)
    rollback_client_response = integration.build_client_route_mode_response(rollback_eval)
    assert_no_forbidden_values(admin_response, "admin route response")
    assert_no_side_effects(admin_response, "admin route response")
    assert_client_safe(client_response, "client route response")
    assert_client_safe(rollback_client_response, "rollback client route response")

    asset_result = build_injected_asset_result(asset_helper, env, payload["job_id"])

    proof = {
        "route_cutover_readiness_attempted": True,
        "route_cutover_readiness_passed": True,
        "public_cutover_default_disabled": default_eval["route_execution_allowed"] is False,
        "owner_flags_required": default_eval["route_execution_allowed"] is False and ready_eval["route_execution_allowed"] is True,
        "rollback_kill_switch_blocked_execution": rollback_eval["aws_route_blocked_by_rollback"] is True,
        "compatibility_fallback_available": rollback_eval["compatibility_fallback_selected"] is True,
        "synthetic_route_reached_aws_durable_path": ready_eval["selected_runtime_path"] == "aws_option_a_durable_acceptance_path",
        "synthetic_status_readback_passed": status_plan["status"] == "durable_status_read_dry_run_prepared",
        "synthetic_asset_result_metadata_passed": asset_result["live_result"]["asset_metadata_readback_passed"] is True,
        "client_safe_view_redacted": True,
        "admin_diagnostics_redacted": True,
        "provider_call_attempted": False,
        "media_generation_attempted": False,
        "stripe_call_attempted": False,
        "billing_mutation_attempted": False,
        "credit_mutation_attempted": False,
        "customer_traffic_attempted": False,
        "public_cutover_enabled": False,
        "render_removal_attempted": False,
        "aws21_or_later_work_attempted": False,
        "route_mode": ready_eval["route_mode"],
        "acceptance_runtime_path": ready_eval["selected_runtime_path"],
        "status_runtime_path": status_eval["selected_runtime_path"],
        "durable_repository_status": repository_plan["status"],
        "queue_enqueue_status": queue_plan["status"],
        "status_readback_status": status_plan["status"],
        "synthetic_job_reference_hash": asset_result["live_result"]["synthetic_job_reference_hash"],
        "synthetic_asset_reference_hash": asset_result["live_result"]["synthetic_asset_reference_hash"],
        "object_key_hash_prefix": asset_result["live_result"]["object_key_hash_prefix"],
        "metadata_object_key_hash_prefix": asset_result["live_result"]["metadata_object_key_hash_prefix"],
    }
    assert_no_forbidden_values(proof, "route cutover readiness proof")
    return proof


def main() -> int:
    source_files = {
        "route integration": read("backend/app/runtime/aws_option_a_route_integration.py"),
        "rollback controls": read("backend/app/runtime/aws_option_a_rollback_controls.py"),
        "observability": read("backend/app/runtime/aws_option_a_observability.py"),
        "durable asset": read("backend/app/runtime/aws_synthetic_durable_asset_delivery.py"),
    }
    for source_name, source in source_files.items():
        for forbidden_source_marker in [
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
                f"{source_name} must not contain forbidden route-readiness marker: {forbidden_source_marker}",
            )

    proof = build_route_cutover_readiness_proof()
    for field in [
        "route_cutover_readiness_attempted",
        "route_cutover_readiness_passed",
        "public_cutover_default_disabled",
        "owner_flags_required",
        "rollback_kill_switch_blocked_execution",
        "compatibility_fallback_available",
        "synthetic_route_reached_aws_durable_path",
        "synthetic_status_readback_passed",
        "synthetic_asset_result_metadata_passed",
        "client_safe_view_redacted",
        "admin_diagnostics_redacted",
    ]:
        require(proof[field] is True, f"Route cutover readiness proof field must be true: {field}")
    for field in [
        "provider_call_attempted",
        "media_generation_attempted",
        "stripe_call_attempted",
        "billing_mutation_attempted",
        "credit_mutation_attempted",
        "customer_traffic_attempted",
        "public_cutover_enabled",
        "render_removal_attempted",
        "aws21_or_later_work_attempted",
    ]:
        require(proof[field] is False, f"Route cutover readiness proof field must be false: {field}")

    master_plan = read("PRODUCTION_COMPLETION_MASTER_PLAN.md")
    matrix = read("AWS_OPTION_A_MEDIA_MIGRATION_MATRIX.md")
    gap_plan = read("PRODUCTION_FINISH_AUDIT_AND_GAP_PLAN.md")
    for marker in [
        "Production route cutover readiness proof",
        "route_cutover_readiness_passed=true",
        "synthetic_route_reached_aws_durable_path=true",
        "synthetic_status_readback_passed=true",
        "synthetic_asset_result_metadata_passed=true",
    ]:
        require(
            marker in master_plan or marker in matrix or marker in gap_plan,
            f"Production docs missing route cutover readiness marker: {marker}",
        )

    assert_no_forbidden_values(proof, "final route cutover readiness proof")
    print("PRODUCTION_ROUTE_CUTOVER_READINESS_PROOF:")
    print(json.dumps(proof, indent=2, sort_keys=True))
    print("PRODUCTION_ROUTE_CUTOVER_READINESS_VERIFICATION_PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
