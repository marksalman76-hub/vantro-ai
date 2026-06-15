from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Mapping
import uuid

from backend.app.runtime.real_agent_component_catalogue import (
    CLIENT_FACING_AGENTS,
    FINAL_APPROVED_VISIBLE_AGENT_COUNT,
    FINAL_APPROVED_VISIBLE_AGENT_SOURCE,
    SYSTEM_AGENTS,
)


PACKAGE_RULES: Dict[str, Dict[str, Any]] = {
    "starter": {"max_selectable_agents": 3, "enterprise_only_allowed": False},
    "growth": {"max_selectable_agents": 7, "enterprise_only_allowed": False},
    "business": {"max_selectable_agents": 10, "enterprise_only_allowed": False},
    "enterprise": {"max_selectable_agents": 27, "enterprise_only_allowed": True},
}

ADMIN_ROLES = {"admin", "owner", "platform_owner", "super_admin"}
DRY_RUN_TRUE_VALUES = {"1", "true", "yes", "on", "enabled"}
SPEND_SENSITIVE_TASK_TYPES = {
    "media_generation",
    "universal_complete_media",
    "generated_site",
    "site_generation",
    "integration_job",
    "provider_execution",
    "support_admin_action",
}
APPROVED_STATUSES = {"approved", "owner_approved", "admin_approved", "not_required", "admin_unrestricted"}
RESERVED_CREDIT_STATUSES = {"reserved", "reservation_ready", "confirmed", "admin_unrestricted", "not_required"}

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


def safe_id(prefix: str = "acceptance_enforcement") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def clean_text(value: Any, limit: int = 1000) -> str:
    return str(value or "").strip()[:limit]


def clean_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    text = str(value or "").strip().lower()
    if text in DRY_RUN_TRUE_VALUES:
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


def normalise_package(value: Any) -> str:
    package = clean_text(value or "starter", 80).lower()
    aliases = {"pro": "business", "professional": "business", "premium": "business"}
    package = aliases.get(package, package)
    return package if package in PACKAGE_RULES else "starter"


def normalise_role(value: Any) -> str:
    role = clean_text(value or "client", 80).lower()
    if role in ADMIN_ROLES:
        return "admin"
    if role == "system":
        return "system"
    return "client"


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


def selected_agent_keys(payload: Mapping[str, Any]) -> List[str]:
    selected = ensure_list(payload.get("selected_agents"))
    selected.extend(key for key in ensure_list(payload.get("agent_ids")) if key not in selected)
    selected_agent = clean_text(first_value(payload, ("selected_agent", "agent_id"), ""), 180).lower()
    if selected_agent and selected_agent not in selected:
        selected.insert(0, selected_agent)
    return selected


def active_entitled_agent_keys(payload: Mapping[str, Any]) -> List[str]:
    for key in ("active_agents", "purchased_agents", "entitled_agents", "allowed_agent_ids", "client_visible_agents"):
        values = ensure_list(payload.get(key))
        if values:
            return values
    return []


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


def build_final_27_agent_validation(selected_agents: List[str], package_name: str) -> Dict[str, Any]:
    visible_by_key = {agent["key"]: agent for agent in CLIENT_FACING_AGENTS}
    system_keys = {agent["key"] for agent in SYSTEM_AGENTS}
    rules = PACKAGE_RULES[package_name]
    invalid: List[str] = []
    internal_only: List[str] = []
    enterprise_blocked: List[str] = []

    for agent_key in selected_agents:
        if agent_key in system_keys:
            internal_only.append(agent_key)
            continue
        agent = visible_by_key.get(agent_key)
        if not agent:
            invalid.append(agent_key)
            continue
        if agent.get("enterprise_only") and not rules["enterprise_only_allowed"]:
            enterprise_blocked.append(agent_key)

    over_package_agent_limit = len(selected_agents) > int(rules["max_selectable_agents"])
    valid = not invalid and not internal_only and not enterprise_blocked and not over_package_agent_limit
    return {
        "valid": valid,
        "source": FINAL_APPROVED_VISIBLE_AGENT_SOURCE,
        "expected_visible_count": FINAL_APPROVED_VISIBLE_AGENT_COUNT,
        "actual_visible_count": len(CLIENT_FACING_AGENTS),
        "selected_agents": selected_agents,
        "invalid_agent_keys": invalid,
        "internal_only_agent_keys": internal_only,
        "enterprise_blocked_agent_keys": enterprise_blocked,
        "over_package_agent_limit": over_package_agent_limit,
        "max_selectable_agents": rules["max_selectable_agents"],
        "system_agents_client_selectable": False,
    }


