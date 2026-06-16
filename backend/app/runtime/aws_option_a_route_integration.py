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


DIAGNOSTIC_TRUE_VALUES = {"1", "true", "yes", "on", "enabled", "admin"}
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


def route_should_short_circuit(decision: Mapping[str, Any], route_intent: bool) -> bool:
    if not route_intent:
        return False
    return clean_text(decision.get("route_mode")) in {
        ROUTE_MODE_ENABLED_MISSING_VALIDATION,
        ROUTE_MODE_LIVE_READY_DISABLED,
        ROUTE_MODE_ENABLED_READY,
    }


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
    return redact_secret_values({
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
    })


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
    return redact_secret_values({
        "success": bool(evaluation.get("route_execution_allowed")),
        "accepted": False,
        "status": evaluation.get("status"),
        "route_kind": evaluation.get("route_kind"),
        "route_mode": evaluation.get("route_mode"),
        "selected_runtime_path": evaluation.get("selected_runtime_path"),
        "route_execution_allowed": bool(evaluation.get("route_execution_allowed")),
        "message": (
            "AWS Option A route mode is ready, but live durable writes remain disabled in AWS-16."
            if evaluation.get("route_execution_allowed")
            else "AWS Option A route mode is not ready. Current compatibility runtime remains the safe path."
        ),
        "missing_gates": decision.get("missing_gates") or [],
        "admin_route_diagnostics": decision.get("admin_view") or {},
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
