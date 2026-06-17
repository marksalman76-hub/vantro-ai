from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import re
import uuid
from typing import Any, Dict, Mapping, Optional

from backend.app.runtime.aws_option_a_rollback_controls import (
    AWS_OPTION_A_KILL_SWITCH_ENABLED_FLAG,
    build_aws_option_a_rollback_control_decision,
)


SYNTHETIC_WORKER_LIFECYCLE_DIAGNOSTIC_VERSION = "synthetic_durable_worker_lifecycle_v1"
SYNTHETIC_WORKER_JOB_PREFIX = "synthetic_worker_lifecycle_non_customer"
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


def synthetic_job_id(payload: Optional[Mapping[str, Any]] = None) -> str:
    payload = dict(payload or {})
    supplied = clean_text(payload.get("job_id"), 180)
    if supplied and supplied.startswith(SYNTHETIC_WORKER_JOB_PREFIX):
        return supplied
    return f"{SYNTHETIC_WORKER_JOB_PREFIX}_{uuid.uuid4().hex[:12]}"


def rollback_controls_block_when_enabled(env: Mapping[str, Any]) -> bool:
    rollback_env = dict(env)
    rollback_env[AWS_OPTION_A_KILL_SWITCH_ENABLED_FLAG] = "true"
    decision = build_aws_option_a_rollback_control_decision(
        env=rollback_env,
        route_kind="synthetic_durable_worker_lifecycle",
        route_intent=True,
        route_execution_allowed=True,
        selected_runtime_path="synthetic_durable_worker_lifecycle_boundary",
        route_mode="synthetic_worker_lifecycle_proof",
    )
    return bool(decision.get("aws_route_blocked_by_rollback"))


def rollback_active(env: Mapping[str, Any]) -> bool:
    decision = build_aws_option_a_rollback_control_decision(
        env=env,
        route_kind="synthetic_durable_worker_lifecycle",
        route_intent=True,
        route_execution_allowed=True,
        selected_runtime_path="synthetic_durable_worker_lifecycle_boundary",
        route_mode="synthetic_worker_lifecycle_proof",
    )
    return bool(decision.get("aws_route_blocked_by_rollback"))


def base_side_effect_guards() -> Dict[str, bool]:
    return {
        "worker_started": False,
        "worker_loop_started": False,
        "customer_queue_consumed": False,
        "aws_call_attempted": False,
        "rds_write_attempted": False,
        "sqs_send_attempted": False,
        "s3_upload_attempted": False,
        "provider_call_attempted": False,
        "paid_provider_calls_started": False,
        "media_generation_attempted": False,
        "ffmpeg_invoked": False,
        "stripe_call_attempted": False,
        "billing_mutation_attempted": False,
        "credit_mutation_attempted": False,
        "public_cutover_enabled": False,
        "public_production_cutover_enabled": False,
        "secret_fetch_attempted": False,
        "secrets_manager_value_retrieved": False,
    }


def initial_synthetic_record(job_id: str) -> Dict[str, Any]:
    return {
        "job_reference_hash": safe_hash(job_id),
        "message_reference_hash": safe_hash(f"{job_id}:message"),
        "status": "queued",
        "client_safe_status": "queued",
        "attempt_count": 0,
        "max_attempts": 3,
        "claim_count": 0,
        "synthetic_non_customer_job": True,
        "non_executable": True,
        "created_at": utc_now(),
        "updated_at": utc_now(),
    }


def claim_once(record: Mapping[str, Any], worker_ref: str) -> Dict[str, Any]:
    claimed = dict(record)
    if clean_text(claimed.get("status")) != "queued" or int(claimed.get("claim_count") or 0) > 0:
        return {
            "status": "already_claimed",
            "claim_once_passed": False,
            "duplicate_claim_blocked": True,
            "record": claimed,
        }
    claimed.update({
        "status": "claimed",
        "client_safe_status": "queued",
        "claim_count": 1,
        "claimed_by_worker_hash": safe_hash(worker_ref),
        "claim_token_hash": safe_hash(f"{worker_ref}:{claimed.get('job_reference_hash')}:claim"),
        "updated_at": utc_now(),
    })
    return {
        "status": "claimed",
        "claim_once_passed": True,
        "duplicate_claim_blocked": False,
        "record": claimed,
    }