def is_spend_sensitive(payload: Mapping[str, Any]) -> bool:
    explicit = payload.get("spend_sensitive")
    if explicit is not None:
        return clean_bool(explicit)
    task_type = clean_text(payload.get("task_type") or payload.get("workflow_type"), 160).lower()
    provider_requested = any(
        clean_text(payload.get(key))
        for key in (
            "video_provider",
            "audio_provider",
            "image_provider",
            "avatar_provider",
            "provider",
            "integration_provider",
        )
    )
    estimated_credits = clean_text(payload.get("estimated_credits_required") or payload.get("credits_required"))
    return task_type in SPEND_SENSITIVE_TASK_TYPES or provider_requested or bool(estimated_credits)


def build_denial_reasons(
    *,
    actor_role: str,
    final_validation: Mapping[str, Any],
    entitlement_status: str,
    active_agents: List[str],
    selected_agents: List[str],
    credit_reservation_required: bool,
    credit_reservation_status: str,
    approval_required: bool,
    approval_status: str,
) -> List[str]:
    if actor_role == "admin":
        if final_validation.get("internal_only_agent_keys"):
            return ["internal_agent_not_visible_or_selectable"]
        return []

    denial_reasons: List[str] = []
    if final_validation.get("invalid_agent_keys") or final_validation.get("internal_only_agent_keys"):
        denial_reasons.append("selected_agent_not_available")
    if final_validation.get("enterprise_blocked_agent_keys"):
        denial_reasons.append("agent_requires_enterprise_package")
    if final_validation.get("over_package_agent_limit"):
        denial_reasons.append("package_agent_limit_exceeded")
    if entitlement_status not in {"active", "admin_unrestricted"}:
        denial_reasons.append("package_entitlement_not_active")
    missing_active = [agent for agent in selected_agents if agent not in active_agents]
    if selected_agents and missing_active:
        denial_reasons.append("selected_agent_not_in_active_entitlement")
    if credit_reservation_required and credit_reservation_status not in RESERVED_CREDIT_STATUSES:
        denial_reasons.append("credit_reservation_required")
    if approval_required and approval_status not in APPROVED_STATUSES:
        denial_reasons.append("owner_approval_required")
    return denial_reasons


@dataclass(frozen=True)
class CanonicalApiAcceptanceEntitlementDecision:
    allowed: bool
    actor_role: str
    authority_level: str
    package_name: str
    entitlement_status: str
    selected_agents: List[str]
    active_entitled_agents: List[str]
    final_27_agent_validation: Dict[str, Any]
    credit_reservation_required: bool
    credit_reservation_status: str
    credit_finalization_status: str
    refund_reversal_status: str
    approval_required: bool
    approval_status: str
    spend_sensitive: bool
    dry_run: bool
    preflight_only: bool
    smoke_test_mode: bool
    denial_reason: str = ""
    denial_reasons: List[str] = field(default_factory=list)
    audit: Dict[str, Any] = field(default_factory=dict)
    admin_safe_view: Dict[str, Any] = field(default_factory=dict)
    client_safe_view: Dict[str, Any] = field(default_factory=dict)
    billing_mutation_attempted: bool = False
    stripe_call_attempted: bool = False
    provider_call_attempted: bool = False
    aws_call_attempted: bool = False
    credit_mutation_attempted: bool = False
    queue_mutation_attempted: bool = False
    credential_values_exposed: bool = False
    provider_secret_values_visible: bool = False
    customer_safe: bool = True
    created_at: str = field(default_factory=utc_now)

    def to_dict(self) -> Dict[str, Any]:
        return redact_secret_values(asdict(self))


