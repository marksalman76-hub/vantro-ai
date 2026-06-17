from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import re
from typing import Any, Dict, Mapping


DIAGNOSTIC_VERSION = "aws_option_a_observability_v1"

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


def first_value(payload: Mapping[str, Any], keys: tuple[str, ...], default: Any = "") -> Any:
    for key in keys:
        value = payload.get(key)
        if value not in (None, ""):
            return value
    return default


def safe_hash(value: Any) -> str:
    text = clean_text(value, 1000)
    if not text:
        return ""
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()[:16]


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
    text = re.sub(r"\s+", " ", text).strip()
    return text[:limit]


def redact_secret_values(value: Any) -> Any:
    if isinstance(value, dict):
        cleaned: Dict[str, Any] = {}
        for key, item in value.items():
            key_l = str(key).lower()
            if isinstance(item, bool):
                cleaned[key] = item
            elif any(marker in key_l for marker in SECRET_KEY_MARKERS):
                cleaned[key] = "[redacted]"
            else:
                cleaned[key] = redact_secret_values(item)
        return cleaned
    if isinstance(value, list):
        return [redact_secret_values(item) for item in value]
    if isinstance(value, str):
        return sanitize_text(value, 1000)
    return value


def validation_summary_from_evaluation(evaluation: Mapping[str, Any]) -> Dict[str, Any]:
    decision = evaluation.get("decision") if isinstance(evaluation.get("decision"), dict) else {}
    summary = decision.get("validation_summary") if isinstance(decision.get("validation_summary"), dict) else {}
    service_results = summary.get("service_results") if isinstance(summary.get("service_results"), dict) else {}
    statuses = {
        service: clean_text(result.get("status") if isinstance(result, dict) else result, 80)
        for service, result in service_results.items()
    }
    evidence_present = bool(statuses) and any(status and status != "missing" for status in statuses.values())
    return {
        "aws_validation_evidence_present": evidence_present,
        "aws_route_validation_passed": bool(summary.get("validation_ready")),
        "service_statuses": statuses,
        "missing_or_failed_services": [
            clean_text(item, 80)
            for item in summary.get("missing_or_failed_services") or []
            if clean_text(item)
        ],
    }


def planning_state(evaluation: Mapping[str, Any]) -> Dict[str, Any]:
    boundary = evaluation.get("aws17_durable_enqueue") if isinstance(evaluation.get("aws17_durable_enqueue"), dict) else {}
    durable = boundary.get("durable_repository") if isinstance(boundary.get("durable_repository"), dict) else {}
    queue = boundary.get("queue_enqueue") if isinstance(boundary.get("queue_enqueue"), dict) else {}
    status = boundary.get("status_persistence") if isinstance(boundary.get("status_persistence"), dict) else {}
    route_ready = bool(evaluation.get("route_execution_allowed"))
    durable_flag_enabled = bool(durable.get("durable_write_enabled"))
    queue_flag_enabled = bool(queue.get("queue_send_enabled"))
    return {
        "durable_write_flag_enabled": durable_flag_enabled,
        "queue_send_flag_enabled": queue_flag_enabled,
        "durable_write_would_execute": bool(route_ready and durable_flag_enabled and durable.get("prepared")),
        "queue_send_would_execute": bool(route_ready and queue_flag_enabled and queue.get("prepared")),
        "durable_dry_run_prepared": bool(durable.get("prepared")),
        "queue_dry_run_prepared": bool(queue.get("prepared")),
        "durable_planning_state": clean_text(durable.get("status") or "not_planned", 120),
        "queue_planning_state": clean_text(queue.get("status") or "not_planned", 120),
        "status_read_state": clean_text(status.get("status") or "not_planned", 120),
        "status_read_source_planned": clean_text(status.get("status") or "not_planned", 120),
        "rds_write_attempted": False,
        "sqs_send_attempted": False,
        "s3_upload_attempted": False,
        "secret_fetch_attempted": False,
        "provider_call_attempted": False,
        "stripe_call_attempted": False,
        "credit_mutation_attempted": False,
    }


