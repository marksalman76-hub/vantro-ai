from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Iterable, Mapping
import hashlib
import importlib
import json
import os
import re
import uuid


LIVE_VALIDATION_FLAG = "AWS_OPTION_A_LIVE_VALIDATION"
FAIL_ON_ERROR_FLAG = "AWS_OPTION_A_LIVE_VALIDATION_FAIL_ON_ERROR"

SERVICE_FLAGS = {
    "iam": "AWS_OPTION_A_VALIDATE_IAM",
    "rds": "AWS_OPTION_A_VALIDATE_RDS",
    "sqs": "AWS_OPTION_A_VALIDATE_SQS",
    "s3": "AWS_OPTION_A_VALIDATE_S3",
    "secrets": "AWS_OPTION_A_VALIDATE_SECRETS",
}

OPTIONAL_MUTATION_FLAGS = {
    "sqs_test_message": "AWS_OPTION_A_VALIDATE_SQS_TEST_MESSAGE",
    "s3_test_object": "AWS_OPTION_A_VALIDATE_S3_TEST_OBJECT",
    "secret_value": "AWS_OPTION_A_VALIDATE_SECRET_VALUE",
}

REQUIRED_ENV_BY_SERVICE = {
    "iam": ("AWS_REGION",),
    "rds": ("DATABASE_URL or AWS_RDS_SECRET_ARN",),
    "sqs": ("AWS_MEDIA_QUEUE_URL", "AWS_MEDIA_DLQ_URL"),
    "s3": ("AWS_MEDIA_S3_BUCKET", "AWS_UPLOADS_S3_BUCKET"),
    "secrets": ("AWS_PROVIDER_SECRETS_PREFIX or AWS_OPTION_A_VALIDATE_SECRET_IDS",),
}

TRUE_VALUES = {"1", "true", "yes", "on", "enabled"}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def enabled(value: Any) -> bool:
    return str(value or "").strip().lower() in TRUE_VALUES


def clean_text(value: Any, limit: int = 1000) -> str:
    return str(value or "").strip()[:limit]


def safe_hash(value: Any, length: int = 12) -> str:
    text = clean_text(value, 5000)
    if not text:
        return ""
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()[:length]


def redacted_ref(value: Any) -> Dict[str, Any]:
    text = clean_text(value, 5000)
    return {
        "present": bool(text),
        "redacted": True,
        "length": len(text),
        "sha256_12": safe_hash(text),
    }


def parse_csv_env(env: Mapping[str, Any], key: str) -> list[str]:
    raw = clean_text(env.get(key), 5000)
    if not raw:
        return []
    return [item.strip() for item in raw.split(",") if item.strip()]


def optional_dependency(module_name: str):
    try:
        return importlib.import_module(module_name)
    except ModuleNotFoundError:
        return None


def safe_error_message(value: Any, limit: int = 500) -> str:
    text = clean_text(value, limit)
    if not text:
        return ""
    lower = text.lower()
    sensitive_markers = (
        "aws_access_key_id",
        "aws_secret_access_key",
        "aws_session_token",
        "secret access key",
        "session token",
        "secretstring",
        "secretbinary",
        "password",
    )
    if any(marker in lower for marker in sensitive_markers):
        return "AWS credential/configuration error; sensitive details redacted."
    text = re.sub(r"\b(AKIA|ASIA)[A-Z0-9]{16}\b", "[redacted_aws_access_key]", text)
    text = re.sub(r"\b\d{12}\b", "[redacted_aws_account_id]", text)
    text = re.sub(r"arn:aws:[A-Za-z0-9_./:=+\-@]+", "[redacted_aws_arn]", text)
    return text


def aws_exception_status(exc: BaseException) -> str:
    botocore_exceptions = optional_dependency("botocore.exceptions")
    if botocore_exceptions is not None:
        credential_types = tuple(
            exception_type
            for name in (
                "NoCredentialsError",
                "PartialCredentialsError",
                "CredentialRetrievalError",
                "SSOTokenLoadError",
                "TokenRetrievalError",
            )
            if isinstance((exception_type := getattr(botocore_exceptions, name, None)), type)
        )
        config_types = tuple(
            exception_type
            for name in (
                "NoRegionError",
                "ProfileNotFound",
                "ConfigNotFound",
                "InvalidConfigError",
                "ConfigParseError",
            )
            if isinstance((exception_type := getattr(botocore_exceptions, name, None)), type)
        )
        if credential_types and isinstance(exc, credential_types):
            return "blocked_missing_aws_credentials"
        if config_types and isinstance(exc, config_types):
            return "blocked_aws_config_error"

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
    } or "profile" in message and "not found" in message:
        return "blocked_aws_config_error"
    return "aws_client_error"