def build_admin_safe_enforcement_view(decision: Mapping[str, Any]) -> Dict[str, Any]:
    return redact_secret_values({
        "allowed": bool(decision.get("allowed")),
        "actor_role": decision.get("actor_role"),
        "authority_level": decision.get("authority_level"),
        "package_name": decision.get("package_name"),
        "entitlement_status": decision.get("entitlement_status"),
        "selected_agents": decision.get("selected_agents") or [],
        "active_entitled_agents": decision.get("active_entitled_agents") or [],
        "final_27_agent_validation": decision.get("final_27_agent_validation") or {},
        "credit_reservation_required": bool(decision.get("credit_reservation_required")),
        "credit_reservation_status": decision.get("credit_reservation_status"),
        "credit_finalization_status": decision.get("credit_finalization_status"),
        "refund_reversal_status": decision.get("refund_reversal_status"),
        "approval_required": bool(decision.get("approval_required")),
        "approval_status": decision.get("approval_status"),
        "spend_sensitive": bool(decision.get("spend_sensitive")),
        "dry_run": bool(decision.get("dry_run")),
        "preflight_only": bool(decision.get("preflight_only")),
        "smoke_test_mode": bool(decision.get("smoke_test_mode")),
        "denial_reason": decision.get("denial_reason"),
        "denial_reasons": decision.get("denial_reasons") or [],
        "audit": decision.get("audit") or {},
        "billing_mutation_attempted": False,
        "stripe_call_attempted": False,
        "provider_call_attempted": False,
        "aws_call_attempted": False,
        "credit_mutation_attempted": False,
        "queue_mutation_attempted": False,
        "credential_values_exposed": False,
        "provider_secret_values_visible": False,
        "customer_safe": True,
    })


