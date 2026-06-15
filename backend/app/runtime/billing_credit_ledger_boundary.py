from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Mapping, Optional
import uuid

from backend.app.runtime.api_acceptance_entitlement_boundary import (
    build_api_acceptance_entitlement_decision,
)


LEDGER_EVENT_TYPES = {
    "credit_reservation_requested",
    "credit_reserved_placeholder",
    "credit_reservation_denied",
    "credit_finalization_requested",
    "credit_finalized_placeholder",
    "credit_refund_requested",
    "credit_refunded_placeholder",
    "credit_reversal_requested",
    "credit_reversed_placeholder",
    "admin_override_recorded",
    "provider_cost_estimate_recorded",
    "provider_actual_cost_recorded",
    "billing_audit_event_recorded",
}

NO_MUTATION_MODE = "no_mutation_placeholder"

SECRET_KEY_MARKERS = (
    "api_key",
    "apikey",
    "authorization",
    "bearer",
    "credential",
    "password",
    "private_key",
    "provider_api_key",
    "stripe_secret_key",
    "secret",
    "token",
)

SAFE_BOOLEAN_MARKER_KEYS = {
    "credential_values_exposed",
    "provider_secret_values_visible",
    "billing_mutation_attempted",
    "stripe_call_attempted",
    "provider_call_attempted",
    "aws_call_attempted",
    "credit_mutation_attempted",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def safe_id(prefix: str = "ledger_event") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def clean_text(value: Any, limit: int = 1000) -> str:
    return str(value or "").strip()[:limit]


def clean_float(value: Any, default: float = 0.0) -> float:
    try:
        return max(0.0, float(value))
    except Exception:
        return default


def clean_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    text = str(value or "").strip().lower()
    if text in {"1", "true", "yes", "on", "enabled"}:
        return True
    if text in {"0", "false", "no", "off", "disabled"}:
        return False
    return default


def first_value(payload: Mapping[str, Any], keys: Iterable[str], default: Any = "") -> Any:
    for key in keys:
        value = payload.get(key)
        if value not in (None, ""):
            return value
    return default


def ensure_list(value: Any) -> List[str]:
    if isinstance(value, list):
        items = value
    elif isinstance(value, tuple):
        items = list(value)
    elif clean_text(value):
        items = [value]
    else:
        items = []
    result: List[str] = []
    for item in items:
        clean = clean_text(item, 180).lower()
        if clean and clean not in result:
            result.append(clean)
    return result


def redact_secret_values(value: Any) -> Any:
    if isinstance(value, dict):
        cleaned: Dict[str, Any] = {}
        for key, item in value.items():
            key_l = str(key).lower()
            if key_l in SAFE_BOOLEAN_MARKER_KEYS:
                cleaned[key] = item
            elif any(marker in key_l for marker in SECRET_KEY_MARKERS):
                cleaned[key] = "[redacted]"
            else:
                cleaned[key] = redact_secret_values(item)
        return cleaned
    if isinstance(value, list):
        return [redact_secret_values(item) for item in value]
    return value


def coerce_decision(decision_or_payload: Mapping[str, Any] | None) -> Dict[str, Any]:
    data = dict(decision_or_payload or {})
    if "final_27_agent_validation" in data and "authority_level" in data:
        return data
    if "acceptance_enforcement" in data:
        return dict(data.get("acceptance_enforcement") or {})
    if "envelope" in data and isinstance(data.get("envelope"), dict):
        envelope = data["envelope"]
        if "acceptance_enforcement" in envelope:
            return dict(envelope.get("acceptance_enforcement") or {})
    return build_api_acceptance_entitlement_decision(data)


def coerce_payload(decision_or_payload: Mapping[str, Any] | None, envelope: Mapping[str, Any] | None = None) -> Dict[str, Any]:
    payload = dict(decision_or_payload or {})
    if envelope:
        payload = {**dict(envelope), **payload}
    if "envelope" in payload and isinstance(payload.get("envelope"), dict):
        payload = {**dict(payload["envelope"]), **payload}
    return payload


def derive_provider_class(payload: Mapping[str, Any]) -> str:
    explicit = clean_text(payload.get("provider_class"), 120)
    if explicit:
        return explicit
    if clean_text(payload.get("video_provider")):
        return "video_generation_providers"
    if clean_text(payload.get("image_provider")):
        return "image_generation_providers"
    if clean_text(payload.get("audio_provider") or payload.get("voice_provider")):
        return "audio_voice_providers"
    if clean_text(payload.get("avatar_provider")):
        return "avatar_human_presenter_providers"
    if clean_text(payload.get("integration_provider")):
        return "integration_provider"
    return "not_provider_specific"


def derive_provider_name(payload: Mapping[str, Any]) -> str:
    return clean_text(
        first_value(
            payload,
            (
                "provider_name",
                "video_provider",
                "image_provider",
                "audio_provider",
                "voice_provider",
                "avatar_provider",
                "integration_provider",
                "provider",
            ),
            "",
        ),
        180,
    )


def estimate_credit_cost(payload: Mapping[str, Any]) -> float:
    explicit = first_value(payload, ("estimated_credit_cost", "estimated_credits_required", "credits_required"), None)
    if explicit not in (None, ""):
        return clean_float(explicit)
    duration = clean_float(payload.get("duration_seconds"))
    segment_count = clean_float(payload.get("segment_count"), 1.0)
    provider_weight = clean_float(payload.get("provider_cost_weight"), 1.0)
    quality_weight = clean_float(payload.get("quality_cost_weight"), 1.0)
    if duration:
        return round(max(1.0, duration / 5.0) * max(1.0, segment_count) * provider_weight * quality_weight, 2)
    return 0.0


@dataclass(frozen=True)
class CanonicalBillingCreditLedgerEntry:
    ledger_event_id: str
    event_type: str
    job_id: str = ""
    customer_id: str = ""
    account_id: str = ""
    tenant_id: str = ""
    actor_role: str = "client"
    authority_level: str = "client_package_credit_governed"
    package_name: str = "starter"
    selected_agent: str = ""
    selected_agents: List[str] = field(default_factory=list)
    agent_ids: List[str] = field(default_factory=list)
    final_27_agent_validation: Dict[str, Any] = field(default_factory=dict)
    task_type: str = ""
    workflow_type: str = ""
    media_type: str = ""
    asset_type: str = ""
    provider_class: str = ""
    provider_name: str = ""
    estimated_credit_cost: float = 0.0
    reserved_credit_amount: float = 0.0
    finalized_credit_amount: float = 0.0
    refunded_credit_amount: float = 0.0
    reversed_credit_amount: float = 0.0
    provider_estimated_cost: float = 0.0
    provider_actual_cost: float = 0.0
    currency: str = "credits"
    approval_status: str = ""
    stripe_reference: str = ""
    package_entitlement_reference: str = ""
    dry_run: bool = False
    preflight_only: bool = False
    smoke_test_mode: bool = False
    mutation_mode: str = NO_MUTATION_MODE
    status: str = "placeholder_recorded"
    denial_reason: str = ""
    audit: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=utc_now)
    billing_mutation_attempted: bool = False
    stripe_call_attempted: bool = False
    provider_call_attempted: bool = False
    aws_call_attempted: bool = False
    credit_mutation_attempted: bool = False
    rds_write_attempted: bool = False
    queue_mutation_attempted: bool = False
    credential_values_exposed: bool = False
    provider_secret_values_visible: bool = False
    customer_safe: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return redact_secret_values(asdict(self))


