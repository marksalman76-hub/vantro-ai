from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import importlib
import json
import re
import uuid
from typing import Any, Dict, Mapping, Optional

from backend.app.runtime.aws_option_a_observability import DIAGNOSTIC_VERSION
from backend.app.runtime.aws_option_a_rollback_controls import build_aws_option_a_rollback_control_decision


AWS_OPTION_A_LIVE_REHEARSAL_ENABLED_FLAG = "AWS_OPTION_A_LIVE_REHEARSAL_ENABLED"
AWS_OPTION_A_LIVE_REHEARSAL_OWNER_APPROVED_FLAG = "AWS_OPTION_A_LIVE_REHEARSAL_OWNER_APPROVED"
AWS_OPTION_A_REHEARSAL_RDS_WRITE_ENABLED_FLAG = "AWS_OPTION_A_REHEARSAL_RDS_WRITE_ENABLED"
AWS_OPTION_A_REHEARSAL_SQS_SEND_ENABLED_FLAG = "AWS_OPTION_A_REHEARSAL_SQS_SEND_ENABLED"
AWS_OPTION_A_REHEARSAL_S3_WRITE_ENABLED_FLAG = "AWS_OPTION_A_REHEARSAL_S3_WRITE_ENABLED"
AWS_OPTION_A_REHEARSAL_CLEANUP_ENABLED_FLAG = "AWS_OPTION_A_REHEARSAL_CLEANUP_ENABLED"
AWS_OPTION_A_REHEARSAL_ONLY_SQS_FLAG = "AWS_OPTION_A_REHEARSAL_ONLY_SQS"

REHEARSAL_JOB_PREFIX = "aws20_rehearsal_non_customer"
REHEARSAL_DIAGNOSTIC_VERSION = "aws20_live_rehearsal_v1"
TRUE_VALUES = {"1", "true", "yes", "on", "enabled"}

