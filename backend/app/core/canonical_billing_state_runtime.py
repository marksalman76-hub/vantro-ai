from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from backend.app.core.durable_billing_state_store import get_billing_runtime_state


OWNER_ADMIN_ROLES = {"owner", "admin", "owner_admin", "platform_admin", "system"}

ACTIVE_SUBSCRIPTION_STATUSES = {
    "active",
    "trialing",
    "trial_active",
    "enterprise_manual",
    "paid",
    "checkout_started",
}

BLOCKED_SUBSCRIPTION_STATUSES = {
    "past_due",
    "unpaid",
    "cancelled",
    "canceled",
    "incomplete_expired",
    "suspended",
}

ATTENTION_SUBSCRIPTION_STATUSES = {
    "incomplete",
    "payment_attention_required",
    "failed",
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalise_actor_role(actor_role: Optional[str]) -> str:
    return (actor_role or "").strip().lower()


def owner_admin_bypasses_client_billing(actor_role: Optional[str]) -> bool:
    return normalise_actor_role(actor_role) in OWNER_ADMIN_ROLES


def normalise_subscription_status(status: Any) -> str:
    value = str(status or "unknown").strip().lower()
    if value == "cancel_at_period_end":
        return "active"
    if value == "cancelled":
        return "cancelled"
    if value == "canceled":
        return "canceled"
    return value or "unknown"


def evaluate_subscription_status(
    status: Any,
    *,
    cancel_at_period_end: Optional[bool] = None,
) -> Dict[str, Any]:
    normalised = normalise_subscription_status(status)

    if cancel_at_period_end and normalised in ACTIVE_SUBSCRIPTION_STATUSES:
        return {
            "subscription_status": normalised,
            "subscription_execution_allowed": True,
            "subscription_status_category": "active_until_period_end",
            "subscription_block_reason": None,
        }

    if normalised in ACTIVE_SUBSCRIPTION_STATUSES:
        return {
            "subscription_status": normalised,
            "subscription_execution_allowed": True,
            "subscription_status_category": "active",
            "subscription_block_reason": None,
        }

    if normalised in BLOCKED_SUBSCRIPTION_STATUSES:
        return {
            "subscription_status": normalised,
            "subscription_execution_allowed": False,
            "subscription_status_category": "blocked",
            "subscription_block_reason": normalised,
        }

    if normalised in ATTENTION_SUBSCRIPTION_STATUSES:
        return {
            "subscription_status": normalised,
            "subscription_execution_allowed": False,
            "subscription_status_category": "attention_required",
            "subscription_block_reason": normalised,
        }

    return {
        "subscription_status": normalised,
        "subscription_execution_allowed": True,
        "subscription_status_category": "unknown_no_runtime_block",
        "subscription_block_reason": None,
    }


def _subscription_from_postgres(tenant_id: str) -> Dict[str, Any]:
    try:
        from backend.app.core.subscription_billing_runtime import get_subscription

        result = get_subscription(tenant_id)
    except Exception as exc:
        return {
            "success": False,
            "source": "postgres_subscription_billing_runtime",
            "error": type(exc).__name__,
        }

    if not result.get("success"):
        return {
            "success": False,
            "source": "postgres_subscription_billing_runtime",
            "error": result.get("error") or "subscription_not_found",
        }

    return {
        "success": True,
        "source": "postgres_subscription_billing_runtime",
        "subscription": result.get("subscription") or {},
    }


def get_canonical_billing_state(tenant_id: Optional[str]) -> Dict[str, Any]:
    if not tenant_id:
        return {
            "success": False,
            "tenant_id": tenant_id,
            "state_found": False,
            "reason": "tenant_id_required",
            "checked_at": utc_now_iso(),
        }

    postgres_result = _subscription_from_postgres(tenant_id)
    postgres_subscription = postgres_result.get("subscription") if postgres_result.get("success") else None
    durable_result = get_billing_runtime_state(tenant_id=tenant_id)
    durable_state = durable_result.get("state") if durable_result.get("success") else None

    subscription_status = (
        (postgres_subscription or {}).get("billing_status")
        or (postgres_subscription or {}).get("subscription_status")
        or (durable_state or {}).get("subscription_status")
        or "unknown"
    )
    cancel_at_period_end = bool(
        (postgres_subscription or {}).get("cancel_at_period_end")
        or (durable_state or {}).get("cancel_at_period_end")
    )
    status_decision = evaluate_subscription_status(
        subscription_status,
        cancel_at_period_end=cancel_at_period_end,
    )

    client_execution_allowed = status_decision["subscription_execution_allowed"]
    durable_client_execution_allowed = (durable_state or {}).get("client_execution_allowed")
    if client_execution_allowed is None:
        client_execution_allowed = durable_client_execution_allowed
    if postgres_subscription is None and durable_client_execution_allowed is not None:
        client_execution_allowed = durable_client_execution_allowed

    durable_credit_state = (durable_state or {}).get("credit_state")
    credit_state = durable_credit_state if postgres_subscription is None else None
    execution_block_reason = (
        (durable_state or {}).get("execution_block_reason")
        if postgres_subscription is None
        else None
    )

    blocked = (
        client_execution_allowed is False
        or status_decision["subscription_execution_allowed"] is False
        or credit_state == "blocked"
    )

    reason = "canonical_billing_state_allows_execution"
    if blocked:
        reason = (
            execution_block_reason
            or status_decision.get("subscription_block_reason")
            or credit_state
            or "billing_execution_blocked"
        )
    elif not durable_state and not postgres_subscription:
        reason = "no_canonical_billing_state_found"

    return {
        "success": True,
        "tenant_id": tenant_id,
        "state_found": bool(durable_state or postgres_subscription),
        "canonical_source": "postgres_client_subscriptions" if postgres_subscription else "durable_billing_state_store_fallback" if durable_state else "none",
        "subscription_status": status_decision["subscription_status"],
        "subscription_status_category": status_decision["subscription_status_category"],
        "subscription_execution_allowed": status_decision["subscription_execution_allowed"],
        "client_execution_allowed": client_execution_allowed,
        "credit_state": credit_state,
        "durable_credit_state": durable_credit_state,
        "execution_block_reason": execution_block_reason,
        "execution_allowed": not blocked,
        "reason": reason,
        "durable_state": durable_state,
        "durable_state_role": "audit_cache_fallback",
        "postgres_subscription_available": bool(postgres_subscription),
        "credential_values_exposed": False,
        "customer_safe_visibility": True,
        "checked_at": utc_now_iso(),
    }


def evaluate_billing_execution_entitlement(
    tenant_id: Optional[str],
    actor_role: Optional[str],
) -> Dict[str, Any]:
    if owner_admin_bypasses_client_billing(actor_role):
        return {
            "allowed": True,
            "reason": "owner_admin_billing_bypass",
            "tenant_id": tenant_id,
            "actor_role": actor_role,
            "billing_guard_applied": True,
            "owner_admin_access_unaffected": True,
            "canonical_billing_source": "owner_admin_bypass",
        }

    if not tenant_id:
        return {
            "allowed": False,
            "reason": "tenant_id_required_for_client_execution",
            "tenant_id": tenant_id,
            "actor_role": actor_role,
            "billing_guard_applied": True,
        }

    canonical_state = get_canonical_billing_state(tenant_id)
    if not canonical_state.get("success"):
        return {
            "allowed": False,
            "reason": canonical_state.get("reason") or "canonical_billing_state_unavailable",
            "tenant_id": tenant_id,
            "actor_role": actor_role,
            "billing_guard_applied": True,
            "canonical_billing_state": canonical_state,
        }

    return {
        "allowed": bool(canonical_state.get("execution_allowed")),
        "reason": canonical_state.get("reason"),
        "tenant_id": tenant_id,
        "actor_role": actor_role,
        "billing_guard_applied": True,
        "subscription_status": canonical_state.get("subscription_status"),
        "subscription_status_category": canonical_state.get("subscription_status_category"),
        "credit_state": canonical_state.get("credit_state"),
        "client_execution_allowed": canonical_state.get("client_execution_allowed"),
        "canonical_billing_source": canonical_state.get("canonical_source"),
        "state": canonical_state.get("durable_state"),
        "canonical_billing_state": canonical_state,
    }
