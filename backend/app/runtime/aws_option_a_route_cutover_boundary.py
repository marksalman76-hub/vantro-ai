from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, Mapping, Optional

from backend.app.runtime.api_acceptance_entitlement_boundary import (
    build_admin_safe_enforcement_view,
    build_api_acceptance_entitlement_decision,
    build_client_safe_enforcement_view,
)
from backend.app.runtime.real_agent_component_catalogue import (
    CLIENT_FACING_AGENTS,
    FINAL_APPROVED_VISIBLE_AGENT_COUNT,
    FINAL_APPROVED_VISIBLE_AGENT_SOURCE,
    SYSTEM_AGENTS,
)


TRUE_VALUES = {"1", "true", "yes", "on", "enabled"}

AWS_OPTION_A_ENABLED_FLAG = "AWS_OPTION_A_ENABLED"
AWS_ROUTE_CUTOVER_ENABLED_FLAG = "AWS_OPTION_A_ROUTE_CUTOVER_ENABLED"
AWS_ACCEPTANCE_CUTOVER_ENABLED_FLAG = "AWS_OPTION_A_ACCEPTANCE_CUTOVER_ENABLED"
AWS_STATUS_CUTOVER_ENABLED_FLAG = "AWS_OPTION_A_STATUS_CUTOVER_ENABLED"

ROUTE_MODE_COMPATIBILITY = "compatibility_runtime_path"
ROUTE_MODE_DRY_RUN = "aws_option_a_dry_run_path"
ROUTE_MODE_LIVE_READY_DISABLED = "aws_option_a_live_ready_but_disabled"
ROUTE_MODE_ENABLED_MISSING_VALIDATION = "aws_option_a_enabled_missing_validation"
ROUTE_MODE_ENABLED_READY = "aws_option_a_enabled_ready"

ROUTE_KIND_ACCEPTANCE = "acceptance"
ROUTE_KIND_STATUS = "status"
SUPPORTED_ROUTE_KINDS = {ROUTE_KIND_ACCEPTANCE, ROUTE_KIND_STATUS}

REQUIRED_VALIDATION_SERVICES = ("iam", "rds", "sqs", "s3", "secrets")

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
    "secret",
    "stripe_secret_key",
    "token",
)