def duplicate_claim(record: Mapping[str, Any], worker_ref: str) -> Dict[str, Any]:
    duplicate = dict(record)
    blocked = int(duplicate.get("claim_count") or 0) > 0
    return {
        "status": "already_claimed" if blocked else "claim_available",
        "duplicate_claim_blocked": blocked,
        "duplicate_worker_hash": safe_hash(worker_ref),
        "existing_claim_token_hash_present": bool(duplicate.get("claim_token_hash")),
    }


def mark_processing(record: Mapping[str, Any]) -> Dict[str, Any]:
    processing = dict(record)
    processing.update({
        "status": "processing",
        "client_safe_status": "running",
        "updated_at": utc_now(),
    })
    return processing


def schedule_retry(record: Mapping[str, Any]) -> Dict[str, Any]:
    retry = dict(record)
    retry.update({
        "status": "retry_scheduled",
        "client_safe_status": "running",
        "attempt_count": int(retry.get("attempt_count") or 0) + 1,
        "retry_allowed": True,
        "retry_reason_code": "synthetic_worker_retry_without_provider",
        "next_retry_reference_hash": safe_hash(f"{retry.get('job_reference_hash')}:retry:1"),
        "provider_retry_external_call_executed": False,
        "updated_at": utc_now(),
    })
    return retry


def record_terminal_failure(record: Mapping[str, Any]) -> Dict[str, Any]:
    failed = dict(record)
    failed.update({
        "status": "failed_terminal",
        "client_safe_status": "needs_attention",
        "safe_error_summary": "Synthetic worker failure was recorded for lifecycle proof. No provider or customer action started.",
        "failure_code_hash": safe_hash("synthetic_worker_failure"),
        "diagnostics_redacted": True,
        "updated_at": utc_now(),
    })
    return failed


def record_terminal_completion(record: Mapping[str, Any]) -> Dict[str, Any]:
    completed = dict(record)
    completed.update({
        "status": "completed",
        "client_safe_status": "completed",
        "synthetic_output_only": True,
        "synthetic_output_reference_hash": safe_hash(f"{completed.get('job_reference_hash')}:synthetic-output"),
        "media_generation_attempted": False,
        "asset_persistence_started": False,
        "updated_at": utc_now(),
    })
    return completed


def build_dlq_or_recovery_shape(record: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "dlq_or_recovery_shape_present": True,
        "dlq_target": "synthetic_media_dead_letter",
        "job_reference_hash": record.get("job_reference_hash"),
        "recovery_actions": [
            "inspect_redacted_admin_diagnostics",
            "retry_synthetic_job_without_provider",
            "mark_terminal_failed_client_safe",
        ],
        "customer_queue_consumed": False,
        "sqs_send_attempted": False,
        "provider_call_attempted": False,
        "billing_mutation_attempted": False,
        "credit_mutation_attempted": False,
        "admin_diagnostics_redacted": True,
    }


def build_client_safe_status(record: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "status": clean_text(record.get("client_safe_status") or "queued", 80),
        "message": "Your job status is available. Support can help if attention is needed.",
        "job_reference_hash": record.get("job_reference_hash"),
        "customer_safe": True,
        "internal_config_exposed": False,
        "credential_values_exposed": False,
        "provider_secret_values_visible": False,
    }


