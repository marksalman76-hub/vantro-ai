from __future__ import annotations

from datetime import datetime, timezone
import json
from typing import Any, Dict, Mapping, Optional
import uuid

from backend.app.runtime.aws_option_a_live_rehearsal import (
    build_boto3_client,
    clean_text,
    enabled,
    redacted_ref,
    redact_secret_values,
    safe_error_code,
    safe_exception_status,
    safe_hash,
)
from backend.app.runtime.aws_option_a_rollback_controls import (
    AWS_OPTION_A_KILL_SWITCH_ENABLED_FLAG,
    build_aws_option_a_rollback_control_decision,
)


AWS_SYNTHETIC_DURABLE_ASSET_PROOF_ENABLED_FLAG = "AWS_SYNTHETIC_DURABLE_ASSET_PROOF_ENABLED"
AWS_SYNTHETIC_DURABLE_ASSET_OWNER_APPROVED_FLAG = "AWS_SYNTHETIC_DURABLE_ASSET_OWNER_APPROVED"
AWS_SYNTHETIC_DURABLE_ASSET_VALIDATION_CONFIRMED_FLAG = "AWS_SYNTHETIC_DURABLE_ASSET_VALIDATION_CONFIRMED"
AWS_SYNTHETIC_DURABLE_ASSET_S3_WRITE_ENABLED_FLAG = "AWS_SYNTHETIC_DURABLE_ASSET_S3_WRITE_ENABLED"
AWS_SYNTHETIC_DURABLE_ASSET_METADATA_READBACK_ENABLED_FLAG = "AWS_SYNTHETIC_DURABLE_ASSET_METADATA_READBACK_ENABLED"
AWS_SYNTHETIC_DURABLE_ASSET_OPEN_DOWNLOAD_ENABLED_FLAG = "AWS_SYNTHETIC_DURABLE_ASSET_OPEN_DOWNLOAD_ENABLED"
AWS_SYNTHETIC_DURABLE_ASSET_CLEANUP_ENABLED_FLAG = "AWS_SYNTHETIC_DURABLE_ASSET_CLEANUP_ENABLED"
AWS_SYNTHETIC_DURABLE_ASSET_LOAD_LOCAL_ENV_FLAG = "AWS_SYNTHETIC_DURABLE_ASSET_LOAD_LOCAL_ENV"

SYNTHETIC_DURABLE_ASSET_DIAGNOSTIC_VERSION = "aws_synthetic_durable_asset_delivery_v1"
SYNTHETIC_ASSET_JOB_PREFIX = "aws_asset_delivery_non_customer"
SYNTHETIC_ASSET_PREFIX = "aws20_assets/non_customer"
SYNTHETIC_ASSET_MARKER = "aws20_durable_asset_delivery_non_customer"