SAFE_BOOLEAN_MARKER_KEYS = {
    "aws_call_attempted",
    "credential_values_exposed",
    "provider_secret_values_visible",
    "db_connection_attempted",
    "migration_attempted",
    "rds_write_attempted",
    "sqs_send_attempted",
    "s3_upload_attempted",
    "secret_fetch_attempted",
    "provider_call_attempted",
    "stripe_call_attempted",
    "credit_mutation_attempted",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def clean_text(value: Any, limit: int = 1000) -> str:
    return str(value or "").strip()[:limit]


def enabled(value: Any) -> bool:
    return str(value or "").strip().lower() in TRUE_VALUES


def first_value(payload: Mapping[str, Any], keys: Iterable[str], default: Any = "") -> Any:
    for key in keys:
        value = payload.get(key)
        if value not in (None, ""):
            return value
    return default


def safe_hash(value: Any) -> str:
    import hashlib

    text = clean_text(value, 5000)
    if not text:
        return ""
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()[:12]


def redacted_env_metadata(env: Mapping[str, Any], keys: Iterable[str]) -> list[Dict[str, Any]]:
    metadata: list[Dict[str, Any]] = []
    for key in keys:
        value = clean_text(env.get(key), 5000)
        metadata.append({
            "name": key,
            "present": bool(value),
            "redacted": True,
            "length": len(value),
            "sha256_12": safe_hash(value),
        })
    return metadata


def redact_secret_values(value: Any) -> Any:
    if isinstance(value, dict):
        cleaned: Dict[str, Any] = {}
        for key, item in value.items():
            key_l = str(key).lower()
            if key_l in SAFE_BOOLEAN_MARKER_KEYS or isinstance(item, bool):
                cleaned[key] = item
            elif any(marker in key_l for marker in SECRET_KEY_MARKERS):
                cleaned[key] = "[redacted]"
            else:
                cleaned[key] = redact_secret_values(item)
        return cleaned
    if isinstance(value, list):
        return [redact_secret_values(item) for item in value]
    return value


def normalise_route_kind(route_kind: Any) -> str:
    route_kind_clean = clean_text(route_kind or ROUTE_KIND_ACCEPTANCE, 80).lower()
    return route_kind_clean if route_kind_clean in SUPPORTED_ROUTE_KINDS else ROUTE_KIND_ACCEPTANCE


def extract_validation_service_results(validation_evidence: Mapping[str, Any] | None) -> Dict[str, Dict[str, Any]]:
    evidence = dict(validation_evidence or {})
    raw_service_results = evidence.get("service_results") if isinstance(evidence.get("service_results"), dict) else evidence
    service_results: Dict[str, Dict[str, Any]] = {}
    for service in REQUIRED_VALIDATION_SERVICES:
        raw_item = raw_service_results.get(service)
        if raw_item is None and service == "secrets":
            raw_item = raw_service_results.get("secrets_manager")
        if isinstance(raw_item, dict):
            status = clean_text(raw_item.get("status"), 120)
        else:
            status = clean_text(raw_item, 120)
        service_results[service] = {
            "service": service,
            "status": status or "missing",
            "passed": status == "passed",
        }
    return service_results


def build_validation_summary(validation_evidence: Mapping[str, Any] | None) -> Dict[str, Any]:
    service_results = extract_validation_service_results(validation_evidence)
    missing = [
        service
        for service, result in service_results.items()
        if result.get("status") != "passed"
    ]
    return {
        "required_services": list(REQUIRED_VALIDATION_SERVICES),
        "service_results": service_results,
        "validation_ready": not missing,
        "missing_or_failed_services": missing,
        "secret_values_printed": False,
        "credential_values_exposed": False,
    }


def final_visible_catalogue_guard() -> Dict[str, Any]:
    visible_keys = [agent["key"] for agent in CLIENT_FACING_AGENTS]
    system_keys = [agent["key"] for agent in SYSTEM_AGENTS]
    return {
        "source": FINAL_APPROVED_VISIBLE_AGENT_SOURCE,
        "expected_visible_count": FINAL_APPROVED_VISIBLE_AGENT_COUNT,
        "actual_visible_count": len(visible_keys),
        "visible_count_valid": len(visible_keys) == FINAL_APPROVED_VISIBLE_AGENT_COUNT,
        "duplicate_visible_keys": sorted({key for key in visible_keys if visible_keys.count(key) > 1}),
        "system_agent_count_internal_only": len(system_keys),
        "system_agents_visible_or_selectable": False,
    }


def build_flag_state(env: Mapping[str, Any], route_kind: str) -> Dict[str, Any]:
    operation_flag = (
        AWS_ACCEPTANCE_CUTOVER_ENABLED_FLAG
        if route_kind == ROUTE_KIND_ACCEPTANCE
        else AWS_STATUS_CUTOVER_ENABLED_FLAG
    )
    return {
        "aws_option_a_enabled": enabled(env.get(AWS_OPTION_A_ENABLED_FLAG)),
        "route_cutover_enabled": enabled(env.get(AWS_ROUTE_CUTOVER_ENABLED_FLAG)),
        "acceptance_cutover_enabled": enabled(env.get(AWS_ACCEPTANCE_CUTOVER_ENABLED_FLAG)),
        "status_cutover_enabled": enabled(env.get(AWS_STATUS_CUTOVER_ENABLED_FLAG)),
        "operation_cutover_flag": operation_flag,
        "operation_cutover_enabled": enabled(env.get(operation_flag)),
    }


def route_mode_from_gates(
    *,
    flag_state: Mapping[str, Any],
    validation_summary: Mapping[str, Any],
    payload: Mapping[str, Any],
) -> str:
    if not flag_state.get("aws_option_a_enabled"):
        return ROUTE_MODE_COMPATIBILITY
    if enabled(payload.get("dry_run")) or enabled(payload.get("preflight_only")):
        return ROUTE_MODE_DRY_RUN
    if not validation_summary.get("validation_ready"):
        return ROUTE_MODE_ENABLED_MISSING_VALIDATION
    if not flag_state.get("route_cutover_enabled") or not flag_state.get("operation_cutover_enabled"):
        return ROUTE_MODE_LIVE_READY_DISABLED
    return ROUTE_MODE_ENABLED_READY


def selected_runtime_path(route_mode: str, route_kind: str) -> str:
    if route_mode == ROUTE_MODE_ENABLED_READY:
        return f"aws_option_a_durable_{route_kind}_path"
    if route_mode == ROUTE_MODE_DRY_RUN:
        return "aws_option_a_dry_run_planning_path"
    return "existing_compatibility_runtime_path"


def build_missing_gates(
    *,
    flag_state: Mapping[str, Any],
    validation_summary: Mapping[str, Any],
    authority_decision: Mapping[str, Any],
    catalogue_guard: Mapping[str, Any],
) -> list[str]:
    missing: list[str] = []
    if not flag_state.get("aws_option_a_enabled"):
        missing.append(AWS_OPTION_A_ENABLED_FLAG)
    if not flag_state.get("route_cutover_enabled"):
        missing.append(AWS_ROUTE_CUTOVER_ENABLED_FLAG)
    if not flag_state.get("operation_cutover_enabled"):
        missing.append(clean_text(flag_state.get("operation_cutover_flag")))
    for service in validation_summary.get("missing_or_failed_services") or []:
        missing.append(f"validation_evidence:{service}")
    if not authority_decision.get("allowed"):
        missing.append("api_acceptance_entitlement_allowed")
    if not catalogue_guard.get("visible_count_valid"):
        missing.append("final_27_agent_catalogue_valid")
    if catalogue_guard.get("duplicate_visible_keys"):
        missing.append("no_duplicate_visible_agent_keys")
    return missing


@dataclass(frozen=True)
class AwsOptionARouteCutoverDecision:
    boundary: str
    route_kind: str
    route_mode: str
    selected_runtime_path: str
    flags: Dict[str, Any]
    validation_summary: Dict[str, Any]
    route_execution_allowed: bool
    request_authority_allowed: bool
    authority_summary: Dict[str, Any]
    final_visible_agent_catalogue: Dict[str, Any]
    missing_gates: list[str] = field(default_factory=list)
    admin_view: Dict[str, Any] = field(default_factory=dict)
    client_view: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=utc_now)
    live_routes_switched: bool = False
    rds_write_attempted: bool = False
    db_connection_attempted: bool = False
    migration_attempted: bool = False
    sqs_send_attempted: bool = False
    s3_upload_attempted: bool = False
    secret_fetch_attempted: bool = False
    aws_call_attempted: bool = False
    provider_call_attempted: bool = False
    stripe_call_attempted: bool = False
    billing_mutation_attempted: bool = False
    credit_mutation_attempted: bool = False
    provider_secret_values_visible: bool = False
    credential_values_exposed: bool = False
    customer_safe: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return redact_secret_values(asdict(self))