def build_billing_credit_ledger_entry(
    event_type: str,
    decision_or_payload: Mapping[str, Any] | None,
    envelope: Optional[Mapping[str, Any]] = None,
    extra: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    if event_type not in LEDGER_EVENT_TYPES:
        event_type = "billing_audit_event_recorded"
    payload = coerce_payload(decision_or_payload, envelope=envelope)
    extra = dict(extra or {})
    decision = coerce_decision(decision_or_payload or payload)
    final_validation = dict(decision.get("final_27_agent_validation") or {})
    allowed = bool(decision.get("allowed"))
    denial_reason = clean_text(decision.get("denial_reason") or first_value(payload, ("denial_reason", "safe_denial_reason"), ""), 240)
    dry_run = clean_bool(decision.get("dry_run") or payload.get("dry_run"))
    preflight_only = clean_bool(decision.get("preflight_only") or payload.get("preflight_only"))
    smoke_test_mode = clean_bool(decision.get("smoke_test_mode") or payload.get("smoke_test_mode"))
    no_mutation_mode = dry_run or preflight_only or smoke_test_mode
    estimated_credits = estimate_credit_cost({**payload, **extra})
    reservation_amount = clean_float(first_value(extra, ("reserved_credit_amount", "credit_amount"), estimated_credits))
    finalized_amount = clean_float(first_value(extra, ("finalized_credit_amount", "credit_amount"), reservation_amount))
    refund_amount = clean_float(first_value(extra, ("refunded_credit_amount", "refund_credit_amount", "credit_amount"), 0))
    reversal_amount = clean_float(first_value(extra, ("reversed_credit_amount", "reversal_credit_amount", "credit_amount"), 0))

    if event_type == "credit_reservation_requested":
        status = "reservation_check_prepared"
    elif event_type == "credit_reserved_placeholder":
        status = "reserved_placeholder" if allowed and not no_mutation_mode else "no_mutation_evidence_recorded"
    elif event_type == "credit_reservation_denied":
        status = "reservation_denied"
    elif event_type == "credit_finalized_placeholder":
        status = "finalized_placeholder"
    elif event_type in {"credit_refunded_placeholder", "credit_reversed_placeholder"}:
        status = "adjustment_placeholder"
    elif event_type == "admin_override_recorded":
        status = "admin_override_audit_only"
    elif event_type in {"provider_cost_estimate_recorded", "provider_actual_cost_recorded"}:
        status = "provider_cost_placeholder_recorded"
    else:
        status = "placeholder_recorded"

    if not allowed and event_type in {"credit_reservation_requested", "credit_reserved_placeholder"}:
        event_type = "credit_reservation_denied"
        status = "reservation_denied"
        denial_reason = denial_reason or "acceptance_entitlement_not_allowed"

    selected_agents = ensure_list(decision.get("selected_agents") or payload.get("selected_agents"))
    agent_ids = ensure_list(payload.get("agent_ids") or selected_agents)
    audit = {
        "correlation_id": clean_text(first_value(extra, ("correlation_id",), first_value(payload, ("correlation_id",), decision.get("audit", {}).get("correlation_id") if isinstance(decision.get("audit"), dict) else "")), 180),
        "request_id": clean_text(first_value(payload, ("request_id",), ""), 180),
        "idempotency_key": clean_text(first_value(payload, ("idempotency_key",), ""), 180),
        "audit_event_type": event_type,
        "source_boundary": "aws12_billing_credit_ledger_boundary",
    }
    entry = CanonicalBillingCreditLedgerEntry(
        ledger_event_id=clean_text(extra.get("ledger_event_id") or safe_id("ledger_event"), 180),
        event_type=event_type,
        job_id=clean_text(first_value(payload, ("job_id", "parent_job_id"), ""), 180),
        customer_id=clean_text(first_value(payload, ("customer_id", "client_id"), ""), 180),
        account_id=clean_text(first_value(payload, ("account_id", "tenant_id"), ""), 180),
        tenant_id=clean_text(payload.get("tenant_id"), 180),
        actor_role=clean_text(decision.get("actor_role") or payload.get("actor_role") or payload.get("requested_by_role") or "client", 80),
        authority_level=clean_text(decision.get("authority_level") or "client_package_credit_governed", 120),
        package_name=clean_text(decision.get("package_name") or payload.get("package_name") or payload.get("package") or "starter", 120),
        selected_agent=clean_text(first_value(payload, ("selected_agent", "agent_id"), selected_agents[0] if selected_agents else ""), 180),
        selected_agents=selected_agents,
        agent_ids=agent_ids,
        final_27_agent_validation=final_validation,
        task_type=clean_text(payload.get("task_type"), 120),
        workflow_type=clean_text(payload.get("workflow_type"), 160),
        media_type=clean_text(payload.get("media_type"), 120),
        asset_type=clean_text(payload.get("asset_type"), 120),
        provider_class=derive_provider_class({**payload, **extra}),
        provider_name=derive_provider_name({**payload, **extra}),
        estimated_credit_cost=estimated_credits,
        reserved_credit_amount=reservation_amount if event_type in {"credit_reserved_placeholder", "credit_reservation_requested"} else 0.0,
        finalized_credit_amount=finalized_amount if event_type == "credit_finalized_placeholder" else 0.0,
        refunded_credit_amount=refund_amount if event_type == "credit_refunded_placeholder" else 0.0,
        reversed_credit_amount=reversal_amount if event_type == "credit_reversed_placeholder" else 0.0,
        provider_estimated_cost=clean_float(first_value(extra, ("provider_estimated_cost", "estimated_provider_cost"), payload.get("provider_estimated_cost"))),
        provider_actual_cost=clean_float(first_value(extra, ("provider_actual_cost", "actual_provider_cost"), payload.get("provider_actual_cost"))),
        currency=clean_text(extra.get("currency") or payload.get("currency") or "credits", 20),
        approval_status=clean_text(decision.get("approval_status") or payload.get("approval_status"), 120),
        stripe_reference=clean_text(first_value(extra, ("stripe_reference", "stripe_event_reference"), payload.get("stripe_reference") or "stripe_reference_placeholder"), 240),
        package_entitlement_reference=clean_text(first_value(extra, ("package_entitlement_reference",), payload.get("package_entitlement_reference") or "package_entitlement_reference_placeholder"), 240),
        dry_run=dry_run,
        preflight_only=preflight_only,
        smoke_test_mode=smoke_test_mode,
        mutation_mode=NO_MUTATION_MODE,
        status=status,
        denial_reason=denial_reason,
        audit=audit,
        billing_mutation_attempted=False,
        stripe_call_attempted=False,
        provider_call_attempted=False,
        aws_call_attempted=False,
        credit_mutation_attempted=False,
        rds_write_attempted=False,
        queue_mutation_attempted=False,
    )
    return entry.to_dict()


def build_credit_reservation_placeholder(
    decision_or_payload: Mapping[str, Any] | None,
    envelope: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    decision = coerce_decision(decision_or_payload or {})
    event_type = "credit_reserved_placeholder" if decision.get("allowed") else "credit_reservation_denied"
    return build_billing_credit_ledger_entry(event_type, decision_or_payload, envelope=envelope)


def build_credit_finalization_placeholder(worker_result_or_payload: Mapping[str, Any] | None) -> Dict[str, Any]:
    return build_billing_credit_ledger_entry(
        "credit_finalized_placeholder",
        worker_result_or_payload,
        extra={"finalized_credit_amount": first_value(dict(worker_result_or_payload or {}), ("finalized_credit_amount", "actual_credit_cost", "credit_amount"), 0)},
    )


def build_credit_refund_placeholder(payload: Mapping[str, Any] | None) -> Dict[str, Any]:
    return build_billing_credit_ledger_entry(
        "credit_refunded_placeholder",
        payload,
        extra={"refunded_credit_amount": first_value(dict(payload or {}), ("refunded_credit_amount", "refund_credit_amount", "credit_amount"), 0)},
    )


def build_credit_reversal_placeholder(payload: Mapping[str, Any] | None) -> Dict[str, Any]:
    return build_billing_credit_ledger_entry(
        "credit_reversed_placeholder",
        payload,
        extra={"reversed_credit_amount": first_value(dict(payload or {}), ("reversed_credit_amount", "reversal_credit_amount", "credit_amount"), 0)},
    )


def build_admin_override_placeholder(payload: Mapping[str, Any] | None) -> Dict[str, Any]:
    return build_billing_credit_ledger_entry("admin_override_recorded", payload)


def build_provider_cost_estimate_placeholder(payload: Mapping[str, Any] | None) -> Dict[str, Any]:
    return build_billing_credit_ledger_entry("provider_cost_estimate_recorded", payload)


def build_provider_actual_cost_placeholder(payload: Mapping[str, Any] | None) -> Dict[str, Any]:
    return build_billing_credit_ledger_entry("provider_actual_cost_recorded", payload)


def build_billing_audit_event_placeholder(payload: Mapping[str, Any] | None) -> Dict[str, Any]:
    return build_billing_credit_ledger_entry("billing_audit_event_recorded", payload)


def build_client_safe_billing_view(entry_or_payload: Mapping[str, Any] | None) -> Dict[str, Any]:
    entry = dict(entry_or_payload or {})
    if "ledger_event_id" not in entry:
        entry = build_billing_audit_event_placeholder(entry)
    return {
        "ledger_event_id": entry.get("ledger_event_id"),
        "job_id": entry.get("job_id"),
        "status": entry.get("status"),
        "event_type": entry.get("event_type"),
        "package_name": entry.get("package_name"),
        "estimated_credit_cost": entry.get("estimated_credit_cost"),
        "reserved_credit_amount": entry.get("reserved_credit_amount"),
        "finalized_credit_amount": entry.get("finalized_credit_amount"),
        "refunded_credit_amount": entry.get("refunded_credit_amount"),
        "reversed_credit_amount": entry.get("reversed_credit_amount"),
        "currency": entry.get("currency"),
        "dry_run": bool(entry.get("dry_run")),
        "preflight_only": bool(entry.get("preflight_only")),
        "smoke_test_mode": bool(entry.get("smoke_test_mode")),
        "denial_reason": entry.get("denial_reason") or "",
        "message": "Billing evidence recorded. No live credit mutation has been performed.",
        "billing_mutation_attempted": False,
        "stripe_call_attempted": False,
        "provider_call_attempted": False,
        "aws_call_attempted": False,
        "credit_mutation_attempted": False,
        "credential_values_exposed": False,
        "provider_secret_values_visible": False,
        "internal_config_exposed": False,
        "customer_safe": True,
    }


def build_admin_safe_billing_diagnostics_view(entry_or_payload: Mapping[str, Any] | None) -> Dict[str, Any]:
    entry = dict(entry_or_payload or {})
    if "ledger_event_id" not in entry:
        entry = build_billing_audit_event_placeholder(entry)
    return redact_secret_values({
        **entry,
        "admin_safe": True,
        "billing_mutation_attempted": False,
        "stripe_call_attempted": False,
        "provider_call_attempted": False,
        "aws_call_attempted": False,
        "credit_mutation_attempted": False,
        "provider_secret_values_visible": False,
        "credential_values_exposed": False,
    })


def validate_billing_credit_ledger_entry(entry: Mapping[str, Any] | None) -> Dict[str, Any]:
    entry = dict(entry or {})
    errors: List[str] = []
    for key in ("ledger_event_id", "event_type", "job_id", "actor_role", "authority_level", "mutation_mode", "status", "audit", "created_at"):
        if key not in entry:
            errors.append(f"missing_{key}")
    if entry.get("event_type") not in LEDGER_EVENT_TYPES:
        errors.append("unsupported_ledger_event_type")
    if entry.get("mutation_mode") != NO_MUTATION_MODE:
        errors.append("mutation_mode_not_placeholder")
    for key in ("billing_mutation_attempted", "stripe_call_attempted", "provider_call_attempted", "aws_call_attempted", "credit_mutation_attempted", "rds_write_attempted"):
        if entry.get(key):
            errors.append(key)
    validation = entry.get("final_27_agent_validation") or {}
    if validation.get("internal_only_agent_keys") and entry.get("event_type") in {"credit_reserved_placeholder", "credit_reservation_requested"}:
        errors.append("internal_only_agent_credit_reservation_attempted")
    return {
        "valid": not errors,
        "errors": sorted(set(errors)),
        "billing_mutation_attempted": False,
        "stripe_call_attempted": False,
        "provider_call_attempted": False,
        "aws_call_attempted": False,
        "credit_mutation_attempted": False,
        "credential_values_exposed": False,
        "customer_safe": True,
    }
