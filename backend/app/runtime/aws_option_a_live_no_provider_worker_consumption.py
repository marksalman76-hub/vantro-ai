from __future__ import annotations

from datetime import datetime, timezone
import json
from typing import Any, Dict, Mapping, Optional
import uuid

from backend.app.runtime.aws_option_a_live_rehearsal import (
    build_boto3_client,
    build_sqs_diagnostic_fields,
    categorize_sqs_failure,
    clean_text,
    enabled,
    optional_dependency,
    redacted_ref,
    redact_secret_values,
    safe_exception_details,
    safe_exception_status,
    safe_hash,
    sqs_next_operator_action,
)
from backend.app.runtime.aws_option_a_rollback_controls import (
    AWS_OPTION_A_KILL_SWITCH_ENABLED_FLAG,
    build_aws_option_a_rollback_control_decision,
)


AWS_OPTION_A_LIVE_WORKER_CONSUMPTION_ENABLED_FLAG = "AWS_OPTION_A_LIVE_WORKER_CONSUMPTION_ENABLED"
AWS_OPTION_A_LIVE_WORKER_CONSUMPTION_OWNER_APPROVED_FLAG = "AWS_OPTION_A_LIVE_WORKER_CONSUMPTION_OWNER_APPROVED"
AWS_OPTION_A_LIVE_WORKER_VALIDATION_CONFIRMED_FLAG = "AWS_OPTION_A_LIVE_WORKER_VALIDATION_CONFIRMED"
AWS_OPTION_A_LIVE_WORKER_QUEUE_RECEIVE_ENABLED_FLAG = "AWS_OPTION_A_LIVE_WORKER_QUEUE_RECEIVE_ENABLED"
AWS_OPTION_A_LIVE_WORKER_QUEUE_DELETE_ENABLED_FLAG = "AWS_OPTION_A_LIVE_WORKER_QUEUE_DELETE_ENABLED"
AWS_OPTION_A_LIVE_WORKER_DURABLE_STATUS_ENABLED_FLAG = "AWS_OPTION_A_LIVE_WORKER_DURABLE_STATUS_ENABLED"
AWS_OPTION_A_LIVE_WORKER_CLEANUP_ENABLED_FLAG = "AWS_OPTION_A_LIVE_WORKER_CLEANUP_ENABLED"
AWS_OPTION_A_LIVE_WORKER_LOAD_LOCAL_ENV_FLAG = "AWS_OPTION_A_LIVE_WORKER_LOAD_LOCAL_ENV"

LIVE_WORKER_DIAGNOSTIC_VERSION = "aws_live_no_provider_worker_consumption_v1"
LIVE_WORKER_JOB_PREFIX = "aws_live_worker_non_customer"
LIVE_WORKER_TABLE = "aws20_live_worker_consumption_proof"
LIVE_WORKER_MARKER = "aws20_live_worker_consumption_non_customer"

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


def synthetic_worker_job_id() -> str:
    return f"{LIVE_WORKER_JOB_PREFIX}_{uuid.uuid4().hex[:12]}"


def live_worker_flags(env: Mapping[str, Any]) -> Dict[str, bool]:
    return {
        "live_worker_consumption_enabled": enabled(env.get(AWS_OPTION_A_LIVE_WORKER_CONSUMPTION_ENABLED_FLAG)),
        "owner_approved": enabled(env.get(AWS_OPTION_A_LIVE_WORKER_CONSUMPTION_OWNER_APPROVED_FLAG)),
        "validation_confirmed": enabled(env.get(AWS_OPTION_A_LIVE_WORKER_VALIDATION_CONFIRMED_FLAG)),
        "queue_receive_enabled": enabled(env.get(AWS_OPTION_A_LIVE_WORKER_QUEUE_RECEIVE_ENABLED_FLAG)),
        "queue_delete_enabled": enabled(env.get(AWS_OPTION_A_LIVE_WORKER_QUEUE_DELETE_ENABLED_FLAG)),
        "durable_status_enabled": enabled(env.get(AWS_OPTION_A_LIVE_WORKER_DURABLE_STATUS_ENABLED_FLAG)),
        "cleanup_enabled": enabled(env.get(AWS_OPTION_A_LIVE_WORKER_CLEANUP_ENABLED_FLAG)),
    }