def reason_code(evaluation: Mapping[str, Any], validation: Mapping[str, Any], planning: Mapping[str, Any]) -> str:
    decision = evaluation.get("decision") if isinstance(evaluation.get("decision"), dict) else {}
    if evaluation.get("kill_switch_active"):
        return "rollback_kill_switch_active"
    if evaluation.get("force_compatibility_fallback"):
        return "force_compatibility_fallback"
    if not evaluation.get("aws_route_cutover_intent"):
        return "compatibility_default"
    if not validation.get("aws_validation_evidence_present"):
        return "aws_validation_missing"
    if not validation.get("aws_route_validation_passed"):
        return "aws_validation_missing"
    if not evaluation.get("request_authority_allowed"):
        return "client_governance_required"
    if not evaluation.get("route_execution_allowed") and "api_acceptance_entitlement_allowed" in (decision.get("missing_gates") or []):
        return "entitlement_blocked"
    if clean_text(evaluation.get("route_kind")) == "status" and planning.get("status_read_state") == "durable_status_read_dry_run_prepared":
        return "status_read_dry_run"
    if evaluation.get("route_execution_allowed") and planning.get("durable_dry_run_prepared") and planning.get("queue_dry_run_prepared"):
        return "aws_route_ready_dry_run"
    if not planning.get("durable_write_flag_enabled"):
        return "durable_write_disabled"
    if not planning.get("queue_send_flag_enabled"):
        return "queue_send_disabled"
    return "aws_route_not_requested"


def next_operator_action(code: str) -> str:
    actions = {
        "compatibility_default": "Current compatibility runtime is active. No AWS route action is required.",
        "aws_route_not_requested": "Confirm the intended AWS route flags before routing traffic.",
        "aws_validation_missing": "Run safe AWS validation and attach passing validation evidence before route cutover.",
        "aws_route_ready_dry_run": "Review dry-run durable and queue plans before approving any live adapter test.",
        "rollback_kill_switch_active": "Keep compatibility fallback active until the incident owner clears the kill switch.",
        "force_compatibility_fallback": "Compatibility fallback is forced. Review incident context before clearing fallback.",
        "durable_write_disabled": "Durable write remains disabled; this is safe for dry-run route review.",
        "queue_send_disabled": "Queue send remains disabled; this is safe for dry-run route review.",
        "status_read_dry_run": "Status reads are planned as dry-run only; no RDS read has occurred.",
        "client_governance_required": "Client package, credit, approval, or agent access must be resolved before paid execution.",
        "entitlement_blocked": "Entitlement is blocking route execution; keep client-safe messaging generic.",
    }
    return actions.get(code, "Support can review this request using admin diagnostics.")


def build_admin_diagnostic_snapshot(payload: Mapping[str, Any], evaluation: Mapping[str, Any]) -> Dict[str, Any]:
    validation = validation_summary_from_evaluation(evaluation)
    planning = planning_state(evaluation)
    code = reason_code(evaluation, validation, planning)
    job_id = first_value(payload, ("job_id", "parent_job_id", "id"), "")
    selected_agent = first_value(payload, ("selected_agent", "agent_id"), "")
    snapshot = {
        "boundary": "aws19_observability_boundary",
        "diagnostic_version": DIAGNOSTIC_VERSION,
        "route_kind": clean_text(evaluation.get("route_kind"), 80),
        "route_mode": clean_text(evaluation.get("route_mode"), 120),
        "status": clean_text(evaluation.get("status"), 120),
        "compatibility_default_active": bool(
            not evaluation.get("aws_route_cutover_intent")
            and clean_text(evaluation.get("route_mode")) == "compatibility_runtime_path"
        ),
        "aws_route_intent_detected": bool(evaluation.get("aws_route_cutover_intent")),
        "aws_validation_evidence_present": validation["aws_validation_evidence_present"],
        "aws_route_validation_passed": validation["aws_route_validation_passed"],
        "validation_service_statuses": validation["service_statuses"],
        "missing_or_failed_validation_services": validation["missing_or_failed_services"],
        "rollback_control_active": bool(evaluation.get("rollback_control_active")),
        "kill_switch_active": bool(evaluation.get("kill_switch_active")),
        "force_compatibility_fallback": bool(evaluation.get("force_compatibility_fallback")),
        "aws_route_blocked_by_rollback": bool(evaluation.get("aws_route_blocked_by_rollback")),
        "compatibility_fallback_selected": bool(evaluation.get("compatibility_fallback_selected")),
        "job_id_present": bool(clean_text(job_id)),
        "safe_job_reference_hash": safe_hash(job_id),
        "media_type": clean_text(first_value(payload, ("media_type", "output_type"), ""), 120),
        "asset_type": clean_text(first_value(payload, ("asset_type", "output_asset_type"), ""), 120),
        "agent_id_present": bool(clean_text(selected_agent)),
        "incident_hint": code,
        "next_operator_action": next_operator_action(code),
        "customer_safe": True,
        "external_logging_attempted": False,
        "cloudwatch_put_attempted": False,
        "live_routes_switched": False,
        **planning,
    }
    return redact_secret_values(snapshot)


