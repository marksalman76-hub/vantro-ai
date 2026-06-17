from __future__ import annotations

from datetime import datetime, timezone
import json
import uuid
from typing import Any, Dict, Mapping, Optional

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
from backend.app.runtime.aws_option_a_route_cutover_boundary import (
    AWS_ACCEPTANCE_CUTOVER_ENABLED_FLAG,
    AWS_OPTION_A_ENABLED_FLAG,
    AWS_ROUTE_CUTOVER_ENABLED_FLAG,
    AWS_STATUS_CUTOVER_ENABLED_FLAG,
    ROUTE_MODE_ENABLED_READY,
    decide_api_acceptance_route_cutover,
    decide_api_status_route_cutover,
)


AWS_OPTION_A_LIVE_DURABLE_HANDOFF_ENABLED_FLAG = "AWS_OPTION_A_LIVE_DURABLE_HANDOFF_ENABLED"
AWS_OPTION_A_LIVE_DURABLE_HANDOFF_OWNER_APPROVED_FLAG = "AWS_OPTION_A_LIVE_DURABLE_HANDOFF_OWNER_APPROVED"
AWS_OPTION_A_LIVE_DURABLE_VALIDATION_CONFIRMED_FLAG = "AWS_OPTION_A_LIVE_DURABLE_VALIDATION_CONFIRMED"
AWS_OPTION_A_LIVE_DURABLE_WRITE_ENABLED_FLAG = "AWS_OPTION_A_LIVE_DURABLE_WRITE_ENABLED"
AWS_OPTION_A_LIVE_DURABLE_QUEUE_SEND_ENABLED_FLAG = "AWS_OPTION_A_LIVE_DURABLE_QUEUE_SEND_ENABLED"
AWS_OPTION_A_LIVE_DURABLE_STATUS_READ_ENABLED_FLAG = "AWS_OPTION_A_LIVE_DURABLE_STATUS_READ_ENABLED"
AWS_OPTION_A_LIVE_DURABLE_CLEANUP_ENABLED_FLAG = "AWS_OPTION_A_LIVE_DURABLE_CLEANUP_ENABLED"
AWS_OPTION_A_LIVE_DURABLE_HANDOFF_LOAD_LOCAL_ENV_FLAG = "AWS_OPTION_A_LIVE_DURABLE_HANDOFF_LOAD_LOCAL_ENV"

LIVE_HANDOFF_DIAGNOSTIC_VERSION = "aws_live_synthetic_durable_handoff_v1"
LIVE_HANDOFF_JOB_PREFIX = "aws_live_handoff_non_customer"
LIVE_HANDOFF_TABLE = "aws20_live_durable_handoff_proof"
LIVE_HANDOFF_MARKER = "aws20_live_durable_handoff_non_customer"

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


def synthetic_handoff_job_id() -> str:
    return f"{LIVE_HANDOFF_JOB_PREFIX}_{uuid.uuid4().hex[:12]}"


def live_handoff_flags(env: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "live_durable_handoff_enabled": enabled(env.get(AWS_OPTION_A_LIVE_DURABLE_HANDOFF_ENABLED_FLAG)),
        "owner_approved": enabled(env.get(AWS_OPTION_A_LIVE_DURABLE_HANDOFF_OWNER_APPROVED_FLAG)),
        "validation_confirmed": enabled(env.get(AWS_OPTION_A_LIVE_DURABLE_VALIDATION_CONFIRMED_FLAG)),
        "durable_write_enabled": enabled(env.get(AWS_OPTION_A_LIVE_DURABLE_WRITE_ENABLED_FLAG)),
        "queue_send_enabled": enabled(env.get(AWS_OPTION_A_LIVE_DURABLE_QUEUE_SEND_ENABLED_FLAG)),
        "status_read_enabled": enabled(env.get(AWS_OPTION_A_LIVE_DURABLE_STATUS_READ_ENABLED_FLAG)),
        "cleanup_enabled": enabled(env.get(AWS_OPTION_A_LIVE_DURABLE_CLEANUP_ENABLED_FLAG)),
        "route_cutover_enabled": enabled(env.get(AWS_ROUTE_CUTOVER_ENABLED_FLAG)),
        "acceptance_cutover_enabled": enabled(env.get(AWS_ACCEPTANCE_CUTOVER_ENABLED_FLAG)),
        "status_cutover_enabled": enabled(env.get(AWS_STATUS_CUTOVER_ENABLED_FLAG)),
        "aws_option_a_enabled": enabled(env.get(AWS_OPTION_A_ENABLED_FLAG)),
    }