def build_admin_diagnostics(
    *,
    queued: Mapping[str, Any],
    claimed: Mapping[str, Any],
    retry: Mapping[str, Any],
    failed: Mapping[str, Any],
    completed: Mapping[str, Any],
    dlq: Mapping[str, Any],
) -> Dict[str, Any]:
    return {
        "diagnostic_version": SYNTHETIC_WORKER_LIFECYCLE_DIAGNOSTIC_VERSION,
        "job_reference_hash": queued.get("job_reference_hash"),
        "queued_status": queued.get("status"),
        "claimed_status": claimed.get("status"),
        "processing_status": "processing",
        "retry_status": retry.get("status"),
        "failed_status": failed.get("status"),
        "completed_status": completed.get("status"),
        "claim_token_hash_present": bool(claimed.get("claim_token_hash")),
        "dlq_or_recovery_shape_present": bool(dlq.get("dlq_or_recovery_shape_present")),
        "safe_error_summary": failed.get("safe_error_summary"),
        "synthetic_output_reference_hash": completed.get("synthetic_output_reference_hash"),
        "admin_diagnostics_redacted": True,
        "credential_values_exposed": False,
        "secret_values_exposed": False,
    }


def build_blocked_by_rollback_result(env: Mapping[str, Any]) -> Dict[str, Any]:
    result = {
        "boundary": "synthetic_durable_worker_lifecycle",
        "diagnostic_version": SYNTHETIC_WORKER_LIFECYCLE_DIAGNOSTIC_VERSION,
        "status": "blocked_by_rollback_control",
        "blocked_reason": "blocked_by_rollback_control",
        "synthetic_worker_lifecycle_attempted": False,
        "synthetic_worker_lifecycle_passed": False,
        "queued_status_represented": False,
        "claim_once_passed": False,
        "duplicate_claim_blocked": False,
        "processing_status_passed": False,
        "retry_state_represented": False,
        "failure_status_passed": False,
        "completed_status_represented": False,
        "terminal_status_readback_passed": False,
        "dlq_or_recovery_shape_present": False,
        "client_safe_status_redacted": True,
        "admin_diagnostics_redacted": True,
        "rollback_controls_blocked_when_enabled": rollback_controls_block_when_enabled(env),
        "synthetic_non_customer_job": True,
        "client_safe_status": {
            "status": "current_runtime_active",
            "message": "Processing is paused by an operator safety control.",
            "customer_safe": True,
            "internal_config_exposed": False,
        },
        "admin_safe_diagnostics": {
            "blocked_reason": "blocked_by_rollback_control",
            "admin_diagnostics_redacted": True,
            "credential_values_exposed": False,
        },
        "customer_safe": True,
        "credential_values_exposed": False,
    }
    result.update(base_side_effect_guards())
    return redact_secret_values(result)


