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
    "DURABLE_ASSET_BUCKET_SHOULD_NOT_LEAK",
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
    "aws20_assets/non_customer",
    "X-Amz-Signature",
]


SIDE_EFFECT_KEYS = {
    "durable_asset_proof_attempted",
    "asset_store_attempted",
    "s3_put_attempted",
    "s3_get_attempted",
    "s3_metadata_get_attempted",
    "s3_delete_attempted",
    "secret_fetch_attempted",
    "secrets_manager_value_retrieved",
    "provider_call_attempted",
    "paid_provider_calls_started",
    "media_generation_attempted",
    "customer_asset_used",
    "stripe_call_attempted",
    "billing_mutation_attempted",
    "credit_mutation_attempted",
    "customer_traffic_attempted",
    "worker_started",
    "media_worker_started",
    "public_cutover_enabled",
    "public_production_cutover_enabled",
}


PAID_SIDE_EFFECT_KEYS = [
    "provider_call_attempted",
    "paid_provider_calls_started",
    "media_generation_attempted",
    "customer_asset_used",
    "stripe_call_attempted",
    "billing_mutation_attempted",
    "credit_mutation_attempted",
    "customer_traffic_attempted",
    "public_cutover_enabled",
    "public_production_cutover_enabled",
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


def assert_paid_side_effects_disabled(result: dict, label: str) -> None:
    for key in PAID_SIDE_EFFECT_KEYS:
        require(result.get(key) is False, f"{label} enabled forbidden paid/customer side effect: {key}")


def dangerous_env() -> dict:
    return {
        "AWS_OPTION_A_ENABLED": "true",
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


def proof_flags(helper) -> dict:
    env = dangerous_env()
    env.update(
        {
            helper.AWS_SYNTHETIC_DURABLE_ASSET_PROOF_ENABLED_FLAG: "true",
            helper.AWS_SYNTHETIC_DURABLE_ASSET_OWNER_APPROVED_FLAG: "true",
            helper.AWS_SYNTHETIC_DURABLE_ASSET_VALIDATION_CONFIRMED_FLAG: "true",
            helper.AWS_SYNTHETIC_DURABLE_ASSET_S3_WRITE_ENABLED_FLAG: "true",
            helper.AWS_SYNTHETIC_DURABLE_ASSET_METADATA_READBACK_ENABLED_FLAG: "true",
            helper.AWS_SYNTHETIC_DURABLE_ASSET_OPEN_DOWNLOAD_ENABLED_FLAG: "true",
            helper.AWS_SYNTHETIC_DURABLE_ASSET_CLEANUP_ENABLED_FLAG: "true",
        }
    )
    return env


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
        return "https://signed.example.invalid/download?X-Amz-Signature=SHOULD_NOT_LEAK"


def run_safe_default_tests(helper) -> None:
    base = helper.build_synthetic_durable_asset_delivery_proof(env={}, actor_role="admin")
    require(base["status"] == "safe_default_no_durable_asset_delivery", "Default mode must not run asset delivery proof.")
    require(base["blocked_reason"] == "blocked_durable_asset_proof_not_enabled", "Default must be blocked by proof flag.")
    require(base["rollback_controls_blocked_when_enabled"] is True, "Rollback controls must be proven to block when enabled.")
    assert_no_live_side_effects(base, "default durable asset proof")
    assert_no_forbidden_values(base, "default durable asset proof")

    route_only = helper.build_synthetic_durable_asset_delivery_proof(env=dangerous_env(), actor_role="admin")
    require(route_only["blocked_reason"] == "blocked_durable_asset_proof_not_enabled", "AWS env alone must not run asset proof.")
    assert_no_live_side_effects(route_only, "route-only durable asset proof")
    assert_no_forbidden_values(route_only, "route-only durable asset proof")

    missing_owner = dict(dangerous_env())
    missing_owner.update(
        {
            helper.AWS_SYNTHETIC_DURABLE_ASSET_PROOF_ENABLED_FLAG: "true",
            helper.AWS_SYNTHETIC_DURABLE_ASSET_S3_WRITE_ENABLED_FLAG: "true",
            helper.AWS_SYNTHETIC_DURABLE_ASSET_METADATA_READBACK_ENABLED_FLAG: "true",
            helper.AWS_SYNTHETIC_DURABLE_ASSET_OPEN_DOWNLOAD_ENABLED_FLAG: "true",
            helper.AWS_SYNTHETIC_DURABLE_ASSET_CLEANUP_ENABLED_FLAG: "true",
        }
    )
    owner_blocked = helper.build_synthetic_durable_asset_delivery_proof(env=missing_owner, actor_role="admin")
    require(owner_blocked["blocked_reason"] == "blocked_owner_approval_required", "Owner approval must be required.")
    assert_no_live_side_effects(owner_blocked, "owner-blocked durable asset proof")

    client_blocked = dict(missing_owner)
    client_blocked[helper.AWS_SYNTHETIC_DURABLE_ASSET_OWNER_APPROVED_FLAG] = "true"
    client_result = helper.build_synthetic_durable_asset_delivery_proof(env=client_blocked, actor_role="client")
    require(client_result["blocked_reason"] == "blocked_client_not_authorized", "Client must not trigger durable asset proof.")
    assert_no_live_side_effects(client_result, "client-blocked durable asset proof")

    missing_validation = dict(client_blocked)
    validation_result = helper.build_synthetic_durable_asset_delivery_proof(env=missing_validation, actor_role="admin")
    require(validation_result["blocked_reason"] == "blocked_validation_confirmation_required", "Validation confirmation must be required.")
    assert_no_live_side_effects(validation_result, "validation-blocked durable asset proof")

    cleanup_missing = proof_flags(helper)
    cleanup_missing[helper.AWS_SYNTHETIC_DURABLE_ASSET_CLEANUP_ENABLED_FLAG] = "false"
    cleanup_result = helper.build_synthetic_durable_asset_delivery_proof(env=cleanup_missing, actor_role="admin")
    require(cleanup_result["blocked_reason"] == "blocked_cleanup_required", "Cleanup flag must be required.")
    assert_no_live_side_effects(cleanup_result, "cleanup-blocked durable asset proof")

    rollback_env = proof_flags(helper)
    rollback_env["AWS_OPTION_A_KILL_SWITCH_ENABLED"] = "true"
    rollback_result = helper.build_synthetic_durable_asset_delivery_proof(env=rollback_env, actor_role="admin")
    require(rollback_result["blocked_reason"] == "blocked_by_rollback_control", "Kill switch must block durable asset proof.")
    assert_no_live_side_effects(rollback_result, "rollback-blocked durable asset proof")

    forbidden_env = proof_flags(helper)
    forbidden_env["PROVIDER_EXECUTION_ENABLED"] = "true"
    forbidden_result = helper.build_synthetic_durable_asset_delivery_proof(env=forbidden_env, actor_role="admin")
    require(forbidden_result["blocked_reason"] == "blocked_forbidden_live_execution_flag_active", "Provider/worker/billing flags must block.")
    assert_no_live_side_effects(forbidden_result, "forbidden-flag durable asset proof")

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
        require(result["synthetic_asset_non_customer"] is True, "Proof boundary must remain synthetic non-customer.")
        require(result["synthetic_asset_non_executable"] is True, "Proof boundary must remain non-executable.")
        require(result["client_safe_asset_view_redacted"] is True, "Client-safe asset view must be redacted.")
        require(result["admin_asset_diagnostics_redacted"] is True, "Admin asset diagnostics must be redacted.")
        require(result["signed_url_exposed"] is False, "Signed URL must never be exposed.")
        assert_paid_side_effects_disabled(result, "safe default durable asset proof")
        assert_no_forbidden_values(result, "safe default durable asset proof")


def run_injected_s3_success_test(helper) -> None:
    fake = FakeS3Client()
    result = helper.build_synthetic_durable_asset_delivery_proof(
        env=proof_flags(helper),
        actor_role="admin",
        s3_client=fake,
    )
    require(result["status"] == "synthetic_durable_asset_delivery_passed", "Injected S3 proof must pass.")
    for key in [
        "durable_asset_proof_attempted",
        "durable_asset_proof_passed",
        "owner_flags_required",
        "synthetic_asset_non_customer",
        "synthetic_asset_non_executable",
        "asset_store_attempted",
        "asset_store_passed",
        "asset_job_link_passed",
        "asset_metadata_readback_passed",
        "asset_open_or_download_proof_passed",
        "client_safe_asset_view_redacted",
        "admin_asset_diagnostics_redacted",
        "cleanup_or_retention_safe_state_passed",
        "rollback_controls_blocked_when_enabled",
    ]:
        require(result.get(key) is True, f"Injected S3 proof field must be true: {key}")
    for key in PAID_SIDE_EFFECT_KEYS:
        require(result.get(key) is False, f"Injected S3 proof forbidden field must be false: {key}")

    require(result["signed_url_exposed"] is False, "Injected S3 proof must not expose signed URL.")
    require(result["client_safe_asset_view"]["raw_storage_identifiers_exposed"] is False, "Client view must hide raw storage identifiers.")
    require(result["client_safe_asset_view"]["signed_url_exposed"] is False, "Client view must hide signed URL.")
    require(result["admin_asset_diagnostics"]["raw_infrastructure_identifiers_exposed"] is False, "Admin diagnostics must be redacted.")
    require(fake.put_count == 2, "Injected S3 proof should store asset and metadata objects.")
    require(fake.get_count == 2, "Injected S3 proof should read asset and metadata objects.")
    require(fake.delete_count == 2, "Injected S3 proof should clean up asset and metadata objects.")
    require(fake.objects == {}, "Injected S3 proof must leave no fake objects after cleanup.")
    assert_no_forbidden_values(result, "injected S3 durable asset proof")


def load_local_env_if_requested(helper) -> None:
    if not helper.enabled(os.environ.get(helper.AWS_SYNTHETIC_DURABLE_ASSET_LOAD_LOCAL_ENV_FLAG)):
        return
    for name in (".env.aws.local", ".env.local"):
        path = ROOT / name
        if not path.exists():
            continue
        for raw_line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


def live_mode_requested(helper) -> bool:
    env = os.environ
    return any(
        helper.enabled(env.get(flag))
        for flag in [
            helper.AWS_SYNTHETIC_DURABLE_ASSET_PROOF_ENABLED_FLAG,
            helper.AWS_SYNTHETIC_DURABLE_ASSET_OWNER_APPROVED_FLAG,
            helper.AWS_SYNTHETIC_DURABLE_ASSET_S3_WRITE_ENABLED_FLAG,
            helper.AWS_SYNTHETIC_DURABLE_ASSET_METADATA_READBACK_ENABLED_FLAG,
            helper.AWS_SYNTHETIC_DURABLE_ASSET_OPEN_DOWNLOAD_ENABLED_FLAG,
        ]
    )


def print_sanitized_live_result(result: dict) -> None:
    print("SYNTHETIC_DURABLE_ASSET_DELIVERY_SANITIZED_RESULT:" + json.dumps(result, sort_keys=True))


def run_owner_approved_live_mode_if_requested(helper) -> str:
    load_local_env_if_requested(helper)
    if not live_mode_requested(helper):
        return "SYNTHETIC_DURABLE_ASSET_DELIVERY_SKIPPED_SAFE_DEFAULT_MODE"

    required_flags = [
        helper.AWS_SYNTHETIC_DURABLE_ASSET_PROOF_ENABLED_FLAG,
        helper.AWS_SYNTHETIC_DURABLE_ASSET_OWNER_APPROVED_FLAG,
        helper.AWS_SYNTHETIC_DURABLE_ASSET_VALIDATION_CONFIRMED_FLAG,
        helper.AWS_SYNTHETIC_DURABLE_ASSET_S3_WRITE_ENABLED_FLAG,
        helper.AWS_SYNTHETIC_DURABLE_ASSET_METADATA_READBACK_ENABLED_FLAG,
        helper.AWS_SYNTHETIC_DURABLE_ASSET_OPEN_DOWNLOAD_ENABLED_FLAG,
        helper.AWS_SYNTHETIC_DURABLE_ASSET_CLEANUP_ENABLED_FLAG,
    ]
    missing = [flag for flag in required_flags if not helper.enabled(os.environ.get(flag))]
    require(not missing, f"Owner-approved live mode requires every durable asset gate: {', '.join(missing)}")

    result = helper.build_synthetic_durable_asset_delivery_proof(env=os.environ, actor_role="admin")
    print_sanitized_live_result(result)
    assert_no_forbidden_values(result, "owner-approved live durable asset proof")
    assert_paid_side_effects_disabled(result, "owner-approved live durable asset proof")

    require(result["status"] == "synthetic_durable_asset_delivery_passed", "Live durable asset delivery proof did not pass.")
    for key in [
        "durable_asset_proof_attempted",
        "durable_asset_proof_passed",
        "synthetic_asset_non_customer",
        "synthetic_asset_non_executable",
        "asset_store_attempted",
        "asset_store_passed",
        "asset_job_link_passed",
        "asset_metadata_readback_passed",
        "asset_open_or_download_proof_passed",
        "client_safe_asset_view_redacted",
        "admin_asset_diagnostics_redacted",
        "cleanup_or_retention_safe_state_passed",
        "rollback_controls_blocked_when_enabled",
    ]:
        require(result.get(key) is True, f"Live proof field must be true: {key}")
    require(result.get("signed_url_exposed") is False, "Live proof must not expose a signed URL.")
    require(str(result.get("object_key_hash_prefix") or "").strip(), "Live proof must expose only object key hash prefix.")
    require(str(result.get("synthetic_asset_reference_hash") or "").strip(), "Live proof must expose asset hash only.")
    require(str(result.get("synthetic_job_reference_hash") or "").strip(), "Live proof must expose job hash only.")
    return "SYNTHETIC_DURABLE_ASSET_DELIVERY_RUN_OWNER_APPROVED_MODE"


def main() -> int:
    helper = load_module(
        "backend/app/runtime/aws_synthetic_durable_asset_delivery.py",
        "aws_synthetic_durable_asset_delivery_under_test",
    )
    source = read("backend/app/runtime/aws_synthetic_durable_asset_delivery.py")

    for marker in ["requests.", "httpx.", "stripe.", "runway.", "elevenlabs.", "kling."]:
        require(marker not in source, f"Synthetic durable asset helper must not contain paid provider/Stripe marker: {marker}")
    for marker in [
        "AWS_SYNTHETIC_DURABLE_ASSET_PROOF_ENABLED",
        "AWS_SYNTHETIC_DURABLE_ASSET_OWNER_APPROVED",
        "AWS_SYNTHETIC_DURABLE_ASSET_VALIDATION_CONFIRMED",
        "AWS_SYNTHETIC_DURABLE_ASSET_S3_WRITE_ENABLED",
        "AWS_SYNTHETIC_DURABLE_ASSET_METADATA_READBACK_ENABLED",
        "AWS_SYNTHETIC_DURABLE_ASSET_OPEN_DOWNLOAD_ENABLED",
        "AWS_SYNTHETIC_DURABLE_ASSET_CLEANUP_ENABLED",
        "durable_asset_proof_attempted",
        "durable_asset_proof_passed",
        "synthetic_asset_non_customer",
        "synthetic_asset_non_executable",
        "asset_store_attempted",
        "asset_store_passed",
        "asset_job_link_passed",
        "asset_metadata_readback_passed",
        "asset_open_or_download_proof_passed",
        "client_safe_asset_view_redacted",
        "admin_asset_diagnostics_redacted",
        "cleanup_or_retention_safe_state_passed",
        "rollback_controls_blocked_when_enabled",
        "provider_call_attempted",
        "media_generation_attempted",
        "customer_asset_used",
        "signed_url_exposed",
    ]:
        require(marker in source, f"Synthetic durable asset source missing marker: {marker}")

    run_safe_default_tests(helper)
    run_injected_s3_success_test(helper)
    live_mode_status = run_owner_approved_live_mode_if_requested(helper)
    print(f"SYNTHETIC_DURABLE_ASSET_DELIVERY_VERIFICATION_PASSED:{live_mode_status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