def forbidden_live_execution_flags(env: Mapping[str, Any]) -> list[str]:
    return [flag for flag in FORBIDDEN_LIVE_EXECUTION_FLAGS if enabled(env.get(flag))]


def synthetic_payload(payload: Optional[Mapping[str, Any]], job_id: str) -> Dict[str, Any]:
    source = dict(payload or {})
    return redact_secret_values({
        "job_id": job_id,
        "customer_id": "synthetic_non_customer",
        "tenant_id": "synthetic_non_customer_tenant",
        "account_id": "synthetic_non_customer_account",
        "actor_role": clean_text(source.get("actor_role") or "admin", 80),
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
        "duration_seconds": 5,
        "aspect_ratio": "9:16",
        "selected_agent": "creative_director_agent",
        "selected_agents": ["creative_director_agent"],
        "agent_ids": ["creative_director_agent"],
        "multi_agent_media_execution": False,
        "video_provider": "none_live_provider_blocked",
        "audio_provider": "none_live_provider_blocked",
        "prompt": "Synthetic non-customer durable handoff proof.",
        "media_prompt": "Synthetic non-customer durable handoff proof.",
        "approval_status": "owner_approved_synthetic_infrastructure_proof",
        "credit_reservation_status": "not_required_synthetic_non_customer",
        "dry_run": False,
        "preflight_only": False,
        "smoke_test_mode": False,
    })


def validation_evidence_from_flags(flags: Mapping[str, Any]) -> Dict[str, Any]:
    status = "passed" if flags.get("validation_confirmed") else "missing"
    return {
        "status": "completed" if flags.get("validation_confirmed") else "blocked_missing_validation_confirmation",
        "service_results": {
            service: {"status": status, "redacted": True}
            for service in ("iam", "rds", "sqs", "s3", "secrets")
        },
        "secret_values_printed": False,
        "credential_values_exposed": False,
    }


def rollback_controls_block_when_enabled(env: Mapping[str, Any]) -> bool:
    rollback_env = dict(env)
    rollback_env[AWS_OPTION_A_KILL_SWITCH_ENABLED_FLAG] = "true"
    decision = build_aws_option_a_rollback_control_decision(
        env=rollback_env,
        route_kind="live_synthetic_durable_handoff",
        route_intent=True,
        route_execution_allowed=True,
        selected_runtime_path="aws_option_a_live_synthetic_durable_handoff_path",
        route_mode=ROUTE_MODE_ENABLED_READY,
    )
    return bool(decision.get("aws_route_blocked_by_rollback"))


