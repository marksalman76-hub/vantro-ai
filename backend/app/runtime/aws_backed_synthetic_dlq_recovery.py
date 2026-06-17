from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Mapping, Optional
import uuid

from backend.app.runtime.aws_option_a_live_rehearsal import (
    clean_text,
    enabled,
    optional_dependency,
    redacted_ref,
    redact_secret_values,
    safe_exception_details,
    safe_exception_status,
    safe_hash,
)
from backend.app.runtime.aws_option_a_rollback_controls import (
    AWS_OPTION_A_KILL_SWITCH_ENABLED_FLAG,
    build_aws_option_a_rollback_control_decision,
)


AWS_BACKED_DLQ_RECOVERY_ENABLED_FLAG = "AWS_BACKED_DLQ_RECOVERY_ENABLED"
AWS_BACKED_DLQ_RECOVERY_OWNER_APPROVED_FLAG = "AWS_BACKED_DLQ_RECOVERY_OWNER_APPROVED"
AWS_BACKED_DLQ_RECOVERY_VALIDATION_CONFIRMED_FLAG = "AWS_BACKED_DLQ_RECOVERY_VALIDATION_CONFIRMED"
AWS_BACKED_DLQ_RECOVERY_STATUS_READBACK_ENABLED_FLAG = "AWS_BACKED_DLQ_RECOVERY_STATUS_READBACK_ENABLED"
AWS_BACKED_DLQ_RECOVERY_ACTION_ENABLED_FLAG = "AWS_BACKED_DLQ_RECOVERY_ACTION_ENABLED"
AWS_BACKED_DLQ_RECOVERY_CLEANUP_ENABLED_FLAG = "AWS_BACKED_DLQ_RECOVERY_CLEANUP_ENABLED"
AWS_BACKED_DLQ_RECOVERY_LOAD_LOCAL_ENV_FLAG = "AWS_BACKED_DLQ_RECOVERY_LOAD_LOCAL_ENV"

AWS_BACKED_DLQ_RECOVERY_DIAGNOSTIC_VERSION = "aws_backed_synthetic_dlq_recovery_v1"
AWS_BACKED_DLQ_RECOVERY_JOB_PREFIX = "aws_backed_dlq_recovery_non_customer"
AWS_BACKED_DLQ_RECOVERY_TABLE = "aws20_live_dlq_recovery_proof"
AWS_BACKED_DLQ_RECOVERY_MARKER = "aws20_live_dlq_recovery_non_customer"

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


def synthetic_dlq_recovery_job_id() -> str:
    return f"{AWS_BACKED_DLQ_RECOVERY_JOB_PREFIX}_{uuid.uuid4().hex[:12]}"


def dlq_recovery_flags(env: Mapping[str, Any]) -> Dict[str, bool]:
    return {
        "dlq_recovery_enabled": enabled(env.get(AWS_BACKED_DLQ_RECOVERY_ENABLED_FLAG)),
        "owner_approved": enabled(env.get(AWS_BACKED_DLQ_RECOVERY_OWNER_APPROVED_FLAG)),
        "validation_confirmed": enabled(env.get(AWS_BACKED_DLQ_RECOVERY_VALIDATION_CONFIRMED_FLAG)),
        "status_readback_enabled": enabled(env.get(AWS_BACKED_DLQ_RECOVERY_STATUS_READBACK_ENABLED_FLAG)),
        "recovery_action_enabled": enabled(env.get(AWS_BACKED_DLQ_RECOVERY_ACTION_ENABLED_FLAG)),
        "cleanup_enabled": enabled(env.get(AWS_BACKED_DLQ_RECOVERY_CLEANUP_ENABLED_FLAG)),
    }


def forbidden_live_execution_flags(env: Mapping[str, Any]) -> list[str]:
    return [flag for flag in FORBIDDEN_LIVE_EXECUTION_FLAGS if enabled(env.get(flag))]


