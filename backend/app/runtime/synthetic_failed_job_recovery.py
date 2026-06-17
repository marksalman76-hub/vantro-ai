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


SYNTHETIC_FAILED_JOB_RECOVERY_DIAGNOSTIC_VERSION = "synthetic_failed_job_recovery_v1"
SYNTHETIC_FAILED_JOB_PREFIX = "synthetic_failed_recovery_non_customer"
TRUE_VALUES = {"1", "true", "yes", "on", "enabled"}

SECRET_KEY_MARKERS = (
    "api_key",
    "apikey",
    "authorization",
    "bearer",
    "bucket",
    "credential",
    "database_url",
    "dlq_url",
    "object_key",
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
        r"(?i)\b(?:[a-z0-9]+[_-])*(?:aws_access_key_id|aws_secret_access_key|aws_session_token|api[_-]?key|authorization|bearer|bucket|credential|database_url|dlq_url|object_key|password|private_key|provider[_-]?api[_-]?key|queue[_-]?url|rds_password|secret|stripe[_-]?secret[_-]?key|token)\b\s*[:=]?\s*[^\s,;]*",
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
                if key_l.endswith("_present") or "hash" in key_l or key_l.endswith("_length") or key_l.endswith("_redacted"):
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


def synthetic_failed_job_id(payload: Optional[Mapping[str, Any]] = None) -> str:
    supplied = clean_text((payload or {}).get("job_id"), 180)
    if supplied and supplied.startswith(SYNTHETIC_FAILED_JOB_PREFIX):
        return supplied
    return f"{SYNTHETIC_FAILED_JOB_PREFIX}_{uuid.uuid4().hex[:12]}"


def base_side_effect_guards() -> Dict[str, bool]:
    return {
        "live_worker_loop_started": False,
        "worker_started": False,
        "worker_loop_started": False,
        "customer_queue_message_consumed": False,
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
        "customer_traffic_started": False,
        "public_cutover_enabled": False,
        "public_production_cutover_enabled": False,
        "secret_fetch_attempted": False,
        "secrets_manager_value_retrieved": False,
        "live_recovery_execution_attempted": False,
    }


def rollback_controls_block_when_enabled(env: Mapping[str, Any]) -> bool:
    rollback_env = dict(env)
    rollback_env[AWS_OPTION_A_KILL_SWITCH_ENABLED_FLAG] = "true"
    decision = build_aws_option_a_rollback_control_decision(
        env=rollback_env,
        route_kind="synthetic_failed_job_recovery",
        route_intent=True,
        route_execution_allowed=True,
        selected_runtime_path="synthetic_failed_job_recovery_boundary",
        route_mode="synthetic_failed_job_recovery_proof",
    )
    return bool(decision.get("aws_route_blocked_by_rollback"))


def rollback_active(env: Mapping[str, Any]) -> bool:
    decision = build_aws_option_a_rollback_control_decision(
        env=env,
        route_kind="synthetic_failed_job_recovery",
        route_intent=True,
        route_execution_allowed=True,
        selected_runtime_path="synthetic_failed_job_recovery_boundary",
        route_mode="synthetic_failed_job_recovery_proof",
    )
    return bool(decision.get("aws_route_blocked_by_rollback"))


def build_failure_classification(job_reference_hash: str) -> Dict[str, Any]:
    return {
        "classification": "synthetic_worker_execution_failure",
        "safe_reason_code": "synthetic_retry_exhausted_without_provider",
        "severity": "recoverable_by_admin_review",
        "job_reference_hash": job_reference_hash,
        "provider_execution_attempted": False,
        "customer_data_involved": False,
        "diagnostics_redacted": True,
    }


def build_retry_exhaustion(job_reference_hash: str) -> Dict[str, Any]:
    return {
        "max_attempts": 3,
        "attempts_represented": 3,
        "retry_exhausted": True,
        "retry_policy": "synthetic_retry_policy_no_provider_calls",
        "retry_history": [
            {
                "attempt_number": number,
                "attempt_reference_hash": safe_hash(f"{job_reference_hash}:attempt:{number}"),
                "provider_call_attempted": False,
                "billing_mutation_attempted": False,
                "credit_mutation_attempted": False,
            }
            for number in (1, 2, 3)
        ],
    }


def build_dlq_shape(job_reference_hash: str) -> Dict[str, Any]:
    dlq_reference_seed = f"{job_reference_hash}:synthetic-dlq"
    return {
        "dlq_shape_present": True,
        "dlq_name": "synthetic_media_failed_job_recovery",
        "dlq_reference_hash": safe_hash(dlq_reference_seed),
        "dlq_reference_redacted": True,
        "dlq_message_non_customer": True,
        "dlq_message_non_executable": True,
        "dlq_handoff_simulated": True,
        "customer_queue_message_consumed": False,
        "sqs_send_attempted": False,
        "provider_call_attempted": False,
        "media_generation_attempted": False,
    }


def build_admin_recovery_action(job_reference_hash: str, dlq_reference_hash: str) -> Dict[str, Any]:
    return {
        "action_type": "requeue_synthetic_failed_job",
        "action_represented": True,
        "execution_mode": "represented_only_no_live_requeue",
        "job_reference_hash": job_reference_hash,
        "dlq_reference_hash": dlq_reference_hash,
        "operator_note": "Admin can inspect redacted diagnostics, requeue safely, or keep the job terminal failed.",
        "requires_owner_approval_for_live_execution": True,
        "live_worker_loop_started": False,
        "customer_queue_message_consumed": False,
        "provider_call_attempted": False,
        "billing_mutation_attempted": False,
        "credit_mutation_attempted": False,
    }


def build_client_safe_failed_status(job_reference_hash: str) -> Dict[str, Any]:
    return {
        "status": "needs_attention",
        "message": "This job could not be completed. Support has a safe recovery record.",
        "job_reference_hash": job_reference_hash,
        "customer_safe": True,
        "internal_config_exposed": False,
        "credential_values_exposed": False,
        "provider_secret_values_visible": False,
        "admin_diagnostics_visible": False,
    }


def build_terminal_failed_readback(job_reference_hash: str) -> Dict[str, Any]:
    return {
        "status": "failed_terminal",
        "client_safe_status": "needs_attention",
        "job_reference_hash": job_reference_hash,
        "terminal_state_readback": True,
        "safe_error_summary": "Synthetic failed job reached a safe terminal failed state after retry exhaustion.",
        "diagnostics_redacted": True,
    }


def build_recovered_or_requeued_state(job_reference_hash: str) -> Dict[str, Any]:
    return {
        "status": "requeued_synthetic",
        "client_safe_status": "running",
        "job_reference_hash": job_reference_hash,
        "recovery_reference_hash": safe_hash(f"{job_reference_hash}:recovered"),
        "recovered_or_requeued_state_represented": True,
        "synthetic_output_only": True,
        "provider_call_attempted": False,
        "media_generation_attempted": False,
    }


def build_terminal_recovered_or_completed(job_reference_hash: str) -> Dict[str, Any]:
    return {
        "status": "completed_synthetic_recovery",
        "client_safe_status": "completed",
        "job_reference_hash": job_reference_hash,
        "terminal_recovered_or_completed_represented": True,
        "synthetic_output_only": True,
        "synthetic_output_reference_hash": safe_hash(f"{job_reference_hash}:synthetic-recovery-output"),
        "asset_delivery_started": False,
        "provider_call_attempted": False,
        "media_generation_attempted": False,
    }


def build_admin_diagnostics(
    *,
    job_reference_hash: str,
    failure_classification: Mapping[str, Any],
    retry_exhaustion: Mapping[str, Any],
    dlq_shape: Mapping[str, Any],
    admin_recovery_action: Mapping[str, Any],
    terminal_failed: Mapping[str, Any],
    terminal_recovered: Mapping[str, Any],
) -> Dict[str, Any]:
    return {
        "diagnostic_version": SYNTHETIC_FAILED_JOB_RECOVERY_DIAGNOSTIC_VERSION,
        "job_reference_hash": job_reference_hash,
        "failure_classification": failure_classification.get("classification"),
        "safe_reason_code": failure_classification.get("safe_reason_code"),
        "retry_exhausted": bool(retry_exhaustion.get("retry_exhausted")),
        "dlq_reference_hash": dlq_shape.get("dlq_reference_hash"),
        "dlq_reference_redacted": bool(dlq_shape.get("dlq_reference_redacted")),
        "admin_recovery_action": admin_recovery_action.get("action_type"),
        "terminal_failed_status": terminal_failed.get("status"),
        "terminal_recovered_status": terminal_recovered.get("status"),
        "recommended_operator_next_step": "Review redacted diagnostics, then choose requeue or keep terminal failed.",
        "admin_diagnostics_redacted": True,
        "credential_values_exposed": False,
        "secret_values_exposed": False,
        "raw_infrastructure_identifiers_exposed": False,
    }


def build_blocked_by_rollback_result(env: Mapping[str, Any]) -> Dict[str, Any]:
    result = {
        "boundary": "synthetic_failed_job_recovery",
        "diagnostic_version": SYNTHETIC_FAILED_JOB_RECOVERY_DIAGNOSTIC_VERSION,
        "status": "blocked_by_rollback_control",
        "blocked_reason": "blocked_by_rollback_control",
        "synthetic_failed_job_recovery_attempted": False,
        "synthetic_failed_job_recovery_passed": False,
        "failure_classification_passed": False,
        "retry_exhaustion_represented": False,
        "dlq_shape_present": False,
        "dlq_reference_redacted": True,
        "admin_recovery_action_represented": False,
        "client_safe_failed_status_redacted": True,
        "admin_diagnostics_redacted": True,
        "recovered_or_requeued_state_represented": False,
        "terminal_failed_readback_passed": False,
        "terminal_recovered_or_completed_represented": False,
        "rollback_controls_blocked_when_enabled": rollback_controls_block_when_enabled(env),
        "synthetic_non_customer_job": True,
        "client_safe_failed_status": {
            "status": "current_runtime_active",
            "message": "Recovery execution is paused by an operator safety control.",
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


def build_synthetic_failed_job_recovery_proof(
    *,
    env: Optional[Mapping[str, Any]] = None,
    payload: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    env = dict(env or {})
    if rollback_active(env):
        return build_blocked_by_rollback_result(env)

    job_id = synthetic_failed_job_id(payload)
    job_reference_hash = safe_hash(job_id)
    failure_classification = build_failure_classification(job_reference_hash)
    retry_exhaustion = build_retry_exhaustion(job_reference_hash)
    dlq_shape = build_dlq_shape(job_reference_hash)
    admin_recovery_action = build_admin_recovery_action(job_reference_hash, clean_text(dlq_shape.get("dlq_reference_hash"), 80))
    client_safe_failed_status = build_client_safe_failed_status(job_reference_hash)
    terminal_failed_readback = build_terminal_failed_readback(job_reference_hash)
    recovered_or_requeued_state = build_recovered_or_requeued_state(job_reference_hash)
    terminal_recovered_or_completed = build_terminal_recovered_or_completed(job_reference_hash)
    admin_diagnostics = build_admin_diagnostics(
        job_reference_hash=job_reference_hash,
        failure_classification=failure_classification,
        retry_exhaustion=retry_exhaustion,
        dlq_shape=dlq_shape,
        admin_recovery_action=admin_recovery_action,
        terminal_failed=terminal_failed_readback,
        terminal_recovered=terminal_recovered_or_completed,
    )

    failure_classification_passed = (
        failure_classification.get("classification") == "synthetic_worker_execution_failure"
        and failure_classification.get("provider_execution_attempted") is False
    )
    retry_exhaustion_represented = (
        retry_exhaustion.get("retry_exhausted") is True
        and retry_exhaustion.get("attempts_represented") == retry_exhaustion.get("max_attempts")
    )
    dlq_shape_present = bool(dlq_shape.get("dlq_shape_present"))
    dlq_reference_redacted = bool(dlq_shape.get("dlq_reference_redacted")) and bool(dlq_shape.get("dlq_reference_hash"))
    admin_recovery_action_represented = bool(admin_recovery_action.get("action_represented"))
    client_safe_failed_status_redacted = (
        client_safe_failed_status.get("customer_safe") is True
        and client_safe_failed_status.get("internal_config_exposed") is False
        and client_safe_failed_status.get("credential_values_exposed") is False
    )
    admin_diagnostics_redacted = admin_diagnostics.get("admin_diagnostics_redacted") is True
    recovered_or_requeued_state_represented = bool(
        recovered_or_requeued_state.get("recovered_or_requeued_state_represented")
    )
    terminal_failed_readback_passed = (
        terminal_failed_readback.get("terminal_state_readback") is True
        and terminal_failed_readback.get("status") == "failed_terminal"
    )
    terminal_recovered_or_completed_represented = bool(
        terminal_recovered_or_completed.get("terminal_recovered_or_completed_represented")
    )
    rollback_blocked = rollback_controls_block_when_enabled(env)

    proof_fields = {
        "synthetic_failed_job_recovery_attempted": True,
        "synthetic_failed_job_recovery_passed": all([
            failure_classification_passed,
            retry_exhaustion_represented,
            dlq_shape_present,
            dlq_reference_redacted,
            admin_recovery_action_represented,
            client_safe_failed_status_redacted,
            admin_diagnostics_redacted,
            recovered_or_requeued_state_represented,
            terminal_failed_readback_passed,
            terminal_recovered_or_completed_represented,
            rollback_blocked,
        ]),
        "failure_classification_passed": failure_classification_passed,
        "retry_exhaustion_represented": retry_exhaustion_represented,
        "dlq_shape_present": dlq_shape_present,
        "dlq_reference_redacted": dlq_reference_redacted,
        "admin_recovery_action_represented": admin_recovery_action_represented,
        "client_safe_failed_status_redacted": client_safe_failed_status_redacted,
        "admin_diagnostics_redacted": admin_diagnostics_redacted,
        "recovered_or_requeued_state_represented": recovered_or_requeued_state_represented,
        "terminal_failed_readback_passed": terminal_failed_readback_passed,
        "terminal_recovered_or_completed_represented": terminal_recovered_or_completed_represented,
        "rollback_controls_blocked_when_enabled": rollback_blocked,
    }

    result = {
        "boundary": "synthetic_failed_job_recovery",
        "diagnostic_version": SYNTHETIC_FAILED_JOB_RECOVERY_DIAGNOSTIC_VERSION,
        "status": (
            "synthetic_failed_job_recovery_passed"
            if proof_fields["synthetic_failed_job_recovery_passed"]
            else "synthetic_failed_job_recovery_failed"
        ),
        "synthetic_non_customer_job": True,
        "non_executable": True,
        "job_reference_hash": job_reference_hash,
        "proof": proof_fields,
        **proof_fields,
        "failure_classification": failure_classification,
        "retry_exhaustion": retry_exhaustion,
        "dlq_shape": dlq_shape,
        "admin_recovery_action": admin_recovery_action,
        "client_safe_failed_status": client_safe_failed_status,
        "terminal_failed_readback": terminal_failed_readback,
        "recovered_or_requeued_state": recovered_or_requeued_state,
        "terminal_recovered_or_completed": terminal_recovered_or_completed,
        "admin_safe_diagnostics": admin_diagnostics,
        "incident_event": {
            "event_type": "synthetic_failed_job_recovery_proof",
            "severity": "info" if proof_fields["synthetic_failed_job_recovery_passed"] else "warning",
            "decision": "passed" if proof_fields["synthetic_failed_job_recovery_passed"] else "failed",
            "safe_job_reference_hash": job_reference_hash,
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