def empty_db_result(status: str = "skipped_resource_flag_disabled") -> Dict[str, Any]:
    return {
        "resource": "rds_durable_record",
        "status": status,
        "live_durable_write_attempted": False,
        "live_durable_write_passed": False,
        "live_status_readback_attempted": False,
        "live_status_readback_passed": False,
        "db_connection_attempted": False,
        "rds_write_attempted": False,
        "cleanup_attempted": False,
        "cleanup_performed": False,
        "rollback_or_cleanup_performed": False,
        "synthetic_non_customer_job": True,
        "persistent_customer_data_touched": False,
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def empty_queue_result(status: str = "skipped_resource_flag_disabled") -> Dict[str, Any]:
    return {
        "resource": "sqs_handoff",
        "status": status,
        "live_queue_send_attempted": False,
        "live_queue_send_passed": False,
        "sqs_send_attempted": False,
        "queue_packet_non_customer": True,
        "queue_packet_non_executable": True,
        "worker_execution_allowed": False,
        "provider_call_allowed": False,
        "billing_mutation_allowed": False,
        "credit_mutation_allowed": False,
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def attempt_db_cleanup(database_url: str, job_id: str) -> Dict[str, Any]:
    cleanup = {
        "cleanup_attempted": True,
        "cleanup_performed": False,
        "cleanup_error": {},
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
                execute(f"DELETE FROM {LIVE_HANDOFF_TABLE} WHERE job_id = %s", (job_id,))
                execute(f"SELECT COUNT(*) FROM {LIVE_HANDOFF_TABLE} WHERE job_id = %s", (job_id,))
                remaining = fetchone()
                execute(f"DROP TABLE IF EXISTS {LIVE_HANDOFF_TABLE}")
            getattr(conn, "commit")()
        cleanup["cleanup_performed"] = bool(remaining and int(remaining[0]) == 0)
    except Exception as exc:
        cleanup["cleanup_error"] = {
            "status": safe_exception_status(exc),
            "error": safe_exception_details(exc),
        }
    return redact_secret_values(cleanup)


def run_live_durable_db_handoff(env: Mapping[str, Any], job_id: str, cleanup_enabled: bool) -> Dict[str, Any]:
    result = empty_db_result()
    database_url = clean_text(env.get("DATABASE_URL"), 5000)
    result["database_url_reference"] = redacted_ref(database_url)
    result["job_reference_hash"] = safe_hash(job_id)
    result["proof_table_hash"] = safe_hash(LIVE_HANDOFF_TABLE)
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
        "status": "live_durable_write_started",
        "live_durable_write_attempted": True,
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
                    CREATE TABLE IF NOT EXISTS {LIVE_HANDOFF_TABLE} (
                        job_id text primary key,
                        marker text not null,
                        internal_status text not null,
                        client_safe_status text not null,
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
                    INSERT INTO {LIVE_HANDOFF_TABLE}
                        (job_id, marker, internal_status, client_safe_status, synthetic_non_customer, non_executable)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (job_id) DO UPDATE SET
                        marker = EXCLUDED.marker,
                        internal_status = EXCLUDED.internal_status,
                        client_safe_status = EXCLUDED.client_safe_status,
                        synthetic_non_customer = EXCLUDED.synthetic_non_customer,
                        non_executable = EXCLUDED.non_executable,
                        updated_at = now()
                    """,
                    (job_id, LIVE_HANDOFF_MARKER, "accepted", "queued", True, True),
                )
                getattr(conn, "commit")()
                execute(
                    f"""
                    SELECT marker, internal_status, client_safe_status, synthetic_non_customer, non_executable
                    FROM {LIVE_HANDOFF_TABLE}
                    WHERE job_id = %s
                    """,
                    (job_id,),
                )
                inserted = fetchone()
                execute(
                    f"""
                    UPDATE {LIVE_HANDOFF_TABLE}
                    SET internal_status = %s, client_safe_status = %s, updated_at = now()
                    WHERE job_id = %s
                    """,
                    ("handoff_queued", "queued", job_id),
                )
                getattr(conn, "commit")()
                result["live_status_readback_attempted"] = True
                execute(
                    f"""
                    SELECT internal_status, client_safe_status, synthetic_non_customer, non_executable
                    FROM {LIVE_HANDOFF_TABLE}
                    WHERE job_id = %s
                    """,
                    (job_id,),
                )
                status_row = fetchone()
                execute(f"DELETE FROM {LIVE_HANDOFF_TABLE} WHERE job_id = %s", (job_id,))
                execute(f"SELECT COUNT(*) FROM {LIVE_HANDOFF_TABLE} WHERE job_id = %s", (job_id,))
                remaining = fetchone()
                execute(f"DROP TABLE IF EXISTS {LIVE_HANDOFF_TABLE}")
                getattr(conn, "commit")()

        insert_read_passed = bool(
            inserted
            and inserted[0] == LIVE_HANDOFF_MARKER
            and inserted[1] == "accepted"
            and inserted[2] == "queued"
            and inserted[3] is True
            and inserted[4] is True
        )
        status_readback_passed = bool(
            status_row
            and status_row[0] == "handoff_queued"
            and status_row[1] == "queued"
            and status_row[2] is True
            and status_row[3] is True
        )
        cleanup_performed = bool(remaining and int(remaining[0]) == 0)
        result.update({
            "status": "passed" if insert_read_passed and status_readback_passed and cleanup_performed else "failed_live_durable_handoff_readback_or_cleanup",
            "live_durable_write_passed": insert_read_passed,
            "live_status_readback_passed": status_readback_passed,
            "cleanup_performed": cleanup_performed,
            "rollback_or_cleanup_performed": cleanup_performed,
            "client_safe_status": "queued",
            "internal_status": "handoff_queued",
        })
    except Exception as exc:
        cleanup = attempt_db_cleanup(database_url, job_id) if cleanup_enabled else {}
        result.update({
            "status": safe_exception_status(exc),
            "error": safe_exception_details(exc),
            "cleanup_attempted": bool(cleanup),
            "cleanup_performed": bool(cleanup.get("cleanup_performed")),
            "rollback_or_cleanup_performed": bool(cleanup.get("cleanup_performed")),
            "cleanup_result": cleanup,
            "next_operator_action": "Review sanitized DB error category, confirm cleanup hash, and rerun only after owner approval.",
        })
    return redact_secret_values(result)


def run_live_queue_handoff(env: Mapping[str, Any], job_id: str) -> Dict[str, Any]:
    result = empty_queue_result()
    queue_url = clean_text(env.get("AWS_MEDIA_QUEUE_URL"), 2000)
    body = {
        "job_reference_hash": safe_hash(job_id),
        "task_type": "aws20_live_durable_handoff_non_customer",
        "workflow_type": "live_synthetic_durable_handoff",
        "non_customer": True,
        "non_executable": True,
        "do_not_process": True,
        "worker_execution_allowed": False,
        "provider_call_allowed": False,
        "media_generation_allowed": False,
        "stripe_call_allowed": False,
        "billing_mutation_allowed": False,
        "credit_mutation_allowed": False,
        "public_cutover_allowed": False,
        "created_at": utc_now(),
    }
    body_text = json.dumps(body, sort_keys=True)
    result["queue_reference"] = redacted_ref(queue_url)
    result["job_reference_hash"] = safe_hash(job_id)
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
        category = categorize_sqs_failure(
            exc,
            queue_url=queue_url,
            region_present=bool(clean_text(env.get("AWS_REGION")) or clean_text(env.get("AWS_DEFAULT_REGION"))),
        )
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
        category = "missing_boto3_dependency" if blocked == "blocked_missing_dependency_boto3" else "unknown_sqs_error"
        result["sqs_error_category"] = category
        result["next_operator_action"] = sqs_next_operator_action(category)
        return redact_secret_values(result)

    kwargs = {
        "QueueUrl": queue_url,
        "MessageBody": body_text,
        "MessageAttributes": {
            "live_synthetic_durable_handoff": {"StringValue": "true", "DataType": "String"},
            "non_customer": {"StringValue": "true", "DataType": "String"},
            "non_executable": {"StringValue": "true", "DataType": "String"},
            "do_not_process": {"StringValue": "true", "DataType": "String"},
        },
    }
    if queue_url.lower().endswith(".fifo"):
        kwargs["MessageGroupId"] = "aws20-live-durable-handoff"
        kwargs["MessageDeduplicationId"] = safe_hash(f"{job_id}:live-durable-handoff", 32)

    result.update({
        "status": "live_queue_send_started",
        "live_queue_send_attempted": True,
        "sqs_send_attempted": True,
        "sqs_attempted": True,
    })
    try:
        response = getattr(sqs, "send_message")(**kwargs)
        result.update({
            "status": "passed",
            "live_queue_send_passed": True,
            "sqs_passed": True,
            "sqs_message_id_hash_prefix": safe_hash(response.get("MessageId"), 12),
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
        category = categorize_sqs_failure(
            exc,
            queue_url=queue_url,
            region_present=bool(clean_text(env.get("AWS_REGION")) or clean_text(env.get("AWS_DEFAULT_REGION"))),
        )
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


def blocking_reason(
    *,
    actor_role: str,
    flags: Mapping[str, Any],
    rollback_control: Mapping[str, Any],
    route_acceptance: Mapping[str, Any],
    route_status: Mapping[str, Any],
    forbidden_flags: list[str],
) -> str:
    if clean_text(actor_role, 80).lower() not in {"admin", "owner"}:
        return "blocked_client_not_authorized"
    if forbidden_flags:
        return "blocked_forbidden_live_execution_flag_active"
    if rollback_control.get("aws_route_blocked_by_rollback"):
        return "blocked_by_rollback_control"
    if not flags.get("live_durable_handoff_enabled"):
        return "blocked_live_durable_handoff_not_enabled"
    if not flags.get("owner_approved"):
        return "blocked_owner_approval_required"
    if not flags.get("validation_confirmed"):
        return "blocked_validation_confirmation_required"
    if route_acceptance.get("route_mode") != ROUTE_MODE_ENABLED_READY:
        return "blocked_acceptance_route_not_ready"
    if route_status.get("route_mode") != ROUTE_MODE_ENABLED_READY:
        return "blocked_status_route_not_ready"
    if flags.get("durable_write_enabled") and not flags.get("cleanup_enabled"):
        return "blocked_cleanup_required"
    return ""


def build_live_synthetic_durable_handoff(
    *,
    env: Optional[Mapping[str, Any]] = None,
    actor_role: str = "admin",
    payload: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    env = dict(env or {})
    flags = live_handoff_flags(env)
    job_id = clean_text((payload or {}).get("job_id") or synthetic_handoff_job_id(), 180)
    payload_for_route = synthetic_payload(payload, job_id)
    validation_evidence = validation_evidence_from_flags(flags)
    route_acceptance = decide_api_acceptance_route_cutover(
        payload_for_route,
        env=env,
        validation_evidence=validation_evidence,
    )
    route_status = decide_api_status_route_cutover(
        {"job_id": job_id, "actor_role": actor_role, "package_name": "enterprise", "entitlement_status": "active"},
        env=env,
        validation_evidence=validation_evidence,
    )
    rollback_control = build_aws_option_a_rollback_control_decision(
        env=env,
        route_kind="live_synthetic_durable_handoff",
        route_intent=True,
        route_execution_allowed=True,
        selected_runtime_path="aws_option_a_live_synthetic_durable_handoff_path",
        route_mode=clean_text(route_acceptance.get("route_mode"), 120),
    )
    forbidden_flags = forbidden_live_execution_flags(env)
    block = blocking_reason(
        actor_role=actor_role,
        flags=flags,
        rollback_control=rollback_control,
        route_acceptance=route_acceptance,
        route_status=route_status,
        forbidden_flags=forbidden_flags,
    )

    if block:
        db_result = empty_db_result(block)
        queue_result = empty_queue_result(block)
    else:
        db_result = (
            run_live_durable_db_handoff(env, job_id, bool(flags.get("cleanup_enabled")))
            if flags.get("durable_write_enabled") or flags.get("status_read_enabled")
            else empty_db_result()
        )
        queue_result = (
            run_live_queue_handoff(env, job_id)
            if flags.get("queue_send_enabled")
            else empty_queue_result()
        )

    live_attempted = bool(db_result.get("live_durable_write_attempted") or queue_result.get("live_queue_send_attempted"))
    live_passed = bool(
        db_result.get("live_durable_write_passed")
        and db_result.get("live_status_readback_passed")
        and queue_result.get("live_queue_send_passed")
    )
    client_safe_status = {
        "status": "queued" if db_result.get("live_status_readback_passed") else "not_started",
        "message": "Your request is queued for processing." if db_result.get("live_status_readback_passed") else "Processing has not started.",
        "job_reference_hash": safe_hash(job_id),
        "customer_safe": True,
        "internal_config_exposed": False,
        "credential_values_exposed": False,
    }
    admin_diagnostics = {
        "boundary": "aws_live_synthetic_durable_handoff",
        "diagnostic_version": LIVE_HANDOFF_DIAGNOSTIC_VERSION,
        "job_reference_hash": safe_hash(job_id),
        "blocked_reason": block,
        "route_acceptance_mode": clean_text(route_acceptance.get("route_mode"), 120),
        "route_status_mode": clean_text(route_status.get("route_mode"), 120),
        "db_status": clean_text(db_result.get("status"), 160),
        "queue_status": clean_text(queue_result.get("status"), 160),
        "sqs_message_id_hash_prefix": queue_result.get("sqs_message_id_hash_prefix", ""),
        "cleanup_performed": bool(db_result.get("cleanup_performed")),
        "forbidden_live_execution_flags_active": forbidden_flags,
        "credential_values_exposed": False,
        "secret_values_exposed": False,
    }
    result = {
        "boundary": "aws_live_synthetic_durable_handoff",
        "diagnostic_version": LIVE_HANDOFF_DIAGNOSTIC_VERSION,
        "status": (
            "live_synthetic_durable_handoff_passed"
            if live_passed
            else ("live_synthetic_durable_handoff_failed" if live_attempted else "safe_default_no_live_handoff")
        ),
        "blocked_reason": block,
        "flags": flags,
        "route_validation_acknowledged": bool(flags.get("validation_confirmed")),
        "route_acceptance_ready": clean_text(route_acceptance.get("route_mode"), 120) == ROUTE_MODE_ENABLED_READY,
        "route_status_ready": clean_text(route_status.get("route_mode"), 120) == ROUTE_MODE_ENABLED_READY,
        "route_acceptance_mode": clean_text(route_acceptance.get("route_mode"), 120),
        "route_status_mode": clean_text(route_status.get("route_mode"), 120),
        "rollback_control_active": bool(rollback_control.get("rollback_control_active")),
        "rollback_controls_blocked_when_enabled": rollback_controls_block_when_enabled(env),
        "forbidden_live_execution_flags_active": forbidden_flags,
        "synthetic_non_customer_job": True,
        "durable_job_reference_hash": safe_hash(job_id),
        "live_durable_write_attempted": bool(db_result.get("live_durable_write_attempted")),
        "live_durable_write_passed": bool(db_result.get("live_durable_write_passed")),
        "live_status_readback_attempted": bool(db_result.get("live_status_readback_attempted")),
        "live_status_readback_passed": bool(db_result.get("live_status_readback_passed")),
        "live_queue_send_attempted": bool(queue_result.get("live_queue_send_attempted")),
        "live_queue_send_passed": bool(queue_result.get("live_queue_send_passed")),
        "queue_packet_non_customer": bool(queue_result.get("queue_packet_non_customer")),
        "queue_packet_non_executable": bool(queue_result.get("queue_packet_non_executable")),
        "rollback_or_cleanup_performed": bool(db_result.get("rollback_or_cleanup_performed")),
        "client_safe_status_redacted": True,
        "admin_diagnostics_redacted": True,
        "worker_started": False,
        "media_worker_started": False,
        "provider_call_attempted": False,
        "paid_provider_calls_started": False,
        "stripe_call_attempted": False,
        "billing_mutation_attempted": False,
        "credit_mutation_attempted": False,
        "public_cutover_enabled": False,
        "public_production_cutover_enabled": False,
        "secret_fetch_attempted": False,
        "secrets_manager_value_retrieved": False,
        "db_result": db_result,
        "queue_result": queue_result,
        "client_safe_status": client_safe_status,
        "admin_safe_diagnostics": admin_diagnostics,
        "incident_event": {
            "event_type": "live_synthetic_durable_handoff_proof",
            "severity": "info" if live_passed else ("warning" if live_attempted else "notice"),
            "decision": "passed" if live_passed else block or "failed_after_live_attempt",
            "safe_job_reference_hash": safe_hash(job_id),
            "timestamp": utc_now(),
            "external_logging_attempted": False,
            "cloudwatch_put_attempted": False,
        },
        "customer_safe": True,
        "credential_values_exposed": False,
        "provider_secret_values_visible": False,
    }
    return redact_secret_values(result)