def build_admin_safe_route_cutover_view(
    decision_base: Mapping[str, Any],
    env: Mapping[str, Any],
    authority_decision: Mapping[str, Any],
) -> Dict[str, Any]:
    safe_env_keys = (
        AWS_OPTION_A_ENABLED_FLAG,
        AWS_ROUTE_CUTOVER_ENABLED_FLAG,
        AWS_ACCEPTANCE_CUTOVER_ENABLED_FLAG,
        AWS_STATUS_CUTOVER_ENABLED_FLAG,
        "AWS_REGION",
        "DATABASE_URL",
        "AWS_RDS_SECRET_ARN",
        "AWS_MEDIA_QUEUE_URL",
        "AWS_MEDIA_DLQ_URL",
        "AWS_MEDIA_S3_BUCKET",
        "AWS_UPLOADS_S3_BUCKET",
        "AWS_PROVIDER_SECRETS_PREFIX",
    )
    return redact_secret_values({
        "boundary": "aws15e_option_a_route_cutover_boundary",
        "route_kind": decision_base.get("route_kind"),
        "route_mode": decision_base.get("route_mode"),
        "selected_runtime_path": decision_base.get("selected_runtime_path"),
        "route_execution_allowed": bool(decision_base.get("route_execution_allowed")),
        "flags": decision_base.get("flags") or {},
        "missing_gates": decision_base.get("missing_gates") or [],
        "validation_summary": decision_base.get("validation_summary") or {},
        "safe_config_metadata": redacted_env_metadata(env, safe_env_keys),
        "authority": build_admin_safe_enforcement_view(authority_decision),
        "final_visible_agent_catalogue": decision_base.get("final_visible_agent_catalogue") or {},
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
        "provider_secret_values_visible": False,
        "credential_values_exposed": False,
        "customer_safe": True,
    })