def safe_exception_details(exc: BaseException) -> Dict[str, Any]:
    return {
        "error_type": clean_text(exc.__class__.__name__, 120),
        "safe_error_summary": safe_error_message(str(exc)),
        "credential_values_exposed": False,
        "secret_values_exposed": False,
    }


def apply_safe_aws_exception(result: Dict[str, Any], exc: BaseException) -> Dict[str, Any]:
    result.update({
        "status": aws_exception_status(exc),
        "error": safe_exception_details(exc),
        "secrets_exposed": False,
        "secret_value_printed": False,
        "credential_values_exposed": False,
    })
    return result


def base_service_result(service: str, action: str, cost_risk: str = "none") -> Dict[str, Any]:
    return {
        "service": service,
        "action": action,
        "status": "skipped",
        "cost_risk": cost_risk,
        "touches_production_data": False,
        "rollback_or_cleanup": "none_needed",
        "expected_pass_signal": "service-specific readiness metadata returned",
        "secrets_exposed": False,
        "cleanup_performed": False,
        "network_call_attempted": False,
        "db_connection_attempted": False,
        "migration_attempted": False,
        "sqs_send_attempted": False,
        "s3_upload_attempted": False,
        "secret_value_printed": False,
        "aws_call_attempted": False,
    }


def live_service_requested(env: Mapping[str, Any], service: str) -> bool:
    return enabled(env.get(LIVE_VALIDATION_FLAG)) and enabled(env.get(SERVICE_FLAGS[service]))


def validate_iam(env: Mapping[str, Any]) -> Dict[str, Any]:
    result = base_service_result("iam", "sts.get_caller_identity", cost_risk="none")
    if not live_service_requested(env, "iam"):
        result["status"] = "skipped_not_enabled"
        return result

    boto3 = optional_dependency("boto3")
    if boto3 is None:
        result["status"] = "blocked_missing_dependency_boto3"
        return result

    result["network_call_attempted"] = True
    result["aws_call_attempted"] = True
    try:
        session = boto3.Session(region_name=clean_text(env.get("AWS_REGION")) or None)
        response = session.client("sts").get_caller_identity()
        result.update({
            "status": "passed",
            "account": redacted_ref(response.get("Account")),
            "arn": redacted_ref(response.get("Arn")),
            "user_id": redacted_ref(response.get("UserId")),
        })
    except Exception as exc:
        apply_safe_aws_exception(result, exc)
    return result


def validate_rds(env: Mapping[str, Any]) -> Dict[str, Any]:
    result = base_service_result("rds", "connect and SELECT 1 readiness check", cost_risk="low")
    if not live_service_requested(env, "rds"):
        result["status"] = "skipped_not_enabled"
        return result

    database_url = clean_text(env.get("DATABASE_URL"), 5000)
    if not database_url:
        result["status"] = "blocked_missing_database_url_no_connection_attempted"
        result["database_url"] = redacted_ref(database_url)
        return result

    psycopg = optional_dependency("psycopg")
    if psycopg is None:
        result["status"] = "blocked_missing_dependency_psycopg"
        return result

    result["network_call_attempted"] = True
    result["db_connection_attempted"] = True
    result["aws_call_attempted"] = False
    try:
        with psycopg.connect(database_url, connect_timeout=5) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                row = cur.fetchone()
        result.update({
            "status": "passed" if row and row[0] == 1 else "failed_unexpected_select_result",
            "migration_attempted": False,
            "write_attempted": False,
            "database_url": redacted_ref(database_url),
        })
    except Exception as exc:
        apply_safe_aws_exception(result, exc)
        result["database_url"] = redacted_ref(database_url)
    return result