FORBIDDEN_LIVE_EXECUTION_FLAGS = (
    "AWS_MEDIA_WORKER_ENABLED",
    "MEDIA_WORKER_ENABLED",
    "RUN_MEDIA_WORKER",
    "ENABLE_MEDIA_WORKERS",
    "PROVIDER_EXECUTION_ENABLED",
    "PAID_PROVIDER_EXECUTION_ENABLED",
    "MEDIA_PROVIDER_EXECUTION_ENABLED",
    "STRIPE_LIVE_MODE",
    "STRIPE_CALLS_ENABLED",
    "BILLING_MUTATION_ENABLED",
    "CREDIT_MUTATION_ENABLED",
    "PUBLIC_PRODUCTION_CUTOVER_ENABLED",
    "AWS_PUBLIC_PRODUCTION_CUTOVER_ENABLED",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def synthetic_asset_job_id() -> str:
    return f"{SYNTHETIC_ASSET_JOB_PREFIX}_{uuid.uuid4().hex[:12]}"


def synthetic_asset_id() -> str:
    return f"synthetic_asset_{uuid.uuid4().hex[:12]}"


def durable_asset_flags(env: Mapping[str, Any]) -> Dict[str, bool]:
    return {
        "durable_asset_proof_enabled": enabled(env.get(AWS_SYNTHETIC_DURABLE_ASSET_PROOF_ENABLED_FLAG)),
        "owner_approved": enabled(env.get(AWS_SYNTHETIC_DURABLE_ASSET_OWNER_APPROVED_FLAG)),
        "validation_confirmed": enabled(env.get(AWS_SYNTHETIC_DURABLE_ASSET_VALIDATION_CONFIRMED_FLAG)),
        "s3_write_enabled": enabled(env.get(AWS_SYNTHETIC_DURABLE_ASSET_S3_WRITE_ENABLED_FLAG)),
        "metadata_readback_enabled": enabled(env.get(AWS_SYNTHETIC_DURABLE_ASSET_METADATA_READBACK_ENABLED_FLAG)),
        "open_download_enabled": enabled(env.get(AWS_SYNTHETIC_DURABLE_ASSET_OPEN_DOWNLOAD_ENABLED_FLAG)),
        "cleanup_enabled": enabled(env.get(AWS_SYNTHETIC_DURABLE_ASSET_CLEANUP_ENABLED_FLAG)),
    }


def forbidden_live_execution_flags(env: Mapping[str, Any]) -> list[str]:
    return [flag for flag in FORBIDDEN_LIVE_EXECUTION_FLAGS if enabled(env.get(flag))]


def base_side_effect_guards() -> Dict[str, bool]:
    return {
        "provider_call_attempted": False,
        "paid_provider_calls_started": False,
        "media_generation_attempted": False,
        "customer_asset_used": False,
        "stripe_call_attempted": False,
        "billing_mutation_attempted": False,
        "credit_mutation_attempted": False,
        "customer_traffic_attempted": False,
        "public_cutover_enabled": False,
        "public_production_cutover_enabled": False,
        "worker_started": False,
        "media_worker_started": False,
        "secret_fetch_attempted": False,
        "secrets_manager_value_retrieved": False,
        "credential_values_exposed": False,
        "provider_secret_values_visible": False,
        "signed_url_exposed": False,
    }


def safe_asset_exception_details(exc: BaseException) -> Dict[str, Any]:
    return {
        "error_type": clean_text(exc.__class__.__name__, 120),
        "error_code": safe_error_code(exc),
        "safe_error_summary": safe_exception_status(exc),
        "credential_values_exposed": False,
        "secret_values_exposed": False,
        "raw_infrastructure_identifiers_exposed": False,
    }


def rollback_controls_block_when_enabled(env: Mapping[str, Any]) -> bool:
    rollback_env = dict(env)
    rollback_env[AWS_OPTION_A_KILL_SWITCH_ENABLED_FLAG] = "true"
    decision = build_aws_option_a_rollback_control_decision(
        env=rollback_env,
        route_kind="synthetic_durable_asset_delivery",
        route_intent=True,
        route_execution_allowed=True,
        selected_runtime_path="aws_synthetic_durable_asset_delivery_boundary",
        route_mode="synthetic_durable_asset_delivery_proof",
    )
    return bool(decision.get("aws_route_blocked_by_rollback"))


def rollback_active(env: Mapping[str, Any]) -> bool:
    decision = build_aws_option_a_rollback_control_decision(
        env=env,
        route_kind="synthetic_durable_asset_delivery",
        route_intent=True,
        route_execution_allowed=True,
        selected_runtime_path="aws_synthetic_durable_asset_delivery_boundary",
        route_mode="synthetic_durable_asset_delivery_proof",
    )
    return bool(decision.get("aws_route_blocked_by_rollback"))


def blocking_reason(
    *,
    actor_role: str,
    flags: Mapping[str, bool],
    env: Mapping[str, Any],
    forbidden_flags: list[str],
) -> str:
    if clean_text(actor_role, 80).lower() not in {"admin", "owner"}:
        return "blocked_client_not_authorized"
    if forbidden_flags:
        return "blocked_forbidden_live_execution_flag_active"
    if rollback_active(env):
        return "blocked_by_rollback_control"
    if not flags.get("durable_asset_proof_enabled"):
        return "blocked_durable_asset_proof_not_enabled"
    if not flags.get("owner_approved"):
        return "blocked_owner_approval_required"
    if not flags.get("validation_confirmed"):
        return "blocked_validation_confirmation_required"
    if not flags.get("s3_write_enabled"):
        return "blocked_s3_write_flag_required"
    if not flags.get("metadata_readback_enabled"):
        return "blocked_metadata_readback_flag_required"
    if not flags.get("open_download_enabled"):
        return "blocked_open_download_flag_required"
    if not flags.get("cleanup_enabled"):
        return "blocked_cleanup_required"
    return ""


def synthetic_asset_body(job_id: str, asset_id: str) -> bytes:
    return json.dumps(
        {
            "marker": SYNTHETIC_ASSET_MARKER,
            "asset_kind": "synthetic_durable_asset_delivery_proof",
            "job_reference_hash": safe_hash(job_id),
            "asset_reference_hash": safe_hash(asset_id),
            "non_customer": True,
            "non_executable": True,
            "customer_asset_used": False,
            "provider_generated": False,
            "media_generation_attempted": False,
            "created_at": utc_now(),
        },
        sort_keys=True,
    ).encode("utf-8")


def synthetic_asset_keys(job_id: str, asset_id: str) -> Dict[str, str]:
    job_hash = safe_hash(job_id, 16)
    asset_hash = safe_hash(asset_id, 16)
    base = f"{SYNTHETIC_ASSET_PREFIX}/{job_hash}/{asset_hash}"
    return {
        "asset_key": f"{base}/asset.txt",
        "metadata_key": f"{base}/metadata.json",
    }


def empty_asset_result(status: str = "skipped_not_enabled") -> Dict[str, Any]:
    return {
        "resource": "synthetic_durable_asset_delivery",
        "status": status,
        "durable_asset_proof_attempted": False,
        "durable_asset_proof_passed": False,
        "synthetic_asset_non_customer": True,
        "synthetic_asset_non_executable": True,
        "asset_store_attempted": False,
        "asset_store_passed": False,
        "asset_job_link_passed": False,
        "asset_metadata_readback_passed": False,
        "asset_open_or_download_proof_passed": False,
        "client_safe_asset_view_redacted": True,
        "admin_asset_diagnostics_redacted": True,
        "cleanup_or_retention_safe_state_passed": False,
        "s3_put_attempted": False,
        "s3_get_attempted": False,
        "s3_metadata_get_attempted": False,
        "s3_delete_attempted": False,
        "signed_url_created": False,
        "signed_url_exposed": False,
        "bucket_reference": redacted_ref(""),
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def delete_object_if_possible(s3_client: Any, bucket: str, key: str) -> bool:
    getattr(s3_client, "delete_object")(Bucket=bucket, Key=key)
    try:
        getattr(s3_client, "head_object")(Bucket=bucket, Key=key)
    except Exception:
        return True
    return False


def run_s3_durable_asset_delivery_proof(
    *,
    env: Mapping[str, Any],
    job_id: str,
    asset_id: str,
    s3_client: Any = None,
) -> Dict[str, Any]:
    result = empty_asset_result()
    bucket = clean_text(
        env.get("AWS_DURABLE_ASSET_S3_BUCKET")
        or env.get("AWS_MEDIA_S3_BUCKET")
        or env.get("AWS_UPLOADS_S3_BUCKET"),
        1000,
    )
    keys = synthetic_asset_keys(job_id, asset_id)
    body = synthetic_asset_body(job_id, asset_id)
    body_hash = safe_hash(body.decode("utf-8", errors="ignore"), 16)
    asset_metadata = {
        "marker": SYNTHETIC_ASSET_MARKER,
        "job_reference_hash": safe_hash(job_id),
        "asset_reference_hash": safe_hash(asset_id),
        "asset_body_hash": body_hash,
        "synthetic_asset_non_customer": True,
        "synthetic_asset_non_executable": True,
        "customer_asset_used": False,
        "content_type": "text/plain",
        "size_bytes": len(body),
        "open_download_mode": "s3_get_object_and_internal_presigned_url_probe",
        "signed_url_exposed": False,
        "created_at": utc_now(),
    }
    result.update(
        {
            "bucket_reference": redacted_ref(bucket),
            "synthetic_asset_reference_hash": safe_hash(asset_id),
            "synthetic_job_reference_hash": safe_hash(job_id),
            "object_key_hash_prefix": safe_hash(keys["asset_key"], 12),
            "metadata_object_key_hash_prefix": safe_hash(keys["metadata_key"], 12),
            "asset_body_hash": body_hash,
            "asset_body_size": len(body),
            "content_type": "text/plain",
        }
    )
    if not bucket:
        result["status"] = "blocked_missing_durable_asset_s3_bucket"
        result["next_operator_action"] = "Set AWS_DURABLE_ASSET_S3_BUCKET or AWS_MEDIA_S3_BUCKET, then rerun once with owner approval."
        return redact_secret_values(result)

    if s3_client is None:
        try:
            s3_client, blocked = build_boto3_client("s3", env)
        except Exception as exc:
            result.update(
                {
                    "status": safe_exception_status(exc),
                    "error": safe_asset_exception_details(exc),
                    "next_operator_action": "Reload AWS credentials/region and rerun the synthetic durable asset proof once.",
                }
            )
            return redact_secret_values(result)
        if blocked:
            result["status"] = blocked
            result["next_operator_action"] = "Install/restore boto3 in the validation environment before rerun."
            return redact_secret_values(result)

    result.update(
        {
            "status": "durable_asset_s3_delivery_started",
            "durable_asset_proof_attempted": True,
            "asset_store_attempted": True,
            "s3_put_attempted": True,
        }
    )
    try:
        getattr(s3_client, "put_object")(
            Bucket=bucket,
            Key=keys["asset_key"],
            Body=body,
            ContentType="text/plain",
            Metadata={
                "synthetic": "true",
                "non-customer": "true",
                "non-executable": "true",
                "job-reference-hash": safe_hash(job_id),
                "asset-reference-hash": safe_hash(asset_id),
            },
        )
        getattr(s3_client, "put_object")(
            Bucket=bucket,
            Key=keys["metadata_key"],
            Body=json.dumps(asset_metadata, sort_keys=True).encode("utf-8"),
            ContentType="application/json",
            Metadata={
                "synthetic": "true",
                "non-customer": "true",
                "non-executable": "true",
            },
        )
        result["asset_store_passed"] = True
        result["s3_get_attempted"] = True
        asset_response = getattr(s3_client, "get_object")(Bucket=bucket, Key=keys["asset_key"])
        asset_read_body = getattr(asset_response["Body"], "read")()
        content_read_passed = asset_read_body == body and SYNTHETIC_ASSET_MARKER.encode("utf-8") in asset_read_body

        result["s3_metadata_get_attempted"] = True
        metadata_response = getattr(s3_client, "get_object")(Bucket=bucket, Key=keys["metadata_key"])
        metadata_body = getattr(metadata_response["Body"], "read")()
        metadata_read = json.loads(metadata_body.decode("utf-8"))
        metadata_readback_passed = bool(
            metadata_read.get("marker") == SYNTHETIC_ASSET_MARKER
            and metadata_read.get("job_reference_hash") == safe_hash(job_id)
            and metadata_read.get("asset_reference_hash") == safe_hash(asset_id)
            and metadata_read.get("asset_body_hash") == body_hash
            and metadata_read.get("synthetic_asset_non_customer") is True
            and metadata_read.get("synthetic_asset_non_executable") is True
            and metadata_read.get("customer_asset_used") is False
        )
        signed_url_created = bool(
            getattr(s3_client, "generate_presigned_url")(
                "get_object",
                Params={"Bucket": bucket, "Key": keys["asset_key"]},
                ExpiresIn=300,
            )
        )
        result.update(
            {
                "signed_url_created": signed_url_created,
                "signed_url_exposed": False,
                "asset_job_link_passed": metadata_read.get("job_reference_hash") == safe_hash(job_id),
                "asset_metadata_readback_passed": metadata_readback_passed,
                "asset_open_or_download_proof_passed": bool(content_read_passed and signed_url_created),
            }
        )
        result["s3_delete_attempted"] = True
        asset_deleted = delete_object_if_possible(s3_client, bucket, keys["asset_key"])
        metadata_deleted = delete_object_if_possible(s3_client, bucket, keys["metadata_key"])
        cleanup_passed = bool(asset_deleted and metadata_deleted)
        passed = bool(
            result["asset_store_passed"]
            and result["asset_job_link_passed"]
            and result["asset_metadata_readback_passed"]
            and result["asset_open_or_download_proof_passed"]
            and cleanup_passed
        )
        result.update(
            {
                "status": "passed" if passed else "failed_durable_asset_readback_or_cleanup",
                "durable_asset_proof_passed": passed,
                "cleanup_or_retention_safe_state_passed": cleanup_passed,
                "cleanup_performed": cleanup_passed,
                "client_safe_asset_view_redacted": True,
                "admin_asset_diagnostics_redacted": True,
            }
        )
    except Exception as exc:
        cleanup_attempted = False
        cleanup_passed = False
        try:
            cleanup_attempted = True
            asset_deleted = delete_object_if_possible(s3_client, bucket, keys["asset_key"])
            metadata_deleted = delete_object_if_possible(s3_client, bucket, keys["metadata_key"])
            cleanup_passed = bool(asset_deleted and metadata_deleted)
        except Exception as cleanup_exc:
            result["cleanup_error"] = {
                "status": safe_exception_status(cleanup_exc),
                "error": safe_asset_exception_details(cleanup_exc),
            }
        result.update(
            {
                "status": safe_exception_status(exc),
                "error": safe_asset_exception_details(exc),
                "cleanup_attempted": cleanup_attempted,
                "cleanup_or_retention_safe_state_passed": cleanup_passed,
                "cleanup_performed": cleanup_passed,
                "next_operator_action": "Review sanitized S3 error category and hashed object reference, then rerun only after owner approval.",
            }
        )
    return redact_secret_values(result)


def build_client_safe_asset_view(live_result: Mapping[str, Any], job_id: str, asset_id: str) -> Dict[str, Any]:
    ready = bool(live_result.get("durable_asset_proof_passed"))
    return {
        "status": "asset_delivery_ready" if ready else "asset_delivery_not_ready",
        "message": "A synthetic asset delivery proof is available." if ready else "Asset delivery proof has not completed.",
        "job_reference_hash": safe_hash(job_id),
        "asset_reference_hash": safe_hash(asset_id),
        "asset_type": "synthetic_text_asset",
        "content_type": "text/plain",
        "size_bytes": live_result.get("asset_body_size", 0),
        "open_or_download_ready": bool(live_result.get("asset_open_or_download_proof_passed")),
        "customer_safe": True,
        "internal_config_exposed": False,
        "raw_storage_identifiers_exposed": False,
        "credential_values_exposed": False,
        "provider_secret_values_visible": False,
        "signed_url_exposed": False,
    }


def build_admin_asset_diagnostics(
    *,
    job_id: str,
    asset_id: str,
    block: str,
    flags: Mapping[str, bool],
    live_result: Mapping[str, Any],
    forbidden_flags: list[str],
) -> Dict[str, Any]:
    return {
        "boundary": "aws_synthetic_durable_asset_delivery",
        "diagnostic_version": SYNTHETIC_DURABLE_ASSET_DIAGNOSTIC_VERSION,
        "blocked_reason": block,
        "owner_flags_required": True,
        "flags": flags,
        "synthetic_job_reference_hash": safe_hash(job_id),
        "synthetic_asset_reference_hash": safe_hash(asset_id),
        "object_key_hash_prefix": live_result.get("object_key_hash_prefix", ""),
        "metadata_object_key_hash_prefix": live_result.get("metadata_object_key_hash_prefix", ""),
        "bucket_reference": live_result.get("bucket_reference", redacted_ref("")),
        "asset_store_passed": bool(live_result.get("asset_store_passed")),
        "asset_job_link_passed": bool(live_result.get("asset_job_link_passed")),
        "asset_metadata_readback_passed": bool(live_result.get("asset_metadata_readback_passed")),
        "asset_open_or_download_proof_passed": bool(live_result.get("asset_open_or_download_proof_passed")),
        "cleanup_or_retention_safe_state_passed": bool(live_result.get("cleanup_or_retention_safe_state_passed")),
        "signed_url_created": bool(live_result.get("signed_url_created")),
        "signed_url_exposed": False,
        "forbidden_live_execution_flags_active": forbidden_flags,
        "admin_asset_diagnostics_redacted": True,
        "credential_values_exposed": False,
        "secret_values_exposed": False,
        "raw_infrastructure_identifiers_exposed": False,
    }


def build_blocked_result(
    *,
    env: Mapping[str, Any],
    actor_role: str,
    block: str,
    flags: Mapping[str, bool],
    forbidden_flags: list[str],
) -> Dict[str, Any]:
    job_id = synthetic_asset_job_id()
    asset_id = synthetic_asset_id()
    live_result = empty_asset_result(block)
    live_result_fields = dict(live_result)
    live_result_fields.pop("status", None)
    result = {
        "boundary": "aws_synthetic_durable_asset_delivery",
        "diagnostic_version": SYNTHETIC_DURABLE_ASSET_DIAGNOSTIC_VERSION,
        "status": "safe_default_no_durable_asset_delivery",
        "blocked_reason": block,
        "actor_role": clean_text(actor_role, 80),
        "flags": flags,
        "owner_flags_required": True,
        "rollback_controls_blocked_when_enabled": rollback_controls_block_when_enabled(env),
        "client_safe_asset_view": build_client_safe_asset_view(live_result, job_id, asset_id),
        "admin_asset_diagnostics": build_admin_asset_diagnostics(
            job_id=job_id,
            asset_id=asset_id,
            block=block,
            flags=flags,
            live_result=live_result,
            forbidden_flags=forbidden_flags,
        ),
        "customer_safe": True,
        "credential_values_exposed": False,
        "provider_secret_values_visible": False,
    }
    result.update(live_result_fields)
    result.update(base_side_effect_guards())
    return redact_secret_values(result)


def build_synthetic_durable_asset_delivery_proof(
    *,
    env: Optional[Mapping[str, Any]] = None,
    actor_role: str = "admin",
    s3_client: Any = None,
) -> Dict[str, Any]:
    env = dict(env or {})
    flags = durable_asset_flags(env)
    forbidden_flags = forbidden_live_execution_flags(env)
    block = blocking_reason(actor_role=actor_role, flags=flags, env=env, forbidden_flags=forbidden_flags)
    if block:
        return build_blocked_result(
            env=env,
            actor_role=actor_role,
            block=block,
            flags=flags,
            forbidden_flags=forbidden_flags,
        )

    job_id = synthetic_asset_job_id()
    asset_id = synthetic_asset_id()
    live_result = run_s3_durable_asset_delivery_proof(
        env=env,
        job_id=job_id,
        asset_id=asset_id,
        s3_client=s3_client,
    )
    live_passed = bool(live_result.get("durable_asset_proof_passed"))
    result = {
        "boundary": "aws_synthetic_durable_asset_delivery",
        "diagnostic_version": SYNTHETIC_DURABLE_ASSET_DIAGNOSTIC_VERSION,
        "status": (
            "synthetic_durable_asset_delivery_passed"
            if live_passed
            else (
                "synthetic_durable_asset_delivery_failed"
                if live_result.get("durable_asset_proof_attempted")
                else "safe_default_no_durable_asset_delivery"
            )
        ),
        "blocked_reason": "",
        "flags": flags,
        "owner_flags_required": True,
        "synthetic_asset_reference_hash": safe_hash(asset_id),
        "synthetic_job_reference_hash": safe_hash(job_id),
        "rollback_controls_blocked_when_enabled": rollback_controls_block_when_enabled(env),
        "client_safe_asset_view": build_client_safe_asset_view(live_result, job_id, asset_id),
        "admin_asset_diagnostics": build_admin_asset_diagnostics(
            job_id=job_id,
            asset_id=asset_id,
            block="",
            flags=flags,
            live_result=live_result,
            forbidden_flags=forbidden_flags,
        ),
        "live_result": live_result,
        "incident_event": {
            "event_type": "synthetic_durable_asset_delivery_proof",
            "severity": "info" if live_passed else "warning",
            "decision": "passed" if live_passed else "failed_after_live_attempt",
            "safe_job_reference_hash": safe_hash(job_id),
            "safe_asset_reference_hash": safe_hash(asset_id),
            "timestamp": utc_now(),
            "external_logging_attempted": False,
            "cloudwatch_put_attempted": False,
        },
        "customer_safe": True,
        "credential_values_exposed": False,
        "provider_secret_values_visible": False,
    }
    result.update(
        {
            key: live_result.get(key)
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
                "object_key_hash_prefix",
                "metadata_object_key_hash_prefix",
                "signed_url_created",
                "signed_url_exposed",
            ]
        }
    )
    result.update(base_side_effect_guards())
    return redact_secret_values(result)