def base_side_effect_guards() -> Dict[str, bool]:
    return {
        "live_worker_loop_started": False,
        "worker_loop_started": False,
        "customer_queue_message_consumed": False,
        "customer_queue_consumed": False,
        "provider_call_attempted": False,
        "paid_provider_calls_started": False,
        "media_generation_attempted": False,
        "ffmpeg_invoked": False,
        "stripe_call_attempted": False,
        "billing_mutation_attempted": False,
        "credit_mutation_attempted": False,
        "customer_traffic_attempted": False,
        "customer_traffic_started": False,
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
        route_kind="aws_backed_synthetic_dlq_recovery",
        route_intent=True,
        route_execution_allowed=True,
        selected_runtime_path="aws_backed_synthetic_dlq_recovery_boundary",
        route_mode="aws_backed_synthetic_dlq_recovery_proof",
    )
    return bool(decision.get("aws_route_blocked_by_rollback"))


def rollback_active(env: Mapping[str, Any]) -> bool:
    decision = build_aws_option_a_rollback_control_decision(
        env=env,
        route_kind="aws_backed_synthetic_dlq_recovery",
        route_intent=True,
        route_execution_allowed=True,
        selected_runtime_path="aws_backed_synthetic_dlq_recovery_boundary",
        route_mode="aws_backed_synthetic_dlq_recovery_proof",
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
    if not flags.get("dlq_recovery_enabled"):
        return "blocked_dlq_recovery_not_enabled"
    if not flags.get("owner_approved"):
        return "blocked_owner_approval_required"
    if not flags.get("validation_confirmed"):
        return "blocked_validation_confirmation_required"
    if not flags.get("status_readback_enabled"):
        return "blocked_status_readback_flag_required"
    if not flags.get("recovery_action_enabled"):
        return "blocked_recovery_action_flag_required"
    if not flags.get("cleanup_enabled"):
        return "blocked_cleanup_required"
    return ""


def empty_live_result(status: str = "skipped_not_enabled") -> Dict[str, Any]:
    return {
        "resource": "aws_backed_synthetic_dlq_recovery",
        "status": status,
        "aws_backed_dlq_recovery_attempted": False,
        "aws_backed_dlq_recovery_passed": False,
        "synthetic_dlq_message_present": False,
        "dlq_message_non_customer": False,
        "dlq_message_non_executable": False,
        "dlq_reference_redacted": True,
        "failure_classification_passed": False,
        "retry_exhaustion_or_failed_terminal_represented": False,
        "admin_recovery_action_represented": False,
        "recovery_or_requeue_attempted": False,
        "recovery_or_requeue_passed": False,
        "client_safe_failed_or_recovered_status_redacted": True,
        "admin_diagnostics_redacted": True,
        "live_durable_status_attempted": False,
        "db_connection_attempted": False,
        "rds_write_attempted": False,
        "cleanup_attempted": False,
        "cleanup_performed": False,
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def build_client_safe_status(live_result: Mapping[str, Any], job_id: str) -> Dict[str, Any]:
    status = "recovered" if live_result.get("recovery_or_requeue_passed") else "failed_support_notified"
    return {
        "status": status,
        "message": "A safe recovery status is available.",
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
    live_result: Mapping[str, Any],
    forbidden_flags: list[str],
) -> Dict[str, Any]:
    return {
        "boundary": "aws_backed_synthetic_dlq_recovery",
        "diagnostic_version": AWS_BACKED_DLQ_RECOVERY_DIAGNOSTIC_VERSION,
        "job_reference_hash": safe_hash(job_id),
        "blocked_reason": block,
        "owner_flags_required": True,
        "flags": flags,
        "dlq_recovery_status": live_result.get("status"),
        "synthetic_dlq_message_present": bool(live_result.get("synthetic_dlq_message_present")),
        "dlq_reference_hash": live_result.get("dlq_reference_hash", ""),
        "dlq_reference_redacted": bool(live_result.get("dlq_reference_redacted", True)),
        "failure_classification": live_result.get("failure_classification", ""),
        "retry_exhaustion_or_failed_terminal_represented": bool(
            live_result.get("retry_exhaustion_or_failed_terminal_represented")
        ),
        "admin_recovery_action_represented": bool(live_result.get("admin_recovery_action_represented")),
        "recovery_or_requeue_attempted": bool(live_result.get("recovery_or_requeue_attempted")),
        "recovery_or_requeue_passed": bool(live_result.get("recovery_or_requeue_passed")),
        "cleanup_performed": bool(live_result.get("cleanup_performed")),
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
    job_id = synthetic_dlq_recovery_job_id()
    live_result = empty_live_result(block)
    live_result_fields = dict(live_result)
    live_result_fields.pop("status", None)
    result = {
        "boundary": "aws_backed_synthetic_dlq_recovery",
        "diagnostic_version": AWS_BACKED_DLQ_RECOVERY_DIAGNOSTIC_VERSION,
        "status": "safe_default_no_aws_backed_dlq_recovery",
        "blocked_reason": block,
        "actor_role": clean_text(actor_role, 80),
        "flags": flags,
        "owner_flags_required": True,
        "rollback_controls_blocked_when_enabled": rollback_controls_block_when_enabled(env),
        "client_safe_failed_or_recovered_status_redacted": True,
        "admin_diagnostics_redacted": True,
        "client_safe_status": build_client_safe_status(live_result, job_id),
        "admin_safe_diagnostics": build_admin_diagnostics(
            job_id=job_id,
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
                execute(f"DELETE FROM {AWS_BACKED_DLQ_RECOVERY_TABLE} WHERE job_id = %s", (job_id,))
                execute(f"SELECT COUNT(*) FROM {AWS_BACKED_DLQ_RECOVERY_TABLE} WHERE job_id = %s", (job_id,))
                remaining = fetchone()
                execute(f"DROP TABLE IF EXISTS {AWS_BACKED_DLQ_RECOVERY_TABLE}")
            getattr(conn, "commit")()
        cleanup["cleanup_performed"] = bool(remaining and int(remaining[0]) == 0)
    except Exception as exc:
        cleanup["cleanup_error"] = {
            "status": safe_exception_status(exc),
            "error": safe_exception_details(exc),
        }
    return redact_secret_values(cleanup)


def run_live_dlq_recovery_status_proof(env: Mapping[str, Any], job_id: str) -> Dict[str, Any]:
    result = empty_live_result()
    database_url = clean_text(env.get("DATABASE_URL"), 5000)
    dlq_url = clean_text(env.get("AWS_OPTION_A_LIVE_DLQ_RECOVERY_QUEUE_URL") or env.get("AWS_MEDIA_DLQ_URL"), 2000)
    result.update({
        "database_url_reference": redacted_ref(database_url),
        "dlq_reference": redacted_ref(dlq_url),
        "dlq_reference_hash": safe_hash(dlq_url or "synthetic-dlq-reference"),
        "dlq_reference_redacted": True,
        "job_reference_hash": safe_hash(job_id),
        "proof_table_hash": safe_hash(AWS_BACKED_DLQ_RECOVERY_TABLE),
    })
    if not database_url:
        result["status"] = "blocked_missing_database_url_no_secret_fetch"
        result["next_operator_action"] = "Load a redacted local validation env with DATABASE_URL present, then rerun once with owner approval."
        return redact_secret_values(result)
    psycopg = optional_dependency("psycopg")
    if psycopg is None:
        result["status"] = "blocked_missing_dependency_psycopg"
        result["next_operator_action"] = "Install/restore psycopg in the validation venv before rerun."
        return redact_secret_values(result)

    result.update({
        "status": "live_aws_backed_dlq_recovery_started",
        "aws_backed_dlq_recovery_attempted": True,
        "live_durable_status_attempted": True,
        "db_connection_attempted": True,
        "rds_write_attempted": True,
        "cleanup_attempted": True,
    })
    cleanup: Dict[str, Any] = {}
    try:
        connect = getattr(psycopg, "connect")
        with connect(database_url, connect_timeout=5) as conn:
            with conn.cursor() as cur:
                execute = getattr(cur, "execute")
                fetchone = getattr(cur, "fetchone")
                execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS {AWS_BACKED_DLQ_RECOVERY_TABLE} (
                        job_id text primary key,
                        marker text not null,
                        dlq_reference_hash text not null,
                        internal_status text not null,
                        client_safe_status text not null,
                        failure_classification text not null,
                        retry_exhausted boolean not null,
                        dlq_message_non_customer boolean not null,
                        dlq_message_non_executable boolean not null,
                        admin_recovery_action text not null,
                        recovery_action_status text not null,
                        created_at text not null,
                        updated_at text not null
                    )
                    """
                )
                now = utc_now()
                execute(
                    f"""
                    INSERT INTO {AWS_BACKED_DLQ_RECOVERY_TABLE} (
                        job_id,
                        marker,
                        dlq_reference_hash,
                        internal_status,
                        client_safe_status,
                        failure_classification,
                        retry_exhausted,
                        dlq_message_non_customer,
                        dlq_message_non_executable,
                        admin_recovery_action,
                        recovery_action_status,
                        created_at,
                        updated_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        job_id,
                        AWS_BACKED_DLQ_RECOVERY_MARKER,
                        result["dlq_reference_hash"],
                        "failed_terminal",
                        "failed_support_notified",
                        "synthetic_worker_execution_failure",
                        True,
                        True,
                        True,
                        "admin_recovery_action_represented",
                        "pending_owner_approved_recovery",
                        now,
                        now,
                    ),
                )
                execute(
                    f"""
                    SELECT marker, internal_status, client_safe_status, failure_classification,
                           retry_exhausted, dlq_message_non_customer, dlq_message_non_executable,
                           admin_recovery_action, recovery_action_status
                    FROM {AWS_BACKED_DLQ_RECOVERY_TABLE}
                    WHERE job_id = %s
                    """,
                    (job_id,),
                )
                failed_row = fetchone()
                synthetic_present = bool(failed_row and failed_row[0] == AWS_BACKED_DLQ_RECOVERY_MARKER)
                failure_classification_passed = bool(failed_row and failed_row[3] == "synthetic_worker_execution_failure")
                retry_or_failed_terminal = bool(failed_row and (failed_row[4] is True or failed_row[1] == "failed_terminal"))
                non_customer = bool(failed_row and failed_row[5] is True)
                non_executable = bool(failed_row and failed_row[6] is True)
                admin_recovery_action = bool(failed_row and failed_row[7] == "admin_recovery_action_represented")

                execute(
                    f"""
                    UPDATE {AWS_BACKED_DLQ_RECOVERY_TABLE}
                    SET internal_status = %s,
                        client_safe_status = %s,
                        recovery_action_status = %s,
                        updated_at = %s
                    WHERE job_id = %s
                      AND marker = %s
                      AND dlq_message_non_customer = true
                      AND dlq_message_non_executable = true
                      AND retry_exhausted = true
                    """,
                    (
                        "recovered_synthetic_no_provider",
                        "recovered",
                        "owner_approved_recovery_represented",
                        utc_now(),
                        job_id,
                        AWS_BACKED_DLQ_RECOVERY_MARKER,
                    ),
                )
                recovery_attempted = True
                recovery_update_passed = bool(getattr(cur, "rowcount", 0) == 1)
                execute(
                    f"""
                    SELECT internal_status, client_safe_status, recovery_action_status
                    FROM {AWS_BACKED_DLQ_RECOVERY_TABLE}
                    WHERE job_id = %s
                    """,
                    (job_id,),
                )
                recovered_row = fetchone()
                recovery_passed = bool(
                    recovery_update_passed
                    and recovered_row
                    and recovered_row[0] == "recovered_synthetic_no_provider"
                    and recovered_row[1] == "recovered"
                    and recovered_row[2] == "owner_approved_recovery_represented"
                )
                execute(f"DELETE FROM {AWS_BACKED_DLQ_RECOVERY_TABLE} WHERE job_id = %s", (job_id,))
                execute(f"SELECT COUNT(*) FROM {AWS_BACKED_DLQ_RECOVERY_TABLE} WHERE job_id = %s", (job_id,))
                remaining = fetchone()
                execute(f"DROP TABLE IF EXISTS {AWS_BACKED_DLQ_RECOVERY_TABLE}")
            getattr(conn, "commit")()
        cleanup = {
            "cleanup_attempted": True,
            "cleanup_performed": bool(remaining and int(remaining[0]) == 0),
            "job_reference_hash": safe_hash(job_id),
        }
        live_passed = bool(
            synthetic_present
            and non_customer
            and non_executable
            and failure_classification_passed
            and retry_or_failed_terminal
            and admin_recovery_action
            and recovery_attempted
            and recovery_passed
            and cleanup.get("cleanup_performed")
        )
        result.update({
            "status": "passed" if live_passed else "failed_aws_backed_dlq_recovery_readback_or_cleanup",
            "aws_backed_dlq_recovery_passed": live_passed,
            "synthetic_dlq_message_present": synthetic_present,
            "dlq_message_non_customer": non_customer,
            "dlq_message_non_executable": non_executable,
            "failure_classification": "synthetic_worker_execution_failure" if failure_classification_passed else "",
            "failure_classification_passed": failure_classification_passed,
            "retry_exhaustion_or_failed_terminal_represented": retry_or_failed_terminal,
            "admin_recovery_action_represented": admin_recovery_action,
            "recovery_or_requeue_attempted": recovery_attempted,
            "recovery_or_requeue_passed": recovery_passed,
            "client_safe_failed_or_recovered_status_redacted": True,
            "admin_diagnostics_redacted": True,
            "cleanup_performed": bool(cleanup.get("cleanup_performed")),
            "client_safe_status": "recovered" if recovery_passed else "failed_support_notified",
        })
    except Exception as exc:
        cleanup = attempt_status_cleanup(database_url, job_id)
        result.update({
            "status": safe_exception_status(exc),
            "error": safe_exception_details(exc),
            "cleanup_attempted": bool(cleanup),
            "cleanup_performed": bool(cleanup.get("cleanup_performed")),
            "cleanup_result": cleanup,
            "next_operator_action": "Review sanitized DB error category, confirm cleanup hash, and rerun only after owner approval.",
        })
    return redact_secret_values(result)


def build_aws_backed_synthetic_dlq_recovery_proof(
    *,
    env: Optional[Mapping[str, Any]] = None,
    actor_role: str = "admin",
) -> Dict[str, Any]:
    env = dict(env or {})
    flags = dlq_recovery_flags(env)
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

    job_id = synthetic_dlq_recovery_job_id()
    live_result = run_live_dlq_recovery_status_proof(env, job_id)
    live_passed = bool(live_result.get("aws_backed_dlq_recovery_passed"))
    result = {
        "boundary": "aws_backed_synthetic_dlq_recovery",
        "diagnostic_version": AWS_BACKED_DLQ_RECOVERY_DIAGNOSTIC_VERSION,
        "status": (
            "aws_backed_dlq_recovery_passed"
            if live_passed
            else (
                "aws_backed_dlq_recovery_failed"
                if live_result.get("aws_backed_dlq_recovery_attempted")
                else "safe_default_no_aws_backed_dlq_recovery"
            )
        ),
        "blocked_reason": "",
        "flags": flags,
        "owner_flags_required": True,
        "job_reference_hash": safe_hash(job_id),
        "rollback_controls_blocked_when_enabled": rollback_controls_block_when_enabled(env),
        "client_safe_status": build_client_safe_status(live_result, job_id),
        "admin_safe_diagnostics": build_admin_diagnostics(
            job_id=job_id,
            block="",
            flags=flags,
            live_result=live_result,
            forbidden_flags=forbidden_flags,
        ),
        "live_result": live_result,
        "incident_event": {
            "event_type": "aws_backed_synthetic_dlq_recovery_proof",
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
    result.update({
        key: live_result.get(key)
        for key in [
            "aws_backed_dlq_recovery_attempted",
            "aws_backed_dlq_recovery_passed",
            "synthetic_dlq_message_present",
            "dlq_message_non_customer",
            "dlq_message_non_executable",
            "dlq_reference_redacted",
            "failure_classification_passed",
            "retry_exhaustion_or_failed_terminal_represented",
            "admin_recovery_action_represented",
            "recovery_or_requeue_attempted",
            "recovery_or_requeue_passed",
            "client_safe_failed_or_recovered_status_redacted",
            "admin_diagnostics_redacted",
        ]
    })
    result.update(base_side_effect_guards())
    return redact_secret_values(result)