def validate_sqs(env: Mapping[str, Any]) -> Dict[str, Any]:
    result = base_service_result("sqs", "get queue and DLQ attributes", cost_risk="low")
    if not live_service_requested(env, "sqs"):
        result["status"] = "skipped_not_enabled"
        return result

    boto3 = optional_dependency("boto3")
    if boto3 is None:
        result["status"] = "blocked_missing_dependency_boto3"
        return result

    queue_url = clean_text(env.get("AWS_MEDIA_QUEUE_URL"), 1000)
    dlq_url = clean_text(env.get("AWS_MEDIA_DLQ_URL"), 1000)
    if not queue_url or not dlq_url:
        result["status"] = "blocked_missing_queue_or_dlq_url"
        result["queue_url"] = redacted_ref(queue_url)
        result["dlq_url"] = redacted_ref(dlq_url)
        return result

    result["network_call_attempted"] = True
    result["aws_call_attempted"] = True
    try:
        sqs = boto3.Session(region_name=clean_text(env.get("AWS_REGION")) or None).client("sqs")
        queue_attrs = sqs.get_queue_attributes(QueueUrl=queue_url, AttributeNames=["QueueArn", "ApproximateNumberOfMessages"])
        dlq_attrs = sqs.get_queue_attributes(QueueUrl=dlq_url, AttributeNames=["QueueArn", "ApproximateNumberOfMessages"])
        result.update({
            "status": "passed",
            "queue_url": redacted_ref(queue_url),
            "dlq_url": redacted_ref(dlq_url),
            "queue_arn": redacted_ref(queue_attrs.get("Attributes", {}).get("QueueArn")),
            "dlq_arn": redacted_ref(dlq_attrs.get("Attributes", {}).get("QueueArn")),
        })

        if enabled(env.get(OPTIONAL_MUTATION_FLAGS["sqs_test_message"])):
            marker = f"aws-option-a-validation-{uuid.uuid4().hex}"
            result["sqs_send_attempted"] = True
            result["touches_production_data"] = True
            result["rollback_or_cleanup"] = "delete validation message after receive"
            sent = sqs.send_message(QueueUrl=queue_url, MessageBody=marker, MessageAttributes={
                "validation": {"DataType": "String", "StringValue": "aws-option-a"}
            })
            received = sqs.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=1, WaitTimeSeconds=1)
            deleted = False
            for message in received.get("Messages", []):
                if message.get("Body") == marker:
                    sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=message["ReceiptHandle"])
                    deleted = True
                    break
            result["test_message"] = {
                "message_id": redacted_ref(sent.get("MessageId")),
                "cleanup_performed": deleted,
            }
            result["cleanup_performed"] = deleted
    except Exception as exc:
        apply_safe_aws_exception(result, exc)
        result["queue_url"] = redacted_ref(queue_url)
        result["dlq_url"] = redacted_ref(dlq_url)
    return result


def validate_s3(env: Mapping[str, Any]) -> Dict[str, Any]:
    result = base_service_result("s3", "head bucket readiness", cost_risk="low")
    if not live_service_requested(env, "s3"):
        result["status"] = "skipped_not_enabled"
        return result

    boto3 = optional_dependency("boto3")
    if boto3 is None:
        result["status"] = "blocked_missing_dependency_boto3"
        return result

    media_bucket = clean_text(env.get("AWS_MEDIA_S3_BUCKET"), 240)
    uploads_bucket = clean_text(env.get("AWS_UPLOADS_S3_BUCKET"), 240)
    if not media_bucket or not uploads_bucket:
        result["status"] = "blocked_missing_s3_bucket"
        result["media_bucket"] = redacted_ref(media_bucket)
        result["uploads_bucket"] = redacted_ref(uploads_bucket)
        return result

    result["network_call_attempted"] = True
    result["aws_call_attempted"] = True
    try:
        s3 = boto3.Session(region_name=clean_text(env.get("AWS_REGION")) or None).client("s3")
        s3.head_bucket(Bucket=media_bucket)
        s3.head_bucket(Bucket=uploads_bucket)
        result.update({
            "status": "passed",
            "media_bucket": redacted_ref(media_bucket),
            "uploads_bucket": redacted_ref(uploads_bucket),
        })

        if enabled(env.get(OPTIONAL_MUTATION_FLAGS["s3_test_object"])):
            key = f"_validation/aws-option-a-live-validation-{uuid.uuid4().hex}.txt"
            body = b"aws-option-a-validation"
            result["s3_upload_attempted"] = True
            result["touches_production_data"] = True
            result["rollback_or_cleanup"] = "delete validation object"
            s3.put_object(Bucket=media_bucket, Key=key, Body=body, ContentType="text/plain")
            fetched = s3.get_object(Bucket=media_bucket, Key=key)
            fetched_body = fetched["Body"].read()
            s3.delete_object(Bucket=media_bucket, Key=key)
            result["test_object"] = {
                "key": redacted_ref(key),
                "bytes_written": len(body),
                "bytes_read": len(fetched_body),
                "cleanup_performed": True,
            }
            result["cleanup_performed"] = True
    except Exception as exc:
        apply_safe_aws_exception(result, exc)
        result["media_bucket"] = redacted_ref(media_bucket)
        result["uploads_bucket"] = redacted_ref(uploads_bucket)
    return result


