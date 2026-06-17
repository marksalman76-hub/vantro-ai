from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Mapping, Optional

from backend.app.runtime.aws_option_a_route_cutover_boundary import (
    AWS_ACCEPTANCE_CUTOVER_ENABLED_FLAG,
    AWS_OPTION_A_ENABLED_FLAG,
    AWS_ROUTE_CUTOVER_ENABLED_FLAG,
    AWS_STATUS_CUTOVER_ENABLED_FLAG,
    ROUTE_KIND_ACCEPTANCE,
    ROUTE_KIND_STATUS,
    ROUTE_MODE_DRY_RUN,
    ROUTE_MODE_ENABLED_MISSING_VALIDATION,
    ROUTE_MODE_ENABLED_READY,
    ROUTE_MODE_LIVE_READY_DISABLED,
    decide_api_acceptance_route_cutover,
    decide_api_status_route_cutover,
    enabled,
    redact_secret_values,
)
from backend.app.runtime.durable_media_job_status_adapter import build_durable_media_job_status_record
from backend.app.runtime.media_queue_adapter_boundary import build_media_queue_message, validate_media_queue_message
from backend.app.runtime.rds_repository_persistence_boundary import build_repository_operation_result


DIAGNOSTIC_TRUE_VALUES = {"1", "true", "yes", "on", "enabled", "admin"}
AWS_DURABLE_WRITE_ENABLED_FLAG = "AWS_OPTION_A_DURABLE_WRITE_ENABLED"
AWS_QUEUE_SEND_ENABLED_FLAG = "AWS_OPTION_A_QUEUE_SEND_ENABLED"
VALIDATION_EVIDENCE_KEYS = (
    "aws_option_a_validation_evidence",
    "aws_validation_evidence",
    "validation_evidence",
    "route_validation_evidence",
)
DIAGNOSTIC_KEYS = (
    "include_route_mode_diagnostics",
    "route_mode_diagnostics",
    "aws_route_diagnostics",
    "include_aws_route_diagnostics",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def clean_text(value: Any, limit: int = 1000) -> str:
    return str(value or "").strip()[:limit]


def clean_bool(value: Any) -> bool:
    return str(value or "").strip().lower() in DIAGNOSTIC_TRUE_VALUES


def normalise_audience(audience: Any) -> str:
    audience_clean = clean_text(audience or "admin", 80).lower()
    return "client" if audience_clean == "client" else "admin"


def mapping_get(mapping: Any, key: str, default: Any = None) -> Any:
    try:
        return mapping.get(key, default)
    except Exception:
        return default


def diagnostics_requested(
    *,
    payload: Optional[Mapping[str, Any]] = None,
    query_params: Optional[Mapping[str, Any]] = None,
    headers: Optional[Mapping[str, Any]] = None,
) -> bool:
    payload = payload or {}
    query_params = query_params or {}
    headers = headers or {}
    for key in DIAGNOSTIC_KEYS:
        if clean_bool(mapping_get(payload, key)) or clean_bool(mapping_get(query_params, key)):
            return True
    for key in (
        "x-aws-route-diagnostics",
        "x-route-mode-diagnostics",
        "x-admin-route-diagnostics",
    ):
        if clean_bool(mapping_get(headers, key)):
            return True
    return False


def extract_validation_evidence(payload: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    payload = payload or {}
    for key in VALIDATION_EVIDENCE_KEYS:
        evidence = payload.get(key)
        if isinstance(evidence, dict):
            return evidence
    return {}


def operation_flag_for_route_kind(route_kind: str) -> str:
    return AWS_ACCEPTANCE_CUTOVER_ENABLED_FLAG if route_kind == ROUTE_KIND_ACCEPTANCE else AWS_STATUS_CUTOVER_ENABLED_FLAG


def aws_route_cutover_intent(env: Optional[Mapping[str, Any]], route_kind: str) -> bool:
    env = env or {}
    if not enabled(env.get(AWS_OPTION_A_ENABLED_FLAG)):
        return False
    operation_flag = operation_flag_for_route_kind(route_kind)
    return bool(enabled(env.get(AWS_ROUTE_CUTOVER_ENABLED_FLAG)) or enabled(env.get(operation_flag)))


def durable_write_enabled(env: Optional[Mapping[str, Any]]) -> bool:
    return enabled((env or {}).get(AWS_DURABLE_WRITE_ENABLED_FLAG))


def queue_send_enabled(env: Optional[Mapping[str, Any]]) -> bool:
    return enabled((env or {}).get(AWS_QUEUE_SEND_ENABLED_FLAG))


def route_should_short_circuit(decision: Mapping[str, Any], route_intent: bool) -> bool:
    if not route_intent:
        return False
    return clean_text(decision.get("route_mode")) in {
        ROUTE_MODE_ENABLED_MISSING_VALIDATION,
        ROUTE_MODE_LIVE_READY_DISABLED,
        ROUTE_MODE_ENABLED_READY,
    }


def first_value(payload: Mapping[str, Any], keys: tuple[str, ...], default: Any = "") -> Any:
    for key in keys:
        value = payload.get(key)
        if value not in (None, ""):
            return value
    return default


def clean_int(value: Any, default: int = 0) -> int:
    try:
        return int(float(value))
    except Exception:
        return default


def ensure_list(value: Any) -> list[str]:
    if isinstance(value, list):
        items = value
    elif isinstance(value, tuple):
        items = list(value)
    elif clean_text(value):
        items = [value]
    else:
        items = []
    result: list[str] = []
    for item in items:
        clean = clean_text(item, 180)
        if clean and clean not in result:
            result.append(clean)
    return result


def route_mode_metadata(evaluation_or_decision: Mapping[str, Any], route_kind: str = "") -> Dict[str, Any]:
    return {
        "boundary": "aws17_durable_enqueue_dry_run_boundary",
        "route_kind": clean_text(evaluation_or_decision.get("route_kind") or route_kind, 80),
        "route_mode": clean_text(evaluation_or_decision.get("route_mode"), 120),
        "selected_runtime_path": clean_text(evaluation_or_decision.get("selected_runtime_path"), 180),
        "route_execution_allowed": bool(evaluation_or_decision.get("route_execution_allowed")),
        "live_routes_switched": False,
        "rds_write_attempted": False,
        "sqs_send_attempted": False,
        "aws_call_attempted": False,
        "provider_call_attempted": False,
        "stripe_call_attempted": False,
        "credit_mutation_attempted": False,
        "customer_safe": True,
    }


def durable_repository_not_prepared(reason: str) -> Dict[str, Any]:
    return {
        "status": "durable_repository_not_prepared",
        "reason": clean_text(reason, 180),
        "prepared": False,
        "durable_write_enabled": False,
        "durable_write_flag": AWS_DURABLE_WRITE_ENABLED_FLAG,
        "rds_write_attempted": False,
        "db_connection_attempted": False,
        "migration_attempted": False,
        "aws_call_attempted": False,
        "provider_call_attempted": False,
        "stripe_call_attempted": False,
        "credit_mutation_attempted": False,
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def queue_enqueue_not_prepared(reason: str) -> Dict[str, Any]:
    return {
        "status": "queue_enqueue_not_prepared",
        "reason": clean_text(reason, 180),
        "prepared": False,
        "queue_send_enabled": False,
        "queue_send_flag": AWS_QUEUE_SEND_ENABLED_FLAG,
        "sqs_send_attempted": False,
        "aws_call_attempted": False,
        "provider_call_attempted": False,
        "stripe_call_attempted": False,
        "credit_mutation_attempted": False,
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def status_persistence_not_prepared(reason: str) -> Dict[str, Any]:
    return {
        "status": "durable_status_read_not_prepared",
        "reason": clean_text(reason, 180),
        "prepared": False,
        "would_read_durable_status": False,
        "rds_read_attempted": False,
        "db_connection_attempted": False,
        "aws_call_attempted": False,
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def build_stable_durable_job_payload(payload: Mapping[str, Any], evaluation_base: Mapping[str, Any]) -> Dict[str, Any]:
    selected_agent = clean_text(first_value(payload, ("selected_agent", "agent_id"), ""), 180)
    selected_agents = ensure_list(payload.get("selected_agents") or payload.get("agent_ids") or selected_agent)
    agent_ids = ensure_list(payload.get("agent_ids") or selected_agents)
    job_id = clean_text(first_value(payload, ("job_id", "parent_job_id", "id"), ""), 180)
    status = clean_text(payload.get("status") or "accepted", 160)
    now = utc_now()
    return redact_secret_values({
        "job_id": job_id or "pending_media_job",
        "parent_job_id": clean_text(payload.get("parent_job_id"), 180),
        "customer_id": clean_text(first_value(payload, ("customer_id", "client_id"), ""), 180),
        "account_id": clean_text(first_value(payload, ("account_id", "tenant_id"), ""), 180),
        "tenant_id": clean_text(payload.get("tenant_id"), 180),
        "status": status,
        "internal_status": status,
        "client_safe_status": "queued" if status in {"accepted", "queued"} else status,
        "task_type": clean_text(payload.get("task_type") or "media_generation", 120),
        "workflow_type": clean_text(payload.get("workflow_type") or "universal_complete_media", 160),
        "media_type": clean_text(first_value(payload, ("media_type", "output_type"), "complete_video"), 160),
        "asset_type": clean_text(first_value(payload, ("asset_type", "output_asset_type"), "video"), 160),
        "output_type": clean_text(first_value(payload, ("output_type", "media_type"), "complete_video"), 180),
        "agent_id": selected_agent,
        "selected_agent": selected_agent,
        "selected_agents": selected_agents,
        "agent_ids": agent_ids,
        "multi_agent_media_execution": clean_bool(payload.get("multi_agent_media_execution")) or len(selected_agents or agent_ids) > 1,
        "duration_seconds": clean_int(first_value(payload, ("duration_seconds", "duration"), 0), 0),
        "aspect_ratio": clean_text(payload.get("aspect_ratio") or "16:9", 40),
        "video_provider": clean_text(first_value(payload, ("video_provider", "visual_provider"), ""), 80),
        "audio_provider": clean_text(payload.get("audio_provider"), 80),
        "created_at": clean_text(payload.get("created_at") or now, 80),
        "updated_at": now,
        "customer_safe": True,
        "route_mode_metadata": route_mode_metadata(evaluation_base, clean_text(evaluation_base.get("route_kind"), 80)),
    })


def build_durable_repository_dry_run_plan(
    payload: Mapping[str, Any],
    evaluation_base: Mapping[str, Any],
    *,
    env: Mapping[str, Any],
) -> Dict[str, Any]:
    record_payload = build_stable_durable_job_payload(payload, evaluation_base)
    durable_record = build_durable_media_job_status_record(record_payload)
    create_operation = build_repository_operation_result("create_job_placeholder", record_payload)
    audit_operation = build_repository_operation_result(
        "append_job_event_placeholder",
        {
            **record_payload,
            "event_type": "aws17_durable_repository_dry_run_prepared",
            "source_type": "aws_option_a_route_integration",
        },
    )
    write_flag_enabled = durable_write_enabled(env)
    return redact_secret_values({
        "boundary": "aws17_durable_enqueue_dry_run_boundary",
        "status": (
            "durable_repository_write_flag_enabled_but_adapter_not_invoked"
            if write_flag_enabled
            else "durable_repository_dry_run_prepared"
        ),
        "prepared": True,
        "dry_run": not write_flag_enabled,
        "durable_write_enabled": write_flag_enabled,
        "durable_write_flag": AWS_DURABLE_WRITE_ENABLED_FLAG,
        "record_shape": {
            "job_id": durable_record.get("job_id"),
            "status": durable_record.get("internal_status"),
            "media_type": durable_record.get("media_type"),
            "asset_type": durable_record.get("asset_type"),
            "agent_id": record_payload.get("agent_id"),
            "created_at": durable_record.get("created_at"),
            "updated_at": durable_record.get("updated_at"),
            "customer_safe": True,
            "route_mode_metadata": record_payload.get("route_mode_metadata") or {},
        },
        "durable_job_record": durable_record,
        "repository_operations": [create_operation, audit_operation],
        "operation_count": 2,
        "rds_write_attempted": False,
        "db_connection_attempted": False,
        "migration_attempted": False,
        "aws_call_attempted": False,
        "provider_call_attempted": False,
        "stripe_call_attempted": False,
        "billing_mutation_attempted": False,
        "credit_mutation_attempted": False,
        "credential_values_exposed": False,
        "provider_secret_values_visible": False,
        "customer_safe": True,
    })


def build_queue_enqueue_dry_run_plan(
    payload: Mapping[str, Any],
    evaluation_base: Mapping[str, Any],
    *,
    env: Mapping[str, Any],
) -> Dict[str, Any]:
    route_metadata = route_mode_metadata(evaluation_base, clean_text(evaluation_base.get("route_kind"), 80))
    queue_payload = {
        **dict(payload or {}),
        "route_mode_metadata": route_metadata,
        "requested_from": clean_text(payload.get("requested_from") or "complete_media_popup", 160),
        "workflow_type": clean_text(payload.get("workflow_type") or "universal_complete_media", 160),
        "task_type": clean_text(payload.get("task_type") or "media_generation", 120),
    }
    message = build_media_queue_message(queue_payload)
    validation = validate_media_queue_message(message)
    send_flag_enabled = queue_send_enabled(env)
    return redact_secret_values({
        "boundary": "aws17_durable_enqueue_dry_run_boundary",
        "status": (
            "queue_send_flag_enabled_but_adapter_not_invoked"
            if send_flag_enabled
            else "queue_enqueue_dry_run_prepared"
        ),
        "prepared": bool(validation.get("valid")),
        "dry_run": not send_flag_enabled,
        "queue_send_enabled": send_flag_enabled,
        "queue_send_flag": AWS_QUEUE_SEND_ENABLED_FLAG,
        "queue_backend": "aws_sqs_future_adapter",
        "queue_packet": message if validation.get("valid") else {},
        "queue_message_validation": validation,
        "sqs_send_attempted": False,
        "aws_call_attempted": False,
        "provider_call_attempted": False,
        "stripe_call_attempted": False,
        "billing_mutation_attempted": False,
        "credit_mutation_attempted": False,
        "credential_values_exposed": False,
        "provider_secret_values_visible": False,
        "customer_safe": True,
    })


def build_status_persistence_dry_run_plan(payload: Mapping[str, Any], evaluation_base: Mapping[str, Any]) -> Dict[str, Any]:
    job_id = clean_text(first_value(payload, ("job_id", "parent_job_id", "id"), ""), 180)
    read_operation = build_repository_operation_result(
        "read_job_status_placeholder",
        {
            "job_id": job_id or "pending_media_job",
            "actor_role": clean_text(first_value(payload, ("actor_role", "requested_by_role", "role"), "system"), 80),
            "route_mode_metadata": route_mode_metadata(evaluation_base, ROUTE_KIND_STATUS),
        },
    )
    return redact_secret_values({
        "boundary": "aws17_durable_enqueue_dry_run_boundary",
        "status": "durable_status_read_dry_run_prepared",
        "prepared": True,
        "would_read_durable_status": True,
        "job_id": job_id or "pending_media_job",
        "read_operation": read_operation,
        "rds_read_attempted": False,
        "db_connection_attempted": False,
        "aws_call_attempted": False,
        "provider_call_attempted": False,
        "stripe_call_attempted": False,
        "billing_mutation_attempted": False,
        "credit_mutation_attempted": False,
        "credential_values_exposed": False,
        "customer_safe": True,
    })


def build_durable_enqueue_dry_run_boundary(
    payload: Mapping[str, Any],
    evaluation_base: Mapping[str, Any],
    *,
    env: Mapping[str, Any],
    route_kind: str,
) -> Dict[str, Any]:
    if not evaluation_base.get("route_execution_allowed"):
        reason = "route_not_ready_or_authority_blocked"
        if clean_text(evaluation_base.get("route_mode")) == ROUTE_MODE_ENABLED_MISSING_VALIDATION:
            reason = "missing_validation_evidence"
        return redact_secret_values({
            "boundary": "aws17_durable_enqueue_dry_run_boundary",
            "status": "not_prepared_until_route_ready",
            "route_kind": route_kind,
            "route_execution_allowed": False,
            "durable_repository": durable_repository_not_prepared(reason),
            "queue_enqueue": queue_enqueue_not_prepared(reason),
            "status_persistence": status_persistence_not_prepared(reason),
            "rds_write_attempted": False,
            "db_connection_attempted": False,
            "sqs_send_attempted": False,
            "aws_call_attempted": False,
            "provider_call_attempted": False,
            "stripe_call_attempted": False,
            "billing_mutation_attempted": False,
            "credit_mutation_attempted": False,
            "customer_safe": True,
        })

    durable_repository = (
        build_durable_repository_dry_run_plan(payload, evaluation_base, env=env)
        if route_kind == ROUTE_KIND_ACCEPTANCE
        else durable_repository_not_prepared("status_route_read_only")
    )
    queue_enqueue = (
        build_queue_enqueue_dry_run_plan(payload, evaluation_base, env=env)
        if route_kind == ROUTE_KIND_ACCEPTANCE
        else queue_enqueue_not_prepared("status_route_read_only")
    )
    status_persistence = (
        build_status_persistence_dry_run_plan(payload, evaluation_base)
        if route_kind == ROUTE_KIND_STATUS
        else status_persistence_not_prepared("acceptance_route_enqueue_only")
    )
    return redact_secret_values({
        "boundary": "aws17_durable_enqueue_dry_run_boundary",
        "status": "aws17_durable_enqueue_dry_run_prepared",
        "route_kind": route_kind,
        "route_execution_allowed": True,
        "durable_repository": durable_repository,
        "queue_enqueue": queue_enqueue,
        "status_persistence": status_persistence,
        "rds_write_attempted": False,
        "db_connection_attempted": False,
        "migration_attempted": False,
        "sqs_send_attempted": False,
        "s3_upload_attempted": False,
        "secret_fetch_attempted": False,
        "aws_call_attempted": False,
        "provider_call_attempted": False,
        "stripe_call_attempted": False,
        "billing_mutation_attempted": False,
        "credit_mutation_attempted": False,
        "credential_values_exposed": False,
        "provider_secret_values_visible": False,
        "customer_safe": True,
    })


def evaluate_acceptance_route_mode(
    payload: Mapping[str, Any] | None = None,
    *,
    env: Optional[Mapping[str, Any]] = None,
    validation_evidence: Optional[Mapping[str, Any]] = None,
    query_params: Optional[Mapping[str, Any]] = None,
    headers: Optional[Mapping[str, Any]] = None,
    audience: str = "admin",
) -> Dict[str, Any]:
    payload = dict(payload or {})
    evidence = dict(validation_evidence or extract_validation_evidence(payload))
    decision = decide_api_acceptance_route_cutover(payload, env=env or {}, validation_evidence=evidence)
    return build_route_mode_evaluation(
        decision,
        payload=payload,
        env=env or {},
        query_params=query_params,
        headers=headers,
        audience=audience,
        route_kind=ROUTE_KIND_ACCEPTANCE,
    )


def evaluate_status_route_mode(
    payload: Mapping[str, Any] | None = None,
    *,
    env: Optional[Mapping[str, Any]] = None,
    validation_evidence: Optional[Mapping[str, Any]] = None,
    query_params: Optional[Mapping[str, Any]] = None,
    headers: Optional[Mapping[str, Any]] = None,
    audience: str = "admin",
) -> Dict[str, Any]:
    payload = dict(payload or {})
    evidence = dict(validation_evidence or extract_validation_evidence(payload))
    decision = decide_api_status_route_cutover(payload, env=env or {}, validation_evidence=evidence)
    return build_route_mode_evaluation(
        decision,
        payload=payload,
        env=env or {},
        query_params=query_params,
        headers=headers,
        audience=audience,
        route_kind=ROUTE_KIND_STATUS,
    )


def build_route_mode_evaluation(
    decision: Mapping[str, Any],
    *,
    payload: Mapping[str, Any],
    env: Mapping[str, Any],
    query_params: Optional[Mapping[str, Any]],
    headers: Optional[Mapping[str, Any]],
    audience: str,
    route_kind: str,
) -> Dict[str, Any]:
    route_intent = aws_route_cutover_intent(env, route_kind)
    diagnostic_requested = diagnostics_requested(payload=payload, query_params=query_params, headers=headers)
    route_execution_allowed = bool(decision.get("route_execution_allowed"))
    short_circuit = route_should_short_circuit(decision, route_intent)
    evaluation_base = {
        "boundary": "aws16_route_integration_boundary",
        "route_kind": route_kind,
        "audience": normalise_audience(audience),
        "route_mode": decision.get("route_mode"),
        "selected_runtime_path": decision.get("selected_runtime_path"),
        "route_execution_allowed": route_execution_allowed,
        "request_authority_allowed": bool(decision.get("request_authority_allowed")),
        "aws_route_cutover_intent": route_intent,
        "diagnostics_requested": diagnostic_requested,
        "short_circuit_route": short_circuit,
        "default_response_unchanged": not route_intent and not diagnostic_requested,
        "status": integration_status(decision, short_circuit),
        "http_status": 202 if route_execution_allowed else 200,
        "decision": decision,
        "created_at": utc_now(),
        "live_routes_switched": False,
        "rds_write_attempted": False,
        "db_connection_attempted": False,
        "migration_attempted": False,
        "sqs_send_attempted": False,
        "s3_upload_attempted": False,
        "secret_fetch_attempted": False,
        "aws_call_attempted": False,
        "provider_call_attempted": False,
        "stripe_call_attempted": False,
        "billing_mutation_attempted": False,
        "credit_mutation_attempted": False,
        "credential_values_exposed": False,
        "provider_secret_values_visible": False,
        "customer_safe": True,
    }
    evaluation_base["aws17_durable_enqueue"] = build_durable_enqueue_dry_run_boundary(
        payload,
        evaluation_base,
        env=env,
        route_kind=route_kind,
    )
    return redact_secret_values(evaluation_base)


def integration_status(decision: Mapping[str, Any], short_circuit: bool) -> str:
    route_mode = clean_text(decision.get("route_mode"), 120)
    if route_mode == ROUTE_MODE_DRY_RUN:
        return "aws_option_a_route_dry_run"
    if route_mode == ROUTE_MODE_ENABLED_READY and bool(decision.get("route_execution_allowed")):
        return "aws_option_a_route_ready_no_live_mutation"
    if short_circuit:
        return "aws_option_a_route_cutover_blocked"
    return "compatibility_runtime_passthrough"


def build_admin_route_mode_response(evaluation: Mapping[str, Any]) -> Dict[str, Any]:
    decision = evaluation.get("decision") if isinstance(evaluation.get("decision"), dict) else {}
    aws17_boundary = evaluation.get("aws17_durable_enqueue") if isinstance(evaluation.get("aws17_durable_enqueue"), dict) else {}
    return redact_secret_values({
        "success": bool(evaluation.get("route_execution_allowed")),
        "accepted": False,
        "status": evaluation.get("status"),
        "route_kind": evaluation.get("route_kind"),
        "route_mode": evaluation.get("route_mode"),
        "selected_runtime_path": evaluation.get("selected_runtime_path"),
        "route_execution_allowed": bool(evaluation.get("route_execution_allowed")),
        "message": (
            "AWS Option A route mode is ready. Durable repository and queue packets are prepared in AWS-17 dry-run mode; no live write or send has occurred."
            if evaluation.get("route_execution_allowed")
            else "AWS Option A route mode is not ready. Current compatibility runtime remains the safe path."
        ),
        "missing_gates": decision.get("missing_gates") or [],
        "admin_route_diagnostics": decision.get("admin_view") or {},
        "aws17_durable_enqueue": aws17_boundary,
        "durable_repository": aws17_boundary.get("durable_repository") or {},
        "queue_enqueue": aws17_boundary.get("queue_enqueue") or {},
        "status_persistence": aws17_boundary.get("status_persistence") or {},
        "live_routes_switched": False,
        "rds_write_attempted": False,
        "db_connection_attempted": False,
        "migration_attempted": False,
        "sqs_send_attempted": False,
        "s3_upload_attempted": False,
        "secret_fetch_attempted": False,
        "aws_call_attempted": False,
        "provider_call_attempted": False,
        "stripe_call_attempted": False,
        "billing_mutation_attempted": False,
        "credit_mutation_attempted": False,
        "credential_values_exposed": False,
        "provider_secret_values_visible": False,
        "customer_safe": True,
    })


def build_client_route_mode_response(evaluation: Mapping[str, Any]) -> Dict[str, Any]:
    decision = evaluation.get("decision") if isinstance(evaluation.get("decision"), dict) else {}
    client_view = decision.get("client_view") if isinstance(decision.get("client_view"), dict) else {}
    return {
        "success": bool(evaluation.get("route_execution_allowed")),
        "accepted": False,
        "status": client_view.get("status") or "current_runtime_active",
        "message": client_view.get("message") or "This request will use the current production runtime path.",
        "processing_mode": client_view.get("runtime_path") or "current_production_runtime",
        "external_calls_started": False,
        "paid_provider_calls_started": False,
        "billing_mutation_attempted": False,
        "credit_mutation_attempted": False,
        "sensitive_values_exposed": False,
        "internal_config_exposed": False,
        "customer_safe": True,
    }


def build_route_mode_response(evaluation: Mapping[str, Any], *, audience: str = "admin") -> Dict[str, Any]:
    if normalise_audience(audience) == "client":
        return build_client_route_mode_response(evaluation)
    return build_admin_route_mode_response(evaluation)


def build_admin_route_diagnostics(evaluation: Mapping[str, Any]) -> Dict[str, Any]:
    decision = evaluation.get("decision") if isinstance(evaluation.get("decision"), dict) else {}
    aws17_boundary = evaluation.get("aws17_durable_enqueue") if isinstance(evaluation.get("aws17_durable_enqueue"), dict) else {}
    return redact_secret_values({
        "boundary": "aws16_route_integration_boundary",
        "status": evaluation.get("status"),
        "route_kind": evaluation.get("route_kind"),
        "route_mode": evaluation.get("route_mode"),
        "selected_runtime_path": evaluation.get("selected_runtime_path"),
        "route_execution_allowed": bool(evaluation.get("route_execution_allowed")),
        "aws_route_cutover_intent": bool(evaluation.get("aws_route_cutover_intent")),
        "missing_gates": decision.get("missing_gates") or [],
        "validation_summary": decision.get("validation_summary") or {},
        "final_visible_agent_catalogue": decision.get("final_visible_agent_catalogue") or {},
        "aws17_durable_enqueue": aws17_boundary,
        "durable_repository": aws17_boundary.get("durable_repository") or {},
        "queue_enqueue": aws17_boundary.get("queue_enqueue") or {},
        "status_persistence": aws17_boundary.get("status_persistence") or {},
        "external_calls_started": False,
        "live_routes_switched": False,
        "rds_write_attempted": False,
        "db_connection_attempted": False,
        "migration_attempted": False,
        "sqs_send_attempted": False,
        "s3_upload_attempted": False,
        "secret_fetch_attempted": False,
        "aws_call_attempted": False,
        "provider_call_attempted": False,
        "stripe_call_attempted": False,
        "billing_mutation_attempted": False,
        "credit_mutation_attempted": False,
        "credential_values_exposed": False,
        "provider_secret_values_visible": False,
        "customer_safe": True,
    })


def build_client_route_diagnostics(evaluation: Mapping[str, Any]) -> Dict[str, Any]:
    decision = evaluation.get("decision") if isinstance(evaluation.get("decision"), dict) else {}
    client_view = decision.get("client_view") if isinstance(decision.get("client_view"), dict) else {}
    return {
        "status": client_view.get("status") or "current_runtime_active",
        "processing_mode": client_view.get("runtime_path") or "current_production_runtime",
        "message": client_view.get("message") or "This request will use the current production runtime path.",
        "external_calls_started": False,
        "paid_provider_calls_started": False,
        "billing_mutation_attempted": False,
        "credit_mutation_attempted": False,
        "sensitive_values_exposed": False,
        "internal_config_exposed": False,
        "customer_safe": True,
    }


def apply_route_mode_to_response(
    response: Mapping[str, Any] | None,
    evaluation: Mapping[str, Any],
    *,
    audience: str = "admin",
) -> Dict[str, Any]:
    response_dict = dict(response or {})
    if not evaluation.get("diagnostics_requested"):
        return response_dict
    if normalise_audience(audience) == "client":
        response_dict["route_mode"] = build_client_route_diagnostics(evaluation)
    else:
        response_dict["aws_option_a_route_mode"] = build_admin_route_diagnostics(evaluation)
    return redact_secret_values(response_dict)
