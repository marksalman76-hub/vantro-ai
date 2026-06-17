from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
from typing import Any, Dict, Mapping, Optional

from backend.app.runtime.api_acceptance_entitlement_boundary import (
    build_api_acceptance_entitlement_decision,
    validate_api_acceptance_entitlement_decision,
)
from backend.app.runtime.billing_credit_ledger_boundary import (
    build_admin_override_placeholder,
    build_admin_safe_billing_diagnostics_view,
    build_client_safe_billing_view,
    build_credit_finalization_placeholder,
    build_credit_refund_placeholder,
    build_credit_reservation_placeholder,
    build_credit_reversal_placeholder,
    build_provider_actual_cost_placeholder,
    build_provider_cost_estimate_placeholder,
    validate_billing_credit_ledger_entry,
)


BILLING_CREDIT_SPEND_GOVERNANCE_VERSION = "billing_credit_spend_governance_v1"
OWNER_ROLES = {"admin", "owner", "platform_owner", "super_admin"}
TRUE_VALUES = {"1", "true", "yes", "on", "enabled"}
SECRET_KEY_MARKERS = (
    "api_key",
    "apikey",
    "authorization",
    "bearer",
    "card",
    "credential",
    "password",
    "private_key",
    "provider_api_key",
    "secret",
    "stripe_secret_key",
    "token",
)
SAFE_BOOLEAN_MARKER_KEYS = {
    "credential_values_exposed",
    "provider_secret_values_visible",
    "stripe_live_charge_attempted",
    "stripe_call_attempted",
    "provider_call_attempted",
    "media_generation_attempted",
    "real_customer_billing_mutation_attempted",
    "real_customer_credit_mutation_attempted",
    "customer_traffic_attempted",
    "public_cutover_enabled",
    "render_removal_attempted",
    "billing_mutation_attempted",
    "credit_mutation_attempted",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


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
    if text in TRUE_VALUES:
        return True
    if text in {"0", "false", "no", "off", "disabled"}:
        return False
    return default


def safe_hash(value: Any, length: int = 12) -> str:
    text = clean_text(value, 2000)
    if not text:
        return ""
    return sha256(text.encode("utf-8", errors="ignore")).hexdigest()[:length]


def redact_secret_values(value: Any) -> Any:
    if isinstance(value, dict):
        cleaned: Dict[str, Any] = {}
        for key, item in value.items():
            key_l = str(key).lower()
            if key_l in SAFE_BOOLEAN_MARKER_KEYS:
                cleaned[key] = item
            elif any(marker in key_l for marker in SECRET_KEY_MARKERS):
                cleaned[key] = "[redacted]"
            elif key_l in {
                "account_id",
                "checkout_session_id",
                "client_id",
                "correlation_id",
                "customer_id",
                "idempotency_key",
                "invoice_id",
                "job_id",
                "request_id",
                "stripe_event_id",
                "tenant_id",
            }:
                cleaned[f"{key}_hash"] = safe_hash(item)
            else:
                cleaned[key] = redact_secret_values(item)
        return cleaned
    if isinstance(value, list):
        return [redact_secret_values(item) for item in value]
    return value


def base_side_effect_guards() -> Dict[str, bool]:
    return {
        "stripe_live_charge_attempted": False,
        "stripe_call_attempted": False,
        "provider_call_attempted": False,
        "media_generation_attempted": False,
        "real_customer_billing_mutation_attempted": False,
        "real_customer_credit_mutation_attempted": False,
        "customer_traffic_attempted": False,
        "public_cutover_enabled": False,
        "render_removal_attempted": False,
        "billing_mutation_attempted": False,
        "credit_mutation_attempted": False,
    }


def synthetic_media_payload(overrides: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    payload = {
        "job_id": "synthetic_billing_governance_job",
        "customer_id": "synthetic_non_customer",
        "tenant_id": "synthetic_non_customer_tenant",
        "actor_role": "client",
        "requested_by_role": "client",
        "package_name": "business",
        "entitlement_status": "active",
        "active_agents": ["marketing_specialist_agent", "ugc_media_agent"],
        "selected_agent": "marketing_specialist_agent",
        "selected_agents": ["marketing_specialist_agent", "ugc_media_agent"],
        "agent_ids": ["marketing_specialist_agent", "ugc_media_agent"],
        "task_type": "media_generation",
        "workflow_type": "universal_complete_media",
        "media_type": "complete_video",
        "asset_type": "video",
        "video_provider": "runway",
        "audio_provider": "elevenlabs",
        "duration_seconds": 25,
        "segment_count": 5,
        "estimated_credit_cost": 10,
        "provider_estimated_cost": 8,
        "provider_actual_cost": 7,
        "provider_cost_cap": 12,
        "currency": "credits",
        "approval_required_for_spend": True,
        "approval_status": "owner_approved",
        "credit_reservation_status": "reserved",
        "correlation_id": "synthetic_billing_governance_correlation",
        "dry_run": False,
        "preflight_only": False,
        "smoke_test_mode": False,
    }
    payload.update(dict(overrides or {}))
    return payload


def evaluate_provider_cost_cap(payload: Mapping[str, Any]) -> Dict[str, Any]:
    actor_role = clean_text(payload.get("actor_role") or payload.get("requested_by_role") or "client", 80).lower()
    owner_authority = actor_role in OWNER_ROLES
    estimated_cost = clean_float(payload.get("provider_estimated_cost") or payload.get("estimated_provider_cost"))
    cap = clean_float(payload.get("provider_cost_cap") or payload.get("provider_cost_allowance") or payload.get("credit_allowance"), 0.0)
    owner_approval = clean_bool(
        payload.get("owner_provider_cost_approval")
        or payload.get("cost_safety_confirmed")
        or payload.get("paid_provider_risk_confirmed")
        or payload.get("credit_risk_acknowledged")
    )
    cap_exceeded = bool(cap and estimated_cost > cap)
    override_allowed = bool(cap_exceeded and owner_authority and owner_approval)
    blocked = bool(cap_exceeded and not override_allowed)
    return redact_secret_values({
        "boundary": "billing_credit_spend_governance_provider_cost_cap",
        "provider_estimated_cost": estimated_cost,
        "provider_cost_cap": cap,
        "provider_cost_cap_exceeded": cap_exceeded,
        "provider_cost_cap_blocked_without_approval": blocked,
        "owner_override_required": bool(cap_exceeded),
        "owner_override_authority_present": owner_authority,
        "owner_provider_cost_approval_present": owner_approval,
        "owner_override_allowed": override_allowed,
        "provider_execution_allowed_after_cost_gate": not blocked,
        "provider_call_attempted": False,
        "media_generation_attempted": False,
        "stripe_live_charge_attempted": False,
        "billing_mutation_attempted": False,
        "credit_mutation_attempted": False,
        "customer_safe": True,
    })


def build_mock_stripe_test_reconciliation_shape(payload: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "mode": "test_fixture_only",
        "mock_webhook_reconciliation_represented": True,
        "stripe_live_charge_attempted": False,
        "stripe_api_call_attempted": False,
        "stripe_event_reference_hash": safe_hash(payload.get("stripe_event_id") or "evt_test_synthetic_billing_governance"),
        "checkout_session_reference_hash": safe_hash(payload.get("checkout_session_id") or "cs_test_synthetic_billing_governance"),
        "invoice_reference_hash": safe_hash(payload.get("invoice_id") or "in_test_synthetic_billing_governance"),
        "billing_mismatch_or_failed_paid_job_supported": True,
        "refund_or_reconciliation_shape_present": True,
        "customer_safe": True,
        "credential_values_exposed": False,
    }


def build_billing_credit_spend_governance_proof(payload: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    base_payload = synthetic_media_payload(payload)

    missing_entitlement_payload = synthetic_media_payload({
        "entitlement_status": "missing",
        "credit_reservation_status": "not_reserved",
        "approval_status": "pending",
    })
    entitlement_decision = build_api_acceptance_entitlement_decision(missing_entitlement_payload)

    allowed_decision = build_api_acceptance_entitlement_decision(base_payload)
    allowed_validation = validate_api_acceptance_entitlement_decision(allowed_decision)
    reservation = build_credit_reservation_placeholder(allowed_decision, envelope=base_payload)
    reservation_validation = validate_billing_credit_ledger_entry(reservation)

    high_cost_payload = synthetic_media_payload({
        "provider_estimated_cost": 30,
        "provider_cost_cap": 12,
        "approval_status": "pending",
        "owner_provider_cost_approval": False,
    })
    cost_block = evaluate_provider_cost_cap(high_cost_payload)
    cost_estimate_event = build_provider_cost_estimate_placeholder(high_cost_payload)

    client_override_payload = synthetic_media_payload({
        "provider_estimated_cost": 30,
        "provider_cost_cap": 12,
        "owner_provider_cost_approval": True,
    })
    client_override = evaluate_provider_cost_cap(client_override_payload)

    owner_override_payload = synthetic_media_payload({
        "actor_role": "owner",
        "requested_by_role": "owner",
        "provider_estimated_cost": 30,
        "provider_cost_cap": 12,
        "owner_provider_cost_approval": True,
        "admin_override_reason": "synthetic_cost_cap_exception",
    })
    owner_override = evaluate_provider_cost_cap(owner_override_payload)
    owner_override_audit = build_admin_override_placeholder(owner_override_payload)

    success_payload = synthetic_media_payload({"actual_credit_cost": 8, "provider_actual_cost": 7.5})
    finalization = build_credit_finalization_placeholder(success_payload)
    actual_cost_event = build_provider_actual_cost_placeholder(success_payload)

    failure_payload = synthetic_media_payload({"reversal_credit_amount": 10, "provider_actual_cost": 0})
    reversal = build_credit_reversal_placeholder(failure_payload)

    refund_payload = synthetic_media_payload({"refund_credit_amount": 10, "billing_mismatch_reason": "synthetic_failed_paid_job"})
    refund = build_credit_refund_placeholder(refund_payload)
    stripe_test_reconciliation = build_mock_stripe_test_reconciliation_shape(refund_payload)

    client_view = build_client_safe_billing_view(reservation)
    admin_diagnostics = build_admin_safe_billing_diagnostics_view(reservation)

    package_entitlement_required = bool(
        entitlement_decision.get("allowed") is False
        and "package_entitlement_not_active" in (entitlement_decision.get("denial_reasons") or [])
    )
    credit_reserve_before_execution_passed = bool(
        allowed_decision.get("allowed")
        and reservation.get("event_type") == "credit_reserved_placeholder"
        and reservation.get("reserved_credit_amount", 0) > 0
        and reservation.get("provider_call_attempted") is False
    )
    owner_override_audited = bool(
        client_override.get("owner_override_allowed") is False
        and owner_override.get("owner_override_allowed") is True
        and owner_override_audit.get("event_type") == "admin_override_recorded"
        and owner_override_audit.get("status") == "admin_override_audit_only"
    )
    credit_finalize_after_success_represented = bool(
        finalization.get("event_type") == "credit_finalized_placeholder"
        and finalization.get("finalized_credit_amount", 0) > 0
        and actual_cost_event.get("event_type") == "provider_actual_cost_recorded"
    )
    credit_reversal_after_failure_represented = bool(
        reversal.get("event_type") == "credit_reversed_placeholder"
        and reversal.get("reversed_credit_amount", 0) > 0
    )
    refund_or_reconciliation_shape_present = bool(
        refund.get("event_type") == "credit_refunded_placeholder"
        and refund.get("refunded_credit_amount", 0) > 0
        and stripe_test_reconciliation.get("refund_or_reconciliation_shape_present")
    )
    client_billing_view_redacted = bool(
        client_view.get("customer_safe")
        and client_view.get("internal_config_exposed") is False
        and "provider_estimated_cost" not in client_view
        and "stripe_reference" not in client_view
    )
    admin_billing_diagnostics_redacted = bool(
        admin_diagnostics.get("credential_values_exposed") is False
        and admin_diagnostics.get("provider_secret_values_visible") is False
        and admin_diagnostics.get("stripe_call_attempted") is False
    )

    proof = {
        "boundary": "billing_credit_spend_governance",
        "diagnostic_version": BILLING_CREDIT_SPEND_GOVERNANCE_VERSION,
        "created_at": utc_now(),
        "billing_credit_governance_attempted": True,
        "billing_credit_governance_passed": False,
        "package_entitlement_required": package_entitlement_required,
        "credit_reserve_before_execution_passed": credit_reserve_before_execution_passed,
        "provider_cost_cap_blocked_without_approval": bool(cost_block.get("provider_cost_cap_blocked_without_approval")),
        "owner_override_audited": owner_override_audited,
        "credit_finalize_after_success_represented": credit_finalize_after_success_represented,
        "credit_reversal_after_failure_represented": credit_reversal_after_failure_represented,
        "refund_or_reconciliation_shape_present": refund_or_reconciliation_shape_present,
        "client_billing_view_redacted": client_billing_view_redacted,
        "admin_billing_diagnostics_redacted": admin_billing_diagnostics_redacted,
        "stripe_test_or_mock_reconciliation_represented": bool(stripe_test_reconciliation.get("mock_webhook_reconciliation_represented")),
        "entitlement_decision": {
            "allowed": bool(entitlement_decision.get("allowed")),
            "denial_reasons": entitlement_decision.get("denial_reasons") or [],
            "client_safe_view": entitlement_decision.get("client_safe_view") or {},
        },
        "allowed_decision_validation": allowed_validation,
        "reservation_validation": reservation_validation,
        "provider_cost_cap_decision": cost_block,
        "provider_cost_estimate_event": cost_estimate_event,
        "owner_override_decision": owner_override,
        "owner_override_audit": owner_override_audit,
        "credit_finalization_event": finalization,
        "credit_reversal_event": reversal,
        "refund_event": refund,
        "provider_actual_cost_event": actual_cost_event,
        "stripe_test_reconciliation": stripe_test_reconciliation,
        "client_billing_view": client_view,
        "admin_billing_diagnostics": admin_diagnostics,
        "synthetic_job_reference_hash": safe_hash(base_payload.get("job_id")),
        "synthetic_tenant_reference_hash": safe_hash(base_payload.get("tenant_id")),
        **base_side_effect_guards(),
        "customer_safe": True,
        "credential_values_exposed": False,
        "provider_secret_values_visible": False,
    }

    proof["billing_credit_governance_passed"] = bool(
        proof["package_entitlement_required"]
        and proof["credit_reserve_before_execution_passed"]
        and proof["provider_cost_cap_blocked_without_approval"]
        and proof["owner_override_audited"]
        and proof["credit_finalize_after_success_represented"]
        and proof["credit_reversal_after_failure_represented"]
        and proof["refund_or_reconciliation_shape_present"]
        and proof["client_billing_view_redacted"]
        and proof["admin_billing_diagnostics_redacted"]
        and proof["stripe_live_charge_attempted"] is False
        and proof["provider_call_attempted"] is False
        and proof["media_generation_attempted"] is False
        and proof["real_customer_billing_mutation_attempted"] is False
        and proof["real_customer_credit_mutation_attempted"] is False
        and proof["customer_traffic_attempted"] is False
        and proof["public_cutover_enabled"] is False
        and proof["render_removal_attempted"] is False
    )
    return redact_secret_values(proof)