def validate_secrets(env: Mapping[str, Any]) -> Dict[str, Any]:
    result = base_service_result("secrets_manager", "describe secret metadata only", cost_risk="low")
    if not live_service_requested(env, "secrets"):
        result["status"] = "skipped_not_enabled"
        return result

    boto3 = optional_dependency("boto3")
    if boto3 is None:
        result["status"] = "blocked_missing_dependency_boto3"
        return result

    secret_ids = parse_csv_env(env, "AWS_OPTION_A_VALIDATE_SECRET_IDS")
    if not secret_ids:
        result["status"] = "blocked_no_secret_ids_configured"
        result["safe_next_step"] = "Set AWS_OPTION_A_VALIDATE_SECRET_IDS to comma-separated test secret names/ARNs."
        return result

    result["network_call_attempted"] = True
    result["aws_call_attempted"] = True
    try:
        client = boto3.Session(region_name=clean_text(env.get("AWS_REGION")) or None).client("secretsmanager")
        described = []
        for secret_id in secret_ids:
            metadata = client.describe_secret(SecretId=secret_id)
            item = {
                "secret_id": redacted_ref(secret_id),
                "arn": redacted_ref(metadata.get("ARN")),
                "name": redacted_ref(metadata.get("Name")),
                "last_changed_date_present": bool(metadata.get("LastChangedDate")),
            }
            if enabled(env.get(OPTIONAL_MUTATION_FLAGS["secret_value"])):
                result["secret_fetch_attempted"] = True
                secret_value = client.get_secret_value(SecretId=secret_id)
                value = secret_value.get("SecretString") or secret_value.get("SecretBinary") or b""
                if isinstance(value, bytes):
                    value_bytes = value
                else:
                    value_bytes = str(value).encode("utf-8", errors="ignore")
                item["secret_value"] = {
                    "present": bool(value_bytes),
                    "length": len(value_bytes),
                    "sha256_12": hashlib.sha256(value_bytes).hexdigest()[:12],
                    "value_printed": False,
                }
            described.append(item)
        result.update({
            "status": "passed",
            "secret_value_printed": False,
            "described_secrets": described,
        })
    except Exception as exc:
        apply_safe_aws_exception(result, exc)
        result["described_secrets"] = [{"secret_id": redacted_ref(secret_id)} for secret_id in secret_ids]
    return result


def build_default_blocked_result(env: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "status": "skipped_live_validation_not_enabled",
        "live_validation_enabled": False,
        "network_call_attempted": False,
        "credentials_required": False,
        "secrets_exposed": False,
        "required_live_flag": LIVE_VALIDATION_FLAG,
        "service_flags": dict(SERVICE_FLAGS),
        "optional_mutation_flags": dict(OPTIONAL_MUTATION_FLAGS),
        "required_environment": dict(REQUIRED_ENV_BY_SERVICE),
        "safe_next_steps": [
            "Set AWS_OPTION_A_LIVE_VALIDATION=true only when intentionally validating AWS test resources.",
            "Enable one service flag at a time, such as AWS_OPTION_A_VALIDATE_IAM=true.",
            "Use test buckets, test queues, test secrets, and read-only checks before optional reversible test writes.",
            "Keep Stripe, provider APIs, production migrations, route cutover, and customer credit mutations out of this validation.",
        ],
        "checked_at": utc_now(),
        "customer_safe": True,
        "credential_values_exposed": False,
    }


def run_validation(env: Mapping[str, Any] | None = None) -> Dict[str, Any]:
    env = dict(env or os.environ)
    live_enabled = enabled(env.get(LIVE_VALIDATION_FLAG))
    if not live_enabled:
        return build_default_blocked_result(env)

    service_results = {}
    validators = {
        "iam": validate_iam,
        "rds": validate_rds,
        "sqs": validate_sqs,
        "s3": validate_s3,
        "secrets": validate_secrets,
    }
    for service, validator in validators.items():
        try:
            service_results[service] = validator(env)
        except Exception as exc:
            result = base_service_result(service, "validator failed before service result could complete")
            service_results[service] = apply_safe_aws_exception(result, exc)

    failures = {
        service: result
        for service, result in service_results.items()
        if result.get("status", "").startswith(("failed", "blocked"))
    }
    return {
        "status": "completed_with_failures" if failures else "completed",
        "live_validation_enabled": True,
        "service_results": service_results,
        "failed_or_blocked_services": sorted(failures.keys()),
        "secrets_exposed": False,
        "secret_values_printed": False,
        "cost_risk": "low",
        "production_migration_attempted": False,
        "route_cutover_attempted": False,
        "provider_calls_attempted": False,
        "stripe_mutation_attempted": False,
        "credit_mutation_attempted": False,
        "checked_at": utc_now(),
        "customer_safe": True,
        "credential_values_exposed": False,
    }


def main() -> int:
    try:
        result = run_validation(os.environ)
    except Exception as exc:
        result = {
            "status": "aws_client_error",
            "live_validation_enabled": enabled(os.environ.get(LIVE_VALIDATION_FLAG)),
            "error": safe_exception_details(exc),
            "secrets_exposed": False,
            "secret_values_printed": False,
            "credential_values_exposed": False,
            "checked_at": utc_now(),
            "customer_safe": True,
        }
    print(json.dumps(result, indent=2, sort_keys=True, default=str))
    if enabled(os.environ.get(FAIL_ON_ERROR_FLAG)) and result.get("status") == "completed_with_failures":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