def build_client_safe_enforcement_view(decision: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "allowed": bool(decision.get("allowed")),
        "package_name": decision.get("package_name"),
        "selected_agents": decision.get("selected_agents") or [],
        "credit_reservation_required": bool(decision.get("credit_reservation_required")),
        "approval_required": bool(decision.get("approval_required")),
        "spend_sensitive": bool(decision.get("spend_sensitive")),
        "dry_run": bool(decision.get("dry_run")),
        "preflight_only": bool(decision.get("preflight_only")),
        "smoke_test_mode": bool(decision.get("smoke_test_mode")),
        "denial_reason": decision.get("denial_reason") or "",
        "message": (
            "This request is ready for acceptance."
            if decision.get("allowed")
            else "This request needs package, credit, approval, or agent access before paid execution."
        ),
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


def build_api_acceptance_entitlement_decision(payload: Mapping[str, Any] | None) -> Dict[str, Any]:
    payload = dict(payload or {})
    actor_role = normalise_role(first_value(payload, ("actor_role", "requested_by_role", "role"), "client"))
    authority_level = "owner_unrestricted" if actor_role == "admin" else ("system_internal" if actor_role == "system" else "client_package_credit_governed")
    package_name = normalise_package(first_value(payload, ("package_name", "package", "plan"), "starter"))
    selected_agents = selected_agent_keys(payload)
    active_agents = active_entitled_agent_keys(payload)
    entitlement_status = clean_text(first_value(payload, ("entitlement_status", "package_status"), "active" if actor_role == "admin" else "missing"), 120).lower()
    dry_run = clean_bool(payload.get("dry_run"))
    preflight_only = clean_bool(payload.get("preflight_only"))
    smoke_test_mode = clean_bool(payload.get("smoke_test_mode"))
    no_paid_mutation_mode = dry_run or preflight_only or smoke_test_mode
    spend_sensitive = is_spend_sensitive(payload)
    final_validation = build_final_27_agent_validation(selected_agents, package_name)

    credit_reservation_required = bool(
        actor_role == "client"
        and spend_sensitive
        and not no_paid_mutation_mode
    )
    credit_reservation_status = clean_text(
        first_value(
            payload,
            ("credit_reservation_status", "credit_status"),
            "not_required" if not credit_reservation_required else "not_reserved",
        ),
        120,
    ).lower()
    approval_required = bool(
        clean_bool(payload.get("approval_required"))
        or clean_bool(payload.get("owner_approval_required"))
        or (actor_role == "client" and spend_sensitive and not no_paid_mutation_mode and clean_bool(payload.get("approval_required_for_spend"), True))
    )
    approval_status = clean_text(first_value(payload, ("approval_status", "owner_control_status"), "not_required" if not approval_required else "pending"), 120).lower()

    denial_reasons = build_denial_reasons(
        actor_role=actor_role,
        final_validation=final_validation,
        entitlement_status=entitlement_status,
        active_agents=active_agents,
        selected_agents=selected_agents,
        credit_reservation_required=credit_reservation_required,
        credit_reservation_status=credit_reservation_status,
        approval_required=approval_required,
        approval_status=approval_status,
    )
    allowed = not denial_reasons
    audit = {
        "correlation_id": clean_text(payload.get("correlation_id") or safe_id("corr"), 180),
        "request_id": clean_text(payload.get("request_id"), 180),
        "idempotency_key": clean_text(payload.get("idempotency_key"), 180),
        "audit_event_type": "api_acceptance_entitlement_decision_prepared",
        "task_type": clean_text(payload.get("task_type"), 120),
        "workflow_type": clean_text(payload.get("workflow_type"), 160),
    }

    base = {
        "allowed": allowed,
        "actor_role": actor_role,
        "authority_level": authority_level,
        "package_name": package_name,
        "entitlement_status": "admin_unrestricted" if actor_role == "admin" else entitlement_status,
        "selected_agents": selected_agents,
        "active_entitled_agents": active_agents,
        "final_27_agent_validation": final_validation,
        "credit_reservation_required": credit_reservation_required,
        "credit_reservation_status": "not_required" if actor_role == "admin" or no_paid_mutation_mode else credit_reservation_status,
        "credit_finalization_status": "not_started",
        "refund_reversal_status": "not_started",
        "approval_required": False if actor_role == "admin" or no_paid_mutation_mode else approval_required,
        "approval_status": "admin_unrestricted" if actor_role == "admin" else ("not_required" if no_paid_mutation_mode else approval_status),
        "spend_sensitive": spend_sensitive,
        "dry_run": dry_run,
        "preflight_only": preflight_only,
        "smoke_test_mode": smoke_test_mode,
        "denial_reason": denial_reasons[0] if denial_reasons else "",
        "denial_reasons": denial_reasons,
        "audit": audit,
        "billing_mutation_attempted": False,
        "stripe_call_attempted": False,
        "provider_call_attempted": False,
        "aws_call_attempted": False,
        "credit_mutation_attempted": False,
        "queue_mutation_attempted": False,
        "credential_values_exposed": False,
        "provider_secret_values_visible": False,
        "customer_safe": True,
    }
    decision = CanonicalApiAcceptanceEntitlementDecision(
        admin_safe_view=build_admin_safe_enforcement_view(base),
        client_safe_view=build_client_safe_enforcement_view(base),
        **base,
    )
    return decision.to_dict()


def validate_api_acceptance_entitlement_decision(decision: Mapping[str, Any] | None) -> Dict[str, Any]:
    decision = dict(decision or {})
    errors: List[str] = []
    for key in ("allowed", "actor_role", "authority_level", "package_name", "selected_agents", "final_27_agent_validation", "audit"):
        if key not in decision:
            errors.append(f"missing_{key}")
    if decision.get("billing_mutation_attempted"):
        errors.append("billing_mutation_attempted")
    if decision.get("stripe_call_attempted"):
        errors.append("stripe_call_attempted")
    if decision.get("provider_call_attempted"):
        errors.append("provider_call_attempted")
    if decision.get("aws_call_attempted"):
        errors.append("aws_call_attempted")
    if decision.get("credit_mutation_attempted"):
        errors.append("credit_mutation_attempted")
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