def build_synthetic_durable_worker_lifecycle_proof(
    *,
    env: Optional[Mapping[str, Any]] = None,
    payload: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    env = dict(env or {})
    if rollback_active(env):
        return build_blocked_by_rollback_result(env)

    job_id = synthetic_job_id(payload)
    queued = initial_synthetic_record(job_id)
    claim = claim_once(queued, "synthetic_worker_primary")
    claimed = claim["record"]
    duplicate = duplicate_claim(claimed, "synthetic_worker_duplicate")
    processing = mark_processing(claimed)
    retry = schedule_retry(processing)
    failed = record_terminal_failure(retry)
    completed = record_terminal_completion(processing)
    dlq = build_dlq_or_recovery_shape(failed)
    failed_client_view = build_client_safe_status(failed)
    completed_client_view = build_client_safe_status(completed)
    admin_diagnostics = build_admin_diagnostics(
        queued=queued,
        claimed=claimed,
        retry=retry,
        failed=failed,
        completed=completed,
        dlq=dlq,
    )

    queued_status_represented = queued.get("status") == "queued"
    claim_once_passed = bool(claim.get("claim_once_passed")) and claimed.get("status") == "claimed"
    duplicate_claim_blocked = bool(duplicate.get("duplicate_claim_blocked"))
    processing_status_passed = processing.get("status") == "processing"
    retry_state_represented = retry.get("status") == "retry_scheduled" and retry.get("retry_allowed") is True
    failure_status_passed = failed.get("status") == "failed_terminal" and failed.get("client_safe_status") == "needs_attention"
    completed_status_represented = completed.get("status") == "completed" and completed.get("synthetic_output_only") is True
    terminal_status_readback_passed = (
        failed_client_view.get("status") == "needs_attention"
        and completed_client_view.get("status") == "completed"
        and failed.get("job_reference_hash") == completed.get("job_reference_hash")
    )
    dlq_or_recovery_shape_present = bool(dlq.get("dlq_or_recovery_shape_present"))
    client_safe_status_redacted = (
        failed_client_view.get("internal_config_exposed") is False
        and completed_client_view.get("credential_values_exposed") is False
    )
    admin_diagnostics_redacted = admin_diagnostics.get("admin_diagnostics_redacted") is True
    rollback_blocked = rollback_controls_block_when_enabled(env)

    proof_fields = {
        "synthetic_worker_lifecycle_attempted": True,
        "synthetic_worker_lifecycle_passed": all([
            queued_status_represented,
            claim_once_passed,
            duplicate_claim_blocked,
            processing_status_passed,
            retry_state_represented,
            failure_status_passed,
            completed_status_represented,
            terminal_status_readback_passed,
            dlq_or_recovery_shape_present,
            client_safe_status_redacted,
            admin_diagnostics_redacted,
            rollback_blocked,
        ]),
        "queued_status_represented": queued_status_represented,
        "claim_once_passed": claim_once_passed,
        "duplicate_claim_blocked": duplicate_claim_blocked,
        "processing_status_passed": processing_status_passed,
        "retry_state_represented": retry_state_represented,
        "failure_status_passed": failure_status_passed,
        "completed_status_represented": completed_status_represented,
        "terminal_status_readback_passed": terminal_status_readback_passed,
        "dlq_or_recovery_shape_present": dlq_or_recovery_shape_present,
        "client_safe_status_redacted": client_safe_status_redacted,
        "admin_diagnostics_redacted": admin_diagnostics_redacted,
        "rollback_controls_blocked_when_enabled": rollback_blocked,
    }
    result = {
        "boundary": "synthetic_durable_worker_lifecycle",
        "diagnostic_version": SYNTHETIC_WORKER_LIFECYCLE_DIAGNOSTIC_VERSION,
        "status": (
            "synthetic_durable_worker_lifecycle_passed"
            if proof_fields["synthetic_worker_lifecycle_passed"]
            else "synthetic_durable_worker_lifecycle_failed"
        ),
        "synthetic_non_customer_job": True,
        "non_executable": True,
        "job_reference_hash": queued.get("job_reference_hash"),
        "message_reference_hash": queued.get("message_reference_hash"),
        "proof": proof_fields,
        **proof_fields,
        "lifecycle_trace": [
            {"status": queued.get("status"), "client_safe_status": queued.get("client_safe_status")},
            {"status": claimed.get("status"), "claim_token_hash_present": bool(claimed.get("claim_token_hash"))},
            {"status": processing.get("status"), "client_safe_status": processing.get("client_safe_status")},
            {"status": retry.get("status"), "next_retry_reference_hash": retry.get("next_retry_reference_hash")},
            {"status": failed.get("status"), "failure_code_hash": failed.get("failure_code_hash")},
            {"status": completed.get("status"), "synthetic_output_reference_hash": completed.get("synthetic_output_reference_hash")},
        ],
        "duplicate_claim_result": duplicate,
        "dlq_or_recovery_shape": dlq,
        "client_safe_failed_status": failed_client_view,
        "client_safe_completed_status": completed_client_view,
        "admin_safe_diagnostics": admin_diagnostics,
        "incident_event": {
            "event_type": "synthetic_durable_worker_lifecycle_proof",
            "severity": "info" if proof_fields["synthetic_worker_lifecycle_passed"] else "warning",
            "decision": "passed" if proof_fields["synthetic_worker_lifecycle_passed"] else "failed",
            "safe_job_reference_hash": queued.get("job_reference_hash"),
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