def forbidden_live_execution_flags(env: Mapping[str, Any]) -> list[str]:
    return [flag for flag in FORBIDDEN_LIVE_EXECUTION_FLAGS if enabled(env.get(flag))]


def base_side_effect_guards() -> Dict[str, bool]:
    return {
        "live_worker_loop_started": False,
        "worker_loop_started": False,
        "provider_call_attempted": False,
        "paid_provider_calls_started": False,
        "media_generation_attempted": False,
        "ffmpeg_invoked": False,
        "stripe_call_attempted": False,
        "billing_mutation_attempted": False,
        "credit_mutation_attempted": False,
        "customer_traffic_attempted": False,
        "public_cutover_enabled": False,
        "public_production_cutover_enabled": False,
        "secret_fetch_attempted": False,
        "secrets_manager_value_retrieved": False,
    }


def rollback_controls_block_when_enabled(env: Mapping[str, Any]) -> bool:
    rollback_env = dict(env)
    rollback_env[AWS_OPTION_A_KILL_SWITCH_ENABLED_FLAG] = "true"
    decision = build_aws_option_a_rollback_control_decision(
        env=rollback_env,
        route_kind="live_no_provider_worker_consumption",
        route_intent=True,
        route_execution_allowed=True,
        selected_runtime_path="aws_option_a_live_no_provider_worker_consumption_boundary",
        route_mode="live_no_provider_worker_consumption_proof",
    )
    return bool(decision.get("aws_route_blocked_by_rollback"))