SECRET_KEY_MARKERS = (
    "api_key",
    "apikey",
    "authorization",
    "bearer",
    "credential",
    "database_url",
    "password",
    "private_key",
    "provider_api_key",
    "queue_url",
    "rds_password",
    "secret",
    "stripe_secret_key",
    "token",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def clean_text(value: Any, limit: int = 1000) -> str:
    return str(value or "").strip()[:limit]


def enabled(value: Any) -> bool:
    return clean_text(value, 80).lower() in TRUE_VALUES


def optional_dependency(module_name: str):
    try:
        return importlib.import_module(module_name)
    except ModuleNotFoundError:
        return None


def safe_hash(value: Any, length: int = 12) -> str:
    text = clean_text(value, 5000)
    if not text:
        return ""
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()[:length]


def sanitize_text(value: Any, limit: int = 240) -> str:
    text = clean_text(value, limit * 2)
    if not text:
        return ""
    text = re.sub(r"arn:aws:[^\s,;]+", "[redacted-arn]", text, flags=re.IGNORECASE)
    text = re.sub(r"https?://[^\s,;]+", "[redacted-url]", text, flags=re.IGNORECASE)
    text = re.sub(r"\b\d{12,}\b", "[redacted-id]", text)
    text = re.sub(r"postgres(?:ql)?://[^\s,;]+", "[redacted-database-url]", text, flags=re.IGNORECASE)
    text = re.sub(
        r"(?i)\b(?:[a-z0-9]+[_-])*(?:aws_access_key_id|aws_secret_access_key|aws_session_token|api[_-]?key|authorization|bearer|credential|database_url|password|private_key|provider[_-]?api[_-]?key|queue[_-]?url|rds_password|secret|stripe[_-]?secret[_-]?key|token)\b\s*[:=]?\s*[^\s,;]*",
        "[redacted-secret-marker]",
        text,
    )
    return re.sub(r"\s+", " ", text).strip()[:limit]


def redact_secret_values(value: Any) -> Any:
    if isinstance(value, dict):
        cleaned: Dict[str, Any] = {}
        for key, item in value.items():
            key_l = str(key).lower()
            if isinstance(item, bool):
                cleaned[key] = item
            elif any(marker in key_l for marker in SECRET_KEY_MARKERS):
                if key_l.endswith("_present") or "hash" in key_l or key_l.endswith("_length"):
                    cleaned[key] = redact_secret_values(item)
                else:
                    cleaned[key] = "[redacted]"
            else:
                cleaned[key] = redact_secret_values(item)
        return cleaned
    if isinstance(value, list):
        return [redact_secret_values(item) for item in value]
    if isinstance(value, str):
        return sanitize_text(value, 1000)
    return value


def redacted_ref(value: Any) -> Dict[str, Any]:
    text = clean_text(value, 5000)
    return {
        "present": bool(text),
        "redacted": True,
        "length": len(text),
        "sha256_12": safe_hash(text),
    }


def safe_exception_status(exc: BaseException) -> str:
    name = exc.__class__.__name__
    message = str(exc).lower()
    if name in {
        "NoCredentialsError",
        "PartialCredentialsError",
        "CredentialRetrievalError",
        "SSOTokenLoadError",
        "TokenRetrievalError",
    } or "unable to locate credentials" in message:
        return "blocked_missing_aws_credentials"
    if name in {
        "NoRegionError",
        "ProfileNotFound",
        "ConfigNotFound",
        "InvalidConfigError",
        "ConfigParseError",
    } or ("profile" in message and "not found" in message):
        return "blocked_aws_config_error"
    return "aws_client_error"


def safe_exception_details(exc: BaseException) -> Dict[str, Any]:
    return {
        "error_type": clean_text(exc.__class__.__name__, 120),
        "error_code": safe_error_code(exc),
        "safe_error_summary": sanitize_text(str(exc), 300),
        "credential_values_exposed": False,
        "secret_values_exposed": False,
    }


def safe_error_code(exc: BaseException) -> str:
    response = getattr(exc, "response", None)
    if isinstance(response, Mapping):
        error = response.get("Error")
        if isinstance(error, Mapping):
            return clean_text(error.get("Code"), 120)
    return ""


def sqs_queue_type(queue_url: str) -> str:
    if not queue_url:
        return "unknown"
    return "fifo" if queue_url.lower().endswith(".fifo") else "standard"


def sqs_next_operator_action(category: str) -> str:
    actions = {
        "missing_queue_url": "Set AWS_MEDIA_QUEUE_URL to the intended AWS-20 test media queue URL.",
        "missing_region": "Set AWS_REGION to the queue region and rerun the SQS-focused rehearsal.",
        "invalid_credentials_or_signature": "Reload AWS credentials and confirm they match the queue account and region.",
        "access_denied": "Grant the rehearsal principal sqs:SendMessage on the test queue.",
        "nonexistent_queue": "Confirm the queue exists and the configured queue reference matches the intended region/account.",
        "region_mismatch": "Confirm AWS_REGION matches the configured SQS queue region.",
        "fifo_parameter_missing": "Confirm FIFO queue settings; the rehearsal should send MessageGroupId and MessageDeduplicationId.",
        "queue_policy_denied": "Review the queue resource policy for the rehearsal principal.",
        "malformed_message": "Inspect rehearsal message attributes and size; keep it synthetic and non-executable.",
        "network_or_endpoint": "Check local network, AWS endpoint reachability, and proxy/VPC endpoint configuration.",
        "missing_boto3_dependency": "Install boto3 in the rehearsal Python environment, then rerun only the SQS-focused rehearsal.",
        "unknown_sqs_error": "Review sanitized error type/code and rerun only after the operator identifies the queue-side cause.",
    }
    return actions.get(category or "unknown_sqs_error", actions["unknown_sqs_error"])


def categorize_sqs_failure(exc: Optional[BaseException] = None, *, queue_url: str = "", region_present: bool = True) -> str:
    if not queue_url:
        return "missing_queue_url"
    if not region_present:
        return "missing_region"
    if exc is None:
        return "unknown_sqs_error"

    code = safe_error_code(exc)
    code_l = code.lower()
    name_l = exc.__class__.__name__.lower()
    message_l = str(exc).lower()
    status = safe_exception_status(exc)

    if status == "blocked_missing_aws_credentials" or code_l in {
        "invalidclienttokenid",
        "signaturedoesnotmatch",
        "unrecognizedclientexception",
        "expiredtoken",
        "authfailure",
    }:
        return "invalid_credentials_or_signature"
    if status == "blocked_aws_config_error":
        return "missing_region" if "region" in message_l else "unknown_sqs_error"
    if code_l in {"aws.simplequeueservice.nonexistentqueue", "queuedoesnotexist", "nonexistentqueue"}:
        return "nonexistent_queue"
    if "does not exist for this wsdl version" in message_l or "queue does not exist" in message_l:
        return "region_mismatch" if "region" in message_l else "nonexistent_queue"
    if code_l in {"accessdenied", "accessdeniedexception", "unauthorizedoperation"}:
        return "queue_policy_denied" if "policy" in message_l else "access_denied"
    if "not authorized" in message_l or "access denied" in message_l:
        return "queue_policy_denied" if "policy" in message_l else "access_denied"
    if code_l in {"missingparameter", "invalidparameter", "invalidparametervalue"} and (
        "messagegroupid" in message_l or "messagededuplicationid" in message_l or "fifo" in message_l
    ):
        return "fifo_parameter_missing"
    if code_l in {"invalidmessagecontents", "invalidparameter", "invalidparametervalue", "malformedquerystring"}:
        return "malformed_message"
    if "endpoint" in name_l or "connecttimeout" in name_l or "readtimeout" in name_l or "connection" in name_l:
        return "network_or_endpoint"
    if "endpoint" in message_l or "timed out" in message_l or "could not connect" in message_l:
        return "network_or_endpoint"
    return "unknown_sqs_error"


def build_sqs_diagnostic_fields(
    *,
    env: Mapping[str, Any],
    queue_url: str,
    job_id: str,
    body_size: int = 0,
    attempted: bool = False,
    passed: bool = False,
    message_id: Any = "",
    exc: Optional[BaseException] = None,
) -> Dict[str, Any]:
    queue_kind = sqs_queue_type(queue_url)
    category = "" if passed else categorize_sqs_failure(
        exc,
        queue_url=queue_url,
        region_present=bool(clean_text(env.get("AWS_REGION")) or clean_text(env.get("AWS_DEFAULT_REGION"))),
    )
    return {
        "sqs_attempted": attempted,
        "sqs_passed": passed,
        "sqs_error_type": clean_text(exc.__class__.__name__, 120) if exc else "",
        "sqs_error_code": safe_error_code(exc) if exc else "",
        "sqs_error_category": category,
        "sqs_region_present": bool(clean_text(env.get("AWS_REGION")) or clean_text(env.get("AWS_DEFAULT_REGION"))),
        "sqs_queue_url_present": bool(queue_url),
        "sqs_queue_url_hash_prefix": safe_hash(queue_url, 12),
        "sqs_queue_type_standard_or_fifo": queue_kind,
        "sqs_message_group_id_required_or_used": queue_kind == "fifo",
        "sqs_message_deduplication_id_used": queue_kind == "fifo",
        "sqs_message_non_customer": True,
        "sqs_message_non_executable": True,
        "sqs_message_body_size": body_size,
        "sqs_message_id_hash_prefix": safe_hash(message_id, 12),
        "next_operator_action": "" if passed else sqs_next_operator_action(category),
    }


def synthetic_rehearsal_job_id() -> str:
    return f"{REHEARSAL_JOB_PREFIX}_{uuid.uuid4().hex[:12]}"


def base_resource_result(resource: str, status: str = "skipped_not_enabled") -> Dict[str, Any]:
    return {
        "resource": resource,
        "status": status,
        "rehearsal_artifact_marked_non_customer": True,
        "synthetic_non_customer_reference": True,
        "live_rehearsal_attempted": False,
        "network_call_attempted": False,
        "rds_write_attempted": False,
        "db_connection_attempted": False,
        "sqs_send_attempted": False,
        "s3_upload_attempted": False,
        "s3_delete_attempted": False,
        "secret_fetch_attempted": False,
        "provider_call_attempted": False,
        "stripe_call_attempted": False,
        "billing_mutation_attempted": False,
        "credit_mutation_attempted": False,
        "media_worker_started": False,
        "credential_values_exposed": False,
        "provider_secret_values_visible": False,
        "customer_safe": True,
    }


def rehearsal_flags(env: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "live_rehearsal_enabled": enabled(env.get(AWS_OPTION_A_LIVE_REHEARSAL_ENABLED_FLAG)),
        "owner_approved": enabled(env.get(AWS_OPTION_A_LIVE_REHEARSAL_OWNER_APPROVED_FLAG)),
        "rds_write_enabled": enabled(env.get(AWS_OPTION_A_REHEARSAL_RDS_WRITE_ENABLED_FLAG)),
        "sqs_send_enabled": enabled(env.get(AWS_OPTION_A_REHEARSAL_SQS_SEND_ENABLED_FLAG)),
        "s3_write_enabled": enabled(env.get(AWS_OPTION_A_REHEARSAL_S3_WRITE_ENABLED_FLAG)),
        "cleanup_enabled": enabled(env.get(AWS_OPTION_A_REHEARSAL_CLEANUP_ENABLED_FLAG)),
        "sqs_only_mode": enabled(env.get(AWS_OPTION_A_REHEARSAL_ONLY_SQS_FLAG)),
    }


def blocking_reason(
    *,
    actor_role: str,
    flags: Mapping[str, Any],
    rollback_control: Mapping[str, Any],
) -> str:
    if clean_text(actor_role, 80).lower() not in {"admin", "owner"}:
        return "blocked_client_not_authorized"
    if rollback_control.get("aws_route_blocked_by_rollback"):
        return "blocked_by_rollback_control"
    if not flags.get("live_rehearsal_enabled"):
        return "blocked_rehearsal_not_enabled"
    if not flags.get("owner_approved"):
        return "blocked_owner_approval_required"
    return ""


def build_boto3_client(service: str, env: Mapping[str, Any]):
    boto3 = optional_dependency("boto3")
    if boto3 is None:
        return None, "blocked_missing_dependency_boto3"
    session = getattr(boto3, "Session")(region_name=clean_text(env.get("AWS_REGION")) or None)
    return getattr(session, "client")(service), ""


def run_rds_rehearsal(env: Mapping[str, Any], job_id: str, cleanup_enabled: bool) -> Dict[str, Any]:
    result = base_resource_result("rds")
    database_url = clean_text(env.get("DATABASE_URL"), 5000)
    result["database_url_reference"] = redacted_ref(database_url)
    if not database_url:
        result["status"] = "blocked_missing_database_url_no_secret_fetch"
        return redact_secret_values(result)
    psycopg = optional_dependency("psycopg")
    if psycopg is None:
        result["status"] = "blocked_missing_dependency_psycopg"
        return redact_secret_values(result)

    result.update({
        "status": "rds_rehearsal_started",
        "live_rehearsal_attempted": True,
        "network_call_attempted": True,
        "db_connection_attempted": True,
        "rds_write_attempted": True,
        "cleanup_requested": cleanup_enabled,
    })
    try:
        connect = getattr(psycopg, "connect")
        with connect(database_url, connect_timeout=5) as conn:
            with conn.cursor() as cur:
                execute = getattr(cur, "execute")
                fetchone = getattr(cur, "fetchone")
                execute(
                    "CREATE TEMP TABLE aws20_rehearsal (job_id text primary key, marker text, updated_at timestamptz DEFAULT now())"
                )
                execute(
                    "INSERT INTO aws20_rehearsal (job_id, marker) VALUES (%s, %s)",
                    (job_id, "aws20_rehearsal_non_customer"),
                )
                execute("SELECT marker FROM aws20_rehearsal WHERE job_id = %s", (job_id,))
                inserted = fetchone()
                execute("UPDATE aws20_rehearsal SET marker = %s WHERE job_id = %s", ("aws20_rehearsal_updated", job_id))
                execute("SELECT marker FROM aws20_rehearsal WHERE job_id = %s", (job_id,))
                updated = fetchone()
            getattr(conn, "rollback")()
        result.update({
            "status": "passed",
            "insert_read_passed": bool(inserted and inserted[0] == "aws20_rehearsal_non_customer"),
            "update_read_passed": bool(updated and updated[0] == "aws20_rehearsal_updated"),
            "transaction_rolled_back": True,
            "persistent_customer_data_touched": False,
        })
    except Exception as exc:
        result.update({
            "status": safe_exception_status(exc),
            "error": safe_exception_details(exc),
            "transaction_rolled_back": True,
        })
    return redact_secret_values(result)


def run_sqs_rehearsal(env: Mapping[str, Any], job_id: str) -> Dict[str, Any]:
    result = base_resource_result("sqs")
    queue_url = clean_text(env.get("AWS_MEDIA_QUEUE_URL"), 2000)
    result["queue_reference"] = redacted_ref(queue_url)
    body = {
        "job_id": job_id,
        "task_type": "aws20_rehearsal_non_customer",
        "workflow_type": "aws20_live_rehearsal",
        "non_executable": True,
        "do_not_process": True,
        "provider_call_allowed": False,
        "media_generation_allowed": False,
        "customer_id": "aws20_rehearsal_non_customer",
        "created_at": utc_now(),
    }
    body_text = json.dumps(body, sort_keys=True)
    result.update(build_sqs_diagnostic_fields(
        env=env,
        queue_url=queue_url,
        job_id=job_id,
        body_size=len(body_text.encode("utf-8")),
    ))
    if not queue_url:
        result["status"] = "blocked_missing_media_queue_url"
        result["sqs_error_category"] = "missing_queue_url"
        result["next_operator_action"] = sqs_next_operator_action("missing_queue_url")
        return redact_secret_values(result)
    try:
        sqs, blocked = build_boto3_client("sqs", env)
    except Exception as exc:
        category = categorize_sqs_failure(exc, queue_url=queue_url, region_present=bool(clean_text(env.get("AWS_REGION")) or clean_text(env.get("AWS_DEFAULT_REGION"))))
        result.update(build_sqs_diagnostic_fields(
            env=env,
            queue_url=queue_url,
            job_id=job_id,
            body_size=len(body_text.encode("utf-8")),
            exc=exc,
        ))
        result.update({
            "status": safe_exception_status(exc),
            "error": safe_exception_details(exc),
            "sqs_error_category": category,
            "next_operator_action": sqs_next_operator_action(category),
        })
        return redact_secret_values(result)
    if blocked:
        result["status"] = blocked
        category = (
            "missing_boto3_dependency"
            if blocked == "blocked_missing_dependency_boto3"
            else ("missing_region" if not result.get("sqs_region_present") else "unknown_sqs_error")
        )
        result["sqs_error_category"] = category
        result["next_operator_action"] = sqs_next_operator_action(category)
        return redact_secret_values(result)

    kwargs = {
        "QueueUrl": queue_url,
        "MessageBody": body_text,
        "MessageAttributes": {
            "aws20_rehearsal": {"StringValue": "true", "DataType": "String"},
            "non_executable": {"StringValue": "true", "DataType": "String"},
        },
    }
    if queue_url.lower().endswith(".fifo"):
        kwargs["MessageGroupId"] = "aws20-rehearsal"
        kwargs["MessageDeduplicationId"] = safe_hash(f"{job_id}:sqs", 32)

    result.update({
        "status": "sqs_rehearsal_started",
        "live_rehearsal_attempted": True,
        "network_call_attempted": True,
        "sqs_send_attempted": True,
        "message_marked_non_executable": True,
        "sqs_attempted": True,
    })
    try:
        response = getattr(sqs, "send_message")(**kwargs)
        result.update({
            "status": "passed",
            "message_id_hash": safe_hash(response.get("MessageId")),
            "md5_present": bool(response.get("MD5OfMessageBody")),
        })
        result.update(build_sqs_diagnostic_fields(
            env=env,
            queue_url=queue_url,
            job_id=job_id,
            body_size=len(body_text.encode("utf-8")),
            attempted=True,
            passed=True,
            message_id=response.get("MessageId"),
        ))
    except Exception as exc:
        category = categorize_sqs_failure(exc, queue_url=queue_url, region_present=bool(clean_text(env.get("AWS_REGION")) or clean_text(env.get("AWS_DEFAULT_REGION"))))
        result.update(build_sqs_diagnostic_fields(
            env=env,
            queue_url=queue_url,
            job_id=job_id,
            body_size=len(body_text.encode("utf-8")),
            attempted=True,
            passed=False,
            exc=exc,
        ))
        result.update({
            "status": safe_exception_status(exc),
            "error": safe_exception_details(exc),
            "sqs_error_category": category,
            "next_operator_action": sqs_next_operator_action(category),
        })
    return redact_secret_values(result)


def run_s3_rehearsal(env: Mapping[str, Any], job_id: str, cleanup_enabled: bool) -> Dict[str, Any]:
    result = base_resource_result("s3")
    bucket = clean_text(env.get("AWS_MEDIA_S3_BUCKET"), 1000)
    result["bucket_reference"] = redacted_ref(bucket)
    if not bucket:
        result["status"] = "blocked_missing_media_s3_bucket"
        return redact_secret_values(result)
    s3, blocked = build_boto3_client("s3", env)
    if blocked:
        result["status"] = blocked
        return redact_secret_values(result)

    key = f"aws20_rehearsal/non_customer/{job_id}.json"
    body = json.dumps({
        "job_id": job_id,
        "marker": "aws20_rehearsal_non_customer",
        "non_customer": True,
        "non_executable": True,
        "created_at": utc_now(),
    }, sort_keys=True).encode("utf-8")
    result.update({
        "status": "s3_rehearsal_started",
        "live_rehearsal_attempted": True,
        "network_call_attempted": True,
        "s3_upload_attempted": True,
        "cleanup_requested": cleanup_enabled,
        "object_key_hash": safe_hash(key),
    })
    try:
        getattr(s3, "put_object")(Bucket=bucket, Key=key, Body=body, ContentType="application/json")
        response = getattr(s3, "get_object")(Bucket=bucket, Key=key)
        read_body = getattr(response["Body"], "read")()
        result["read_back_passed"] = b"aws20_rehearsal_non_customer" in read_body
        if cleanup_enabled:
            getattr(s3, "delete_object")(Bucket=bucket, Key=key)
            result["s3_delete_attempted"] = True
            result["cleanup_performed"] = True
        else:
            result["cleanup_performed"] = False
        result["status"] = "passed" if result["read_back_passed"] else "failed_readback_marker_missing"
    except Exception as exc:
        result.update({"status": safe_exception_status(exc), "error": safe_exception_details(exc)})
    return redact_secret_values(result)


def skipped_resource(resource: str, status: str) -> Dict[str, Any]:
    return redact_secret_values(base_resource_result(resource, status))


def build_aws20_live_rehearsal(
    *,
    env: Optional[Mapping[str, Any]] = None,
    actor_role: str = "admin",
    payload: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    env = dict(env or {})
    payload = dict(payload or {})
    flags = rehearsal_flags(env)
    job_id = clean_text(payload.get("job_id") or synthetic_rehearsal_job_id(), 180)
    rollback_control = build_aws_option_a_rollback_control_decision(
        env=env,
        route_kind="aws20_live_rehearsal",
        route_intent=True,
        route_execution_allowed=True,
        selected_runtime_path="aws20_live_rehearsal_helper_path",
        route_mode="aws20_live_rehearsal",
    )
    block = blocking_reason(actor_role=actor_role, flags=flags, rollback_control=rollback_control)
    resource_results: Dict[str, Dict[str, Any]] = {}

    if block:
        for resource in ("rds", "sqs", "s3"):
            resource_results[resource] = skipped_resource(resource, block)
    else:
        sqs_only_mode = bool(flags.get("sqs_only_mode"))
        resource_results["rds"] = (
            run_rds_rehearsal(env, job_id, bool(flags.get("cleanup_enabled")))
            if flags.get("rds_write_enabled") and not sqs_only_mode
            else skipped_resource("rds", "skipped_resource_flag_disabled")
        )
        resource_results["sqs"] = (
            run_sqs_rehearsal(env, job_id)
            if flags.get("sqs_send_enabled")
            else skipped_resource("sqs", "skipped_resource_flag_disabled")
        )
        resource_results["s3"] = (
            run_s3_rehearsal(env, job_id, bool(flags.get("cleanup_enabled")))
            if flags.get("s3_write_enabled") and not sqs_only_mode
            else skipped_resource("s3", "skipped_resource_flag_disabled")
        )

    live_attempted = any(item.get("live_rehearsal_attempted") for item in resource_results.values())
    result = {
        "boundary": "aws20_live_rehearsal_boundary",
        "diagnostic_version": REHEARSAL_DIAGNOSTIC_VERSION,
        "aws19_diagnostic_version": DIAGNOSTIC_VERSION,
        "status": "live_rehearsal_executed" if live_attempted else "safe_default_no_live_rehearsal",
        "blocked_reason": block,
        "actor_role": "admin" if clean_text(actor_role).lower() in {"admin", "owner"} else "client",
        "owner_admin_only": True,
        "client_trigger_allowed": False,
        "flags": flags,
        "rollback_control_active": bool(rollback_control.get("rollback_control_active")),
        "kill_switch_active": bool(rollback_control.get("kill_switch_active")),
        "force_compatibility_fallback": bool(rollback_control.get("force_compatibility_fallback")),
        "aws_route_blocked_by_rollback": bool(rollback_control.get("aws_route_blocked_by_rollback")),
        "rehearsal_job_reference_hash": safe_hash(job_id),
        "rehearsal_artifact_marker": "aws20_rehearsal/test/non_customer",
        "synthetic_non_customer_job": True,
        "resource_results": resource_results,
        "admin_safe_summary": {
            "rds_status": resource_results["rds"].get("status"),
            "sqs_status": resource_results["sqs"].get("status"),
            "s3_status": resource_results["s3"].get("status"),
            "sqs_error_category": resource_results["sqs"].get("sqs_error_category"),
            "sqs_next_operator_action": resource_results["sqs"].get("next_operator_action"),
            "sqs_queue_url_hash_prefix": resource_results["sqs"].get("sqs_queue_url_hash_prefix"),
            "live_rehearsal_attempted": live_attempted,
            "cleanup_enabled": bool(flags.get("cleanup_enabled")),
            "sqs_only_mode": bool(flags.get("sqs_only_mode")),
            "blocked_reason": block,
            "rehearsal_job_reference_hash": safe_hash(job_id),
        },
        "client_safe_view": {
            "status": "current_runtime_active",
            "message": "Support can review this request if needed.",
            "customer_safe": True,
            "internal_config_exposed": False,
            "sensitive_values_exposed": False,
        },
        "incident_event": {
            "event_type": "aws20_live_rehearsal_boundary_prepared",
            "severity": "info" if live_attempted else "notice",
            "decision": "live_rehearsal_executed" if live_attempted else block or "resource_flags_disabled",
            "safe_job_reference_hash": safe_hash(job_id),
            "timestamp": utc_now(),
            "diagnostic_version": REHEARSAL_DIAGNOSTIC_VERSION,
            "external_logging_attempted": False,
            "cloudwatch_put_attempted": False,
        },
        "provider_call_attempted": False,
        "stripe_call_attempted": False,
        "billing_mutation_attempted": False,
        "credit_mutation_attempted": False,
        "media_worker_started": False,
        "secret_fetch_attempted": False,
        "secrets_manager_value_retrieved": False,
        "live_routes_switched": False,
        "public_production_cutover_enabled": False,
        "customer_safe": True,
        "credential_values_exposed": False,
        "provider_secret_values_visible": False,
    }
    result["rds_write_attempted"] = bool(resource_results["rds"].get("rds_write_attempted"))
    result["db_connection_attempted"] = bool(resource_results["rds"].get("db_connection_attempted"))
    result["sqs_send_attempted"] = bool(resource_results["sqs"].get("sqs_send_attempted"))
    result["s3_upload_attempted"] = bool(resource_results["s3"].get("s3_upload_attempted"))
    result["network_call_attempted"] = any(item.get("network_call_attempted") for item in resource_results.values())
    return redact_secret_values(result)