def build_client_safe_route_cutover_view(
    decision_base: Mapping[str, Any],
    authority_decision: Mapping[str, Any],
) -> Dict[str, Any]:
    route_execution_allowed = bool(decision_base.get("route_execution_allowed"))
    route_mode = clean_text(decision_base.get("route_mode"), 120)
    if route_mode == ROUTE_MODE_DRY_RUN:
        status = "runtime_precheck_ready"
        message = "This request can be checked safely before live execution."
    elif route_execution_allowed:
        status = "durable_processing_ready"
        message = "This request is ready for the durable production processing path."
    else:
        status = "current_runtime_active"
        message = "This request will use the current production runtime path."
    authority_view = build_client_safe_enforcement_view(authority_decision)
    for hidden_key in (
        "aws_call_attempted",
        "provider_call_attempted",
        "stripe_call_attempted",
        "provider_secret_values_visible",
        "credential_values_exposed",
    ):
        authority_view.pop(hidden_key, None)
    return {
        "status": status,
        "runtime_path": "durable_processing_path" if route_execution_allowed else "current_production_runtime",
        "request_allowed": bool(authority_decision.get("allowed")),
        "message": message,
        "authority": authority_view,
        "external_calls_started": False,
        "paid_provider_calls_started": False,
        "billing_mutation_attempted": False,
        "credit_mutation_attempted": False,
        "sensitive_values_exposed": False,
        "internal_config_exposed": False,
        "customer_safe": True,
    }


def build_aws_option_a_route_cutover_decision(
    payload: Mapping[str, Any] | None = None,
    *,
    env: Optional[Mapping[str, Any]] = None,
    validation_evidence: Optional[Mapping[str, Any]] = None,
    route_kind: str = ROUTE_KIND_ACCEPTANCE,
) -> Dict[str, Any]:
    env = dict(env or {})
    payload = dict(payload or {})
    route_kind = normalise_route_kind(route_kind or first_value(payload, ("route_kind", "operation"), ROUTE_KIND_ACCEPTANCE))
    flag_state = build_flag_state(env, route_kind)
    validation_summary = build_validation_summary(validation_evidence)
    authority_decision = build_api_acceptance_entitlement_decision(payload)
    catalogue_guard = final_visible_catalogue_guard()
    route_mode = route_mode_from_gates(
        flag_state=flag_state,
        validation_summary=validation_summary,
        payload=payload,
    )
    runtime_path = selected_runtime_path(route_mode, route_kind)
    request_authority_allowed = bool(authority_decision.get("allowed"))
    catalogue_valid = bool(catalogue_guard.get("visible_count_valid")) and not bool(catalogue_guard.get("duplicate_visible_keys"))
    route_execution_allowed = bool(
        route_mode == ROUTE_MODE_ENABLED_READY
        and request_authority_allowed
        and catalogue_valid
    )
    base = {
        "boundary": "aws15e_option_a_route_cutover_boundary",
        "route_kind": route_kind,
        "route_mode": route_mode,
        "selected_runtime_path": runtime_path,
        "flags": flag_state,
        "validation_summary": validation_summary,
        "route_execution_allowed": route_execution_allowed,
        "request_authority_allowed": request_authority_allowed,
        "authority_summary": {
            "allowed": request_authority_allowed,
            "actor_role": authority_decision.get("actor_role"),
            "authority_level": authority_decision.get("authority_level"),
            "denial_reason": authority_decision.get("denial_reason") or "",
            "denial_reasons": authority_decision.get("denial_reasons") or [],
            "final_27_agent_validation": authority_decision.get("final_27_agent_validation") or {},
        },
        "final_visible_agent_catalogue": catalogue_guard,
    }
    missing_gates = build_missing_gates(
        flag_state=flag_state,
        validation_summary=validation_summary,
        authority_decision=authority_decision,
        catalogue_guard=catalogue_guard,
    )
    base["missing_gates"] = missing_gates
    decision = AwsOptionARouteCutoverDecision(
        admin_view=build_admin_safe_route_cutover_view(base, env, authority_decision),
        client_view=build_client_safe_route_cutover_view(base, authority_decision),
        missing_gates=missing_gates,
        **{key: value for key, value in base.items() if key != "missing_gates"},
    )
    return decision.to_dict()


def decide_api_acceptance_route_cutover(
    payload: Mapping[str, Any] | None = None,
    *,
    env: Optional[Mapping[str, Any]] = None,
    validation_evidence: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    return build_aws_option_a_route_cutover_decision(
        payload,
        env=env,
        validation_evidence=validation_evidence,
        route_kind=ROUTE_KIND_ACCEPTANCE,
    )


def decide_api_status_route_cutover(
    payload: Mapping[str, Any] | None = None,
    *,
    env: Optional[Mapping[str, Any]] = None,
    validation_evidence: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    return build_aws_option_a_route_cutover_decision(
        payload,
        env=env,
        validation_evidence=validation_evidence,
        route_kind=ROUTE_KIND_STATUS,
    )