def rollback_active(env: Mapping[str, Any]) -> bool:
    decision = build_aws_option_a_rollback_control_decision(
        env=env,
        route_kind="live_no_provider_worker_consumption",
        route_intent=True,
        route_execution_allowed=True,
        selected_runtime_path="aws_option_a_live_no_provider_worker_consumption_boundary",
        route_mode="live_no_provider_worker_consumption_proof",
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
    if not flags.get("live_worker_consumption_enabled"):
        return "blocked_live_worker_consumption_not_enabled"
    if not flags.get("owner_approved"):
        return "blocked_owner_approval_required"
    if not flags.get("validation_confirmed"):
        return "blocked_validation_confirmation_required"
    if not flags.get("queue_receive_enabled"):
        return "blocked_queue_receive_flag_required"
    if not flags.get("queue_delete_enabled"):
        return "blocked_queue_delete_flag_required"
    if not flags.get("durable_status_enabled"):
        return "blocked_durable_status_flag_required"
    if not flags.get("cleanup_enabled"):
        return "blocked_cleanup_required"
    return ""


def empty_queue_result(status: str = "skipped_not_enabled") -> Dict[str, Any]:
    return {
        "resource": "sqs_worker_receive_delete",
        "status": status,
        "synthetic_queue_message_received": False,
        "queue_message_non_customer": False,
        "queue_message_non_executable": False,
        "queue_message_delete_or_ack_attempted": False,
        "queue_message_delete_or_ack_passed": False,
        "sqs_receive_attempted": False,
        "sqs_delete_attempted": False,
        "customer_queue_message_consumed": False,
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def empty_status_result(status: str = "skipped_not_enabled") -> Dict[str, Any]:
    return {
        "resource": "rds_synthetic_worker_status",
        "status": status,
        "durable_job_claim_once_passed": False,
        "duplicate_claim_blocked": False,
        "processing_status_passed": False,
        "terminal_status_passed": False,
        "live_durable_status_attempted": False,
        "db_connection_attempted": False,
        "rds_write_attempted": False,
        "cleanup_attempted": False,
        "cleanup_performed": False,
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def parse_message_body(body: Any) -> Dict[str, Any]:
    text = clean_text(body, 20000)
    if not text:
        return {}
    try:
        parsed = json.loads(text)
    except Exception:
        return {"raw_body_hash": safe_hash(text), "body_json_valid": False}
    return parsed if isinstance(parsed, dict) else {"body_json_valid": False, "body_hash": safe_hash(text)}


def message_attribute_bool(attributes: Mapping[str, Any], key: str) -> bool:
    item = attributes.get(key)
    if not isinstance(item, Mapping):
        return False
    return enabled(item.get("StringValue") or item.get("BinaryValue"))


def queue_message_is_non_customer(body: Mapping[str, Any], attributes: Mapping[str, Any]) -> bool:
    return bool(
        body.get("non_customer") is True
        or body.get("synthetic_non_customer_job") is True
        or body.get("customer_id") == "synthetic_non_customer"
        or body.get("tenant_id") == "synthetic_non_customer_tenant"
        or message_attribute_bool(attributes, "non_customer")
    )


def queue_message_is_non_executable(body: Mapping[str, Any], attributes: Mapping[str, Any]) -> bool:
    return bool(
        body.get("non_executable") is True
        or body.get("do_not_process") is True
        or body.get("worker_execution_allowed") is False
        or body.get("provider_call_allowed") is False
        or message_attribute_bool(attributes, "non_executable")
        or message_attribute_bool(attributes, "do_not_process")
    )


def safe_queue_job_hash(body: Mapping[str, Any], fallback_job_id: str) -> str:
    for key in ("job_reference_hash", "job_id", "parent_job_id", "id"):
        value = clean_text(body.get(key), 240)
        if value:
            return value if "hash" in key else safe_hash(value)
    return safe_hash(fallback_job_id)


def receive_synthetic_queue_message(env: Mapping[str, Any], job_id: str) -> Dict[str, Any]:
    result = empty_queue_result()
    queue_url = clean_text(env.get("AWS_OPTION_A_LIVE_WORKER_QUEUE_URL") or env.get("AWS_MEDIA_QUEUE_URL"), 2000)
    result["queue_reference"] = redacted_ref(queue_url)
    result.update(build_sqs_diagnostic_fields(
        env=env,
        queue_url=queue_url,
        job_id=job_id,
        attempted=False,
        passed=False,
    ))
    if not queue_url:
        result["status"] = "blocked_missing_worker_queue_url"
        result["sqs_error_category"] = "missing_queue_url"
        result["next_operator_action"] = sqs_next_operator_action("missing_queue_url")
        return redact_secret_values(result)
    try:
        sqs, blocked = build_boto3_client("sqs", env)
    except Exception as exc:
        category = categorize_sqs_failure(
            exc,
            queue_url=queue_url,
            region_present=bool(clean_text(env.get("AWS_REGION")) or clean_text(env.get("AWS_DEFAULT_REGION"))),
        )
        result.update(build_sqs_diagnostic_fields(env=env, queue_url=queue_url, job_id=job_id, attempted=True, exc=exc))
        result.update({
            "status": safe_exception_status(exc),
            "error": safe_exception_details(exc),
            "sqs_error_category": category,
            "next_operator_action": sqs_next_operator_action(category),
        })
        return redact_secret_values(result)
    if blocked:
        result["status"] = blocked
        category = "missing_boto3_dependency" if blocked == "blocked_missing_dependency_boto3" else "unknown_sqs_error"
        result["sqs_error_category"] = category
        result["next_operator_action"] = sqs_next_operator_action(category)
        return redact_secret_values(result)

    result.update({
        "status": "live_queue_receive_started",
        "sqs_receive_attempted": True,
    })
    try:
        response = getattr(sqs, "receive_message")(
            QueueUrl=queue_url,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=1,
            VisibilityTimeout=0,
            MessageAttributeNames=["All"],
            AttributeNames=["All"],
        )
        messages = response.get("Messages") or []
        if not messages:
            result.update({
                "status": "no_synthetic_queue_message_available",
                "next_operator_action": "Send one synthetic non-customer non-executable handoff message, then rerun this worker proof.",
            })
            return redact_secret_values(result)
        message = messages[0]
        body = parse_message_body(message.get("Body"))
        attributes = message.get("MessageAttributes") if isinstance(message.get("MessageAttributes"), dict) else {}
        non_customer = queue_message_is_non_customer(body, attributes)
        non_executable = queue_message_is_non_executable(body, attributes)
        result.update(build_sqs_diagnostic_fields(
            env=env,
            queue_url=queue_url,
            job_id=job_id,
            body_size=len(clean_text(message.get("Body"), 20000).encode("utf-8")),
            attempted=True,
            passed=bool(non_customer and non_executable),
            message_id=message.get("MessageId"),
        ))
        result.update({
            "status": "synthetic_queue_message_received" if non_customer and non_executable else "blocked_unsafe_queue_message_received",
            "synthetic_queue_message_received": bool(non_customer and non_executable),
            "queue_message_non_customer": non_customer,
            "queue_message_non_executable": non_executable,
            "message_reference_hash": safe_hash(message.get("MessageId")),
            "receipt_handle_hash": safe_hash(message.get("ReceiptHandle")),
            "safe_queue_job_reference_hash": safe_queue_job_hash(body, job_id),
            "receipt_handle_present": bool(clean_text(message.get("ReceiptHandle"), 5000)),
            "raw_body_exposed": False,
            "raw_receipt_handle_exposed": False,
        })
        if not (non_customer and non_executable):
            result["next_operator_action"] = "Do not delete this message. Confirm the queue contains only synthetic worker proof messages before rerun."
            return redact_secret_values(result)
        result["_receipt_handle_for_internal_delete"] = message.get("ReceiptHandle")
        result["_queue_url_for_internal_delete"] = queue_url
    except Exception as exc:
        category = categorize_sqs_failure(
            exc,
            queue_url=queue_url,
            region_present=bool(clean_text(env.get("AWS_REGION")) or clean_text(env.get("AWS_DEFAULT_REGION"))),
        )
        result.update(build_sqs_diagnostic_fields(env=env, queue_url=queue_url, job_id=job_id, attempted=True, exc=exc))
        result.update({
            "status": safe_exception_status(exc),
            "error": safe_exception_details(exc),
            "sqs_error_category": category,
            "next_operator_action": sqs_next_operator_action(category),
        })
    if result.get("synthetic_queue_message_received"):
        return result
    return redact_secret_values(result)


def delete_received_queue_message(env: Mapping[str, Any], queue_result: Mapping[str, Any]) -> Dict[str, Any]:
    result = dict(queue_result)
    receipt_handle = queue_result.get("_receipt_handle_for_internal_delete")
    queue_url = queue_result.get("_queue_url_for_internal_delete")
    if not (queue_result.get("synthetic_queue_message_received") and receipt_handle and queue_url):
        result.pop("_receipt_handle_for_internal_delete", None)
        result.pop("_queue_url_for_internal_delete", None)
        return redact_secret_values(result)
    try:
        sqs, blocked = build_boto3_client("sqs", env)
    except Exception as exc:
        result.update({
            "status": safe_exception_status(exc),
            "delete_error": safe_exception_details(exc),
            "queue_message_delete_or_ack_attempted": True,
            "queue_message_delete_or_ack_passed": False,
        })
        result.pop("_receipt_handle_for_internal_delete", None)
        result.pop("_queue_url_for_internal_delete", None)
        return redact_secret_values(result)
    if blocked:
        result.update({
            "status": blocked,
            "queue_message_delete_or_ack_attempted": True,
            "queue_message_delete_or_ack_passed": False,
        })
        result.pop("_receipt_handle_for_internal_delete", None)
        result.pop("_queue_url_for_internal_delete", None)
        return redact_secret_values(result)
    try:
        result["queue_message_delete_or_ack_attempted"] = True
        result["sqs_delete_attempted"] = True
        getattr(sqs, "delete_message")(QueueUrl=queue_url, ReceiptHandle=receipt_handle)
        result["queue_message_delete_or_ack_passed"] = True
        result["status"] = "synthetic_queue_message_deleted_after_terminal_status"
    except Exception as exc:
        result.update({
            "status": safe_exception_status(exc),
            "delete_error": safe_exception_details(exc),
            "queue_message_delete_or_ack_passed": False,
        })
    result.pop("_receipt_handle_for_internal_delete", None)
    result.pop("_queue_url_for_internal_delete", None)
    return redact_secret_values(result)


def attempt_status_cleanup(database_url: str, job_id: str) -> Dict[str, Any]:
    cleanup = {
        "cleanup_attempted": True,
        "cleanup_performed": False,
        "job_reference_hash": safe_hash(job_id),
    }
    psycopg = optional_dependency("psycopg")
    if psycopg is None:
        cleanup["cleanup_error"] = {"status": "blocked_missing_dependency_psycopg"}
        return cleanup
    try:
        connect = getattr(psycopg, "connect")
        with connect(database_url, connect_timeout=5) as conn:
            with conn.cursor() as cur:
                execute = getattr(cur, "execute")
                fetchone = getattr(cur, "fetchone")
                execute(f"DELETE FROM {LIVE_WORKER_TABLE} WHERE job_id = %s", (job_id,))
                execute(f"SELECT COUNT(*) FROM {LIVE_WORKER_TABLE} WHERE job_id = %s", (job_id,))
                remaining = fetchone()
                execute(f"DROP TABLE IF EXISTS {LIVE_WORKER_TABLE}")
            getattr(conn, "commit")()
        cleanup["cleanup_performed"] = bool(remaining and int(remaining[0]) == 0)
    except Exception as exc:
        cleanup["cleanup_error"] = {
            "status": safe_exception_status(exc),
            "error": safe_exception_details(exc),
        }
    return redact_secret_values(cleanup)


def run_live_synthetic_status_claim(env: Mapping[str, Any], job_id: str, cleanup_enabled: bool) -> Dict[str, Any]:
    result = empty_status_result()
    database_url = clean_text(env.get("DATABASE_URL"), 5000)
    result["database_url_reference"] = redacted_ref(database_url)
    result["job_reference_hash"] = safe_hash(job_id)
    result["proof_table_hash"] = safe_hash(LIVE_WORKER_TABLE)
    if not database_url:
        result["status"] = "blocked_missing_database_url_no_secret_fetch"
        return redact_secret_values(result)
    if not cleanup_enabled:
        result["status"] = "blocked_cleanup_required"
        return redact_secret_values(result)
    psycopg = optional_dependency("psycopg")
    if psycopg is None:
        result["status"] = "blocked_missing_dependency_psycopg"
        return redact_secret_values(result)

    result.update({
        "status": "live_synthetic_status_claim_started",
        "live_durable_status_attempted": True,
        "db_connection_attempted": True,
        "rds_write_attempted": True,
        "cleanup_attempted": True,
    })
    try:
        connect = getattr(psycopg, "connect")
        with connect(database_url, connect_timeout=5) as conn:
            with conn.cursor() as cur:
                execute = getattr(cur, "execute")
                fetchone = getattr(cur, "fetchone")
                execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS {LIVE_WORKER_TABLE} (
                        job_id text primary key,
                        marker text not null,
                        internal_status text not null,
                        client_safe_status text not null,
                        claim_token_hash text,
                        synthetic_non_customer boolean not null,
                        non_executable boolean not null,
                        created_at timestamptz not null default now(),
                        updated_at timestamptz not null default now()
                    )
                    """
                )
                getattr(conn, "commit")()
                execute(
                    f"""
                    INSERT INTO {LIVE_WORKER_TABLE}
                        (job_id, marker, internal_status, client_safe_status, claim_token_hash, synthetic_non_customer, non_executable)
                    VALUES (%s, %s, %s, %s, NULL, %s, %s)
                    ON CONFLICT (job_id) DO UPDATE SET
                        marker = EXCLUDED.marker,
                        internal_status = EXCLUDED.internal_status,
                        client_safe_status = EXCLUDED.client_safe_status,
                        claim_token_hash = NULL,
                        synthetic_non_customer = EXCLUDED.synthetic_non_customer,
                        non_executable = EXCLUDED.non_executable,
                        updated_at = now()
                    """,
                    (job_id, LIVE_WORKER_MARKER, "queued", "queued", True, True),
                )
                getattr(conn, "commit")()
                claim_token_hash = safe_hash(f"{job_id}:claim:primary")
                execute(
                    f"""
                    UPDATE {LIVE_WORKER_TABLE}
                    SET internal_status = %s, client_safe_status = %s, claim_token_hash = %s, updated_at = now()
                    WHERE job_id = %s AND claim_token_hash IS NULL AND synthetic_non_customer = true AND non_executable = true
                    """,
                    ("claimed", "queued", claim_token_hash, job_id),
                )
                primary_claim_count = getattr(cur, "rowcount", 0)
                getattr(conn, "commit")()
                duplicate_claim_token_hash = safe_hash(f"{job_id}:claim:duplicate")
                execute(
                    f"""
                    UPDATE {LIVE_WORKER_TABLE}
                    SET claim_token_hash = %s, updated_at = now()
                    WHERE job_id = %s AND claim_token_hash IS NULL
                    """,
                    (duplicate_claim_token_hash, job_id),
                )
                duplicate_claim_count = getattr(cur, "rowcount", 0)
                execute(
                    f"""
                    UPDATE {LIVE_WORKER_TABLE}
                    SET internal_status = %s, client_safe_status = %s, updated_at = now()
                    WHERE job_id = %s AND claim_token_hash = %s
                    """,
                    ("processing", "running", job_id, claim_token_hash),
                )
                processing_count = getattr(cur, "rowcount", 0)
                execute(
                    f"""
                    UPDATE {LIVE_WORKER_TABLE}
                    SET internal_status = %s, client_safe_status = %s, updated_at = now()
                    WHERE job_id = %s AND claim_token_hash = %s
                    """,
                    ("completed_synthetic_no_provider", "completed", job_id, claim_token_hash),
                )
                terminal_count = getattr(cur, "rowcount", 0)
                getattr(conn, "commit")()
                execute(
                    f"""
                    SELECT internal_status, client_safe_status, synthetic_non_customer, non_executable, claim_token_hash
                    FROM {LIVE_WORKER_TABLE}
                    WHERE job_id = %s
                    """,
                    (job_id,),
                )
                terminal_row = fetchone()
                execute(f"DELETE FROM {LIVE_WORKER_TABLE} WHERE job_id = %s", (job_id,))
                execute(f"SELECT COUNT(*) FROM {LIVE_WORKER_TABLE} WHERE job_id = %s", (job_id,))
                remaining = fetchone()
                execute(f"DROP TABLE IF EXISTS {LIVE_WORKER_TABLE}")
                getattr(conn, "commit")()

        claim_once_passed = bool(primary_claim_count == 1)
        duplicate_claim_blocked = bool(duplicate_claim_count == 0)
        processing_status_passed = bool(processing_count == 1)
        terminal_status_passed = bool(
            terminal_count == 1
            and terminal_row
            and terminal_row[0] == "completed_synthetic_no_provider"
            and terminal_row[1] == "completed"
            and terminal_row[2] is True
            and terminal_row[3] is True
            and terminal_row[4] == claim_token_hash
        )
        cleanup_performed = bool(remaining and int(remaining[0]) == 0)
        result.update({
            "status": (
                "passed"
                if claim_once_passed and duplicate_claim_blocked and processing_status_passed and terminal_status_passed and cleanup_performed
                else "failed_live_worker_status_readback_or_cleanup"
            ),
            "durable_job_claim_once_passed": claim_once_passed,
            "duplicate_claim_blocked": duplicate_claim_blocked,
            "processing_status_passed": processing_status_passed,
            "terminal_status_passed": terminal_status_passed,
            "cleanup_performed": cleanup_performed,
            "claim_token_hash_present": True,
            "internal_status": "completed_synthetic_no_provider" if terminal_status_passed else "",
            "client_safe_status": "completed" if terminal_status_passed else "needs_attention",
        })
    except Exception as exc:
        cleanup = attempt_status_cleanup(database_url, job_id) if cleanup_enabled else {}
        result.update({
            "status": safe_exception_status(exc),
            "error": safe_exception_details(exc),
            "cleanup_attempted": bool(cleanup),
            "cleanup_performed": bool(cleanup.get("cleanup_performed")),
            "cleanup_result": cleanup,
            "next_operator_action": "Review sanitized DB error category, confirm cleanup hash, and rerun only after owner approval.",
        })
    return redact_secret_values(result)


def build_client_safe_status(status_result: Mapping[str, Any], job_id: str) -> Dict[str, Any]:
    return {
        "status": status_result.get("client_safe_status") or "needs_attention",
        "message": "A synthetic worker proof status is available.",
        "job_reference_hash": safe_hash(job_id),
        "customer_safe": True,
        "internal_config_exposed": False,
        "credential_values_exposed": False,
        "provider_secret_values_visible": False,
    }


def build_admin_diagnostics(
    *,
    job_id: str,
    block: str,
    flags: Mapping[str, bool],
    queue_result: Mapping[str, Any],
    status_result: Mapping[str, Any],
    forbidden_flags: list[str],
) -> Dict[str, Any]:
    return {
        "boundary": "aws_live_no_provider_worker_consumption",
        "diagnostic_version": LIVE_WORKER_DIAGNOSTIC_VERSION,
        "job_reference_hash": safe_hash(job_id),
        "blocked_reason": block,
        "owner_flags_required": True,
        "flags": flags,
        "queue_status": queue_result.get("status"),
        "status_result": status_result.get("status"),
        "message_reference_hash": queue_result.get("message_reference_hash", ""),
        "receipt_handle_hash_present": bool(queue_result.get("receipt_handle_hash")),
        "queue_message_delete_or_ack_passed": bool(queue_result.get("queue_message_delete_or_ack_passed")),
        "durable_job_claim_once_passed": bool(status_result.get("durable_job_claim_once_passed")),
        "duplicate_claim_blocked": bool(status_result.get("duplicate_claim_blocked")),
        "processing_status_passed": bool(status_result.get("processing_status_passed")),
        "terminal_status_passed": bool(status_result.get("terminal_status_passed")),
        "forbidden_live_execution_flags_active": forbidden_flags,
        "admin_diagnostics_redacted": True,
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
    queue_result = empty_queue_result(block)
    status_result = empty_status_result(block)
    job_id = synthetic_worker_job_id()
    result = {
        "boundary": "aws_live_no_provider_worker_consumption",
        "diagnostic_version": LIVE_WORKER_DIAGNOSTIC_VERSION,
        "status": "safe_default_no_live_worker_consumption",
        "blocked_reason": block,
        "actor_role": clean_text(actor_role, 80),
        "flags": flags,
        "owner_flags_required": True,
        "live_worker_consumption_attempted": False,
        "live_worker_consumption_passed": False,
        "synthetic_queue_message_received": False,
        "queue_message_non_customer": False,
        "queue_message_non_executable": False,
        "durable_job_claim_once_passed": False,
        "duplicate_claim_blocked": False,
        "processing_status_passed": False,
        "terminal_status_passed": False,
        "queue_message_delete_or_ack_attempted": False,
        "queue_message_delete_or_ack_passed": False,
        "client_safe_status_redacted": True,
        "admin_diagnostics_redacted": True,
        "rollback_controls_blocked_when_enabled": rollback_controls_block_when_enabled(env),
        "queue_result": queue_result,
        "status_result": status_result,
        "client_safe_status": build_client_safe_status(status_result, job_id),
        "admin_safe_diagnostics": build_admin_diagnostics(
            job_id=job_id,
            block=block,
            flags=flags,
            queue_result=queue_result,
            status_result=status_result,
            forbidden_flags=forbidden_flags,
        ),
        "customer_safe": True,
        "credential_values_exposed": False,
        "provider_secret_values_visible": False,
    }
    result.update(base_side_effect_guards())
    return redact_secret_values(result)


def build_live_no_provider_worker_consumption_proof(
    *,
    env: Optional[Mapping[str, Any]] = None,
    actor_role: str = "admin",
) -> Dict[str, Any]:
    env = dict(env or {})
    flags = live_worker_flags(env)
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

    job_id = synthetic_worker_job_id()
    queue_result = receive_synthetic_queue_message(env, job_id)
    status_result = (
        run_live_synthetic_status_claim(env, job_id, bool(flags.get("cleanup_enabled")))
        if queue_result.get("synthetic_queue_message_received")
        else empty_status_result("blocked_no_safe_synthetic_queue_message")
    )
    queue_result = (
        delete_received_queue_message(env, queue_result)
        if status_result.get("terminal_status_passed")
        else redact_secret_values({key: value for key, value in queue_result.items() if not key.startswith("_")})
    )

    live_attempted = bool(queue_result.get("sqs_receive_attempted") or status_result.get("live_durable_status_attempted"))
    live_passed = bool(
        queue_result.get("synthetic_queue_message_received")
        and queue_result.get("queue_message_non_customer")
        and queue_result.get("queue_message_non_executable")
        and status_result.get("durable_job_claim_once_passed")
        and status_result.get("duplicate_claim_blocked")
        and status_result.get("processing_status_passed")
        and status_result.get("terminal_status_passed")
        and queue_result.get("queue_message_delete_or_ack_attempted")
        and queue_result.get("queue_message_delete_or_ack_passed")
    )
    result = {
        "boundary": "aws_live_no_provider_worker_consumption",
        "diagnostic_version": LIVE_WORKER_DIAGNOSTIC_VERSION,
        "status": (
            "live_no_provider_worker_consumption_passed"
            if live_passed
            else ("live_no_provider_worker_consumption_failed" if live_attempted else "safe_default_no_live_worker_consumption")
        ),
        "blocked_reason": "",
        "flags": flags,
        "owner_flags_required": True,
        "job_reference_hash": safe_hash(job_id),
        "live_worker_consumption_attempted": live_attempted,
        "live_worker_consumption_passed": live_passed,
        "synthetic_queue_message_received": bool(queue_result.get("synthetic_queue_message_received")),
        "queue_message_non_customer": bool(queue_result.get("queue_message_non_customer")),
        "queue_message_non_executable": bool(queue_result.get("queue_message_non_executable")),
        "durable_job_claim_once_passed": bool(status_result.get("durable_job_claim_once_passed")),
        "duplicate_claim_blocked": bool(status_result.get("duplicate_claim_blocked")),
        "processing_status_passed": bool(status_result.get("processing_status_passed")),
        "terminal_status_passed": bool(status_result.get("terminal_status_passed")),
        "queue_message_delete_or_ack_attempted": bool(queue_result.get("queue_message_delete_or_ack_attempted")),
        "queue_message_delete_or_ack_passed": bool(queue_result.get("queue_message_delete_or_ack_passed")),
        "client_safe_status_redacted": True,
        "admin_diagnostics_redacted": True,
        "rollback_controls_blocked_when_enabled": rollback_controls_block_when_enabled(env),
        "queue_result": queue_result,
        "status_result": status_result,
        "client_safe_status": build_client_safe_status(status_result, job_id),
        "admin_safe_diagnostics": build_admin_diagnostics(
            job_id=job_id,
            block="",
            flags=flags,
            queue_result=queue_result,
            status_result=status_result,
            forbidden_flags=forbidden_flags,
        ),
        "incident_event": {
            "event_type": "live_no_provider_worker_consumption_proof",
            "severity": "info" if live_passed else "warning",
            "decision": "passed" if live_passed else "failed_after_live_attempt",
            "safe_job_reference_hash": safe_hash(job_id),
            "timestamp": utc_now(),
            "external_logging_attempted": False,
            "cloudwatch_put_attempted": False,
        },
        "customer_safe": True,
        "credential_values_exposed": False,
        "provider_secret_values_visible": False,
    }
    result.update(base_side_effect_guards())
    return redact_secret_values(result)