def build_client_diagnostic_snapshot(payload: Mapping[str, Any], evaluation: Mapping[str, Any]) -> Dict[str, Any]:
    route_blocked = bool(evaluation.get("aws_route_blocked_by_rollback"))
    status = "current_runtime_active" if route_blocked or not evaluation.get("route_execution_allowed") else "processing_ready"
    message = (
        "This request will use the current production runtime path."
        if route_blocked
        else "Support can review this request if needed."
    )
    job_id = clean_text(first_value(payload, ("job_id", "parent_job_id", "id"), ""), 180)
    return {
        "status": status,
        "message": message,
        "job_reference_present": bool(job_id),
        "customer_safe": True,
        "external_calls_started": False,
        "paid_provider_calls_started": False,
        "billing_mutation_attempted": False,
        "credit_mutation_attempted": False,
        "sensitive_values_exposed": False,
        "internal_config_exposed": False,
    }


def build_incident_event(payload: Mapping[str, Any], evaluation: Mapping[str, Any], admin_snapshot: Mapping[str, Any]) -> Dict[str, Any]:
    job_id = first_value(payload, ("job_id", "parent_job_id", "id"), "")
    event = {
        "event_type": "aws_option_a_route_observability_snapshot_prepared",
        "severity": "warning" if admin_snapshot.get("aws_route_blocked_by_rollback") or not admin_snapshot.get("aws_route_validation_passed") else "info",
        "route_mode": admin_snapshot.get("route_mode"),
        "decision": admin_snapshot.get("incident_hint"),
        "blocked_reason_code": admin_snapshot.get("incident_hint"),
        "fallback_selected": bool(admin_snapshot.get("compatibility_fallback_selected")),
        "rollback_control_active": bool(admin_snapshot.get("rollback_control_active")),
        "durable_planning_state": admin_snapshot.get("durable_planning_state"),
        "queue_planning_state": admin_snapshot.get("queue_planning_state"),
        "status_read_state": admin_snapshot.get("status_read_state"),
        "safe_job_reference_hash": safe_hash(job_id),
        "timestamp": utc_now(),
        "diagnostic_version": DIAGNOSTIC_VERSION,
        "external_logging_attempted": False,
        "cloudwatch_put_attempted": False,
        "rds_write_attempted": False,
        "sqs_send_attempted": False,
        "s3_upload_attempted": False,
        "secret_fetch_attempted": False,
        "provider_call_attempted": False,
        "stripe_call_attempted": False,
        "credit_mutation_attempted": False,
        "customer_safe": True,
    }
    return redact_secret_values(event)


def build_aws_option_a_observability_bundle(
    *,
    payload: Mapping[str, Any] | None = None,
    evaluation: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    payload = dict(payload or {})
    evaluation = dict(evaluation or {})
    admin_snapshot = build_admin_diagnostic_snapshot(payload, evaluation)
    client_snapshot = build_client_diagnostic_snapshot(payload, evaluation)
    incident_event = build_incident_event(payload, evaluation, admin_snapshot)
    return redact_secret_values({
        "boundary": "aws19_observability_boundary",
        "diagnostic_version": DIAGNOSTIC_VERSION,
        "admin_diagnostic_snapshot": admin_snapshot,
        "client_diagnostic_snapshot": client_snapshot,
        "incident_event": incident_event,
        "observability_alters_route_decision": False,
        "external_logging_attempted": False,
        "cloudwatch_put_attempted": False,
        "rds_write_attempted": False,
        "sqs_send_attempted": False,
        "s3_upload_attempted": False,
        "secret_fetch_attempted": False,
        "provider_call_attempted": False,
        "stripe_call_attempted": False,
        "credit_mutation_attempted": False,
        "customer_safe": True,
    })
