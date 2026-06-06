from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from backend.app.core.canonical_billing_state_runtime import get_canonical_billing_state
from backend.app.core.stripe_tenant_mapping_store import list_stripe_tenant_mappings


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_bool(value: Any) -> bool:
    return bool(value)


def _find_mapping_for_tenant(tenant_id: str) -> Optional[Dict[str, Any]]:
    mappings = list_stripe_tenant_mappings(limit=500).get("mappings", [])
    for item in mappings:
        if item.get("tenant_id") == tenant_id:
            return item
    return None


def customer_billing_visibility(tenant_id: str) -> Dict[str, Any]:
    mapping = _find_mapping_for_tenant(tenant_id)
    canonical_state = get_canonical_billing_state(tenant_id)

    state = canonical_state.get("durable_state") or {}

    subscription_status = (
        canonical_state.get("subscription_status")
        or (mapping or {}).get("subscription_status")
        or "unknown"
    )

    client_execution_allowed = canonical_state.get("client_execution_allowed")
    credit_state = canonical_state.get("credit_state")
    execution_block_reason = canonical_state.get("execution_block_reason")
    retry_interval_hours = state.get("retry_interval_hours")

    failed_payment_warning = not bool(canonical_state.get("execution_allowed"))

    return {
        "success": True,
        "tenant_id": tenant_id,
        "billing_visibility": {
            "subscription_status": subscription_status,
            "package_name": (mapping or {}).get("package_name"),
            "client_execution_allowed": client_execution_allowed,
            "credit_state": credit_state,
            "execution_block_reason": execution_block_reason,
            "failed_payment_warning": failed_payment_warning,
            "retry_interval_hours": retry_interval_hours,
            "month_to_month": True,
            "lock_in_contract": False,
            "owner_admin_access_unaffected": True,
            "next_billing_date": state.get("current_period_end") or state.get("next_billing_date"),
            "last_webhook_processed_at": state.get("last_webhook_processed_at"),
            "canonical_subscription_source": canonical_state.get("canonical_source"),
        },
        "stripe_mapping": {
            "mapping_available": mapping is not None,
            "stripe_customer_id_present": bool((mapping or {}).get("stripe_customer_id")),
            "stripe_subscription_id_present": bool((mapping or {}).get("stripe_subscription_id")),
            "credential_values_exposed": False,
        },
        "invoices": {
            "available": False,
            "reason": "stripe_live_invoice_fetch_requires_configured_stripe_credentials",
            "safe_placeholder": True,
            "credential_values_exposed": False,
        },
        "checked_at": utc_now_iso(),
    }


def billing_portal_readiness(tenant_id: str) -> Dict[str, Any]:
    mapping = _find_mapping_for_tenant(tenant_id)
    stripe_secret_configured = bool(os.getenv("STRIPE_SECRET_KEY"))
    return_url = os.getenv("STRIPE_BILLING_PORTAL_RETURN_URL")

    try:
        import stripe  # type: ignore
        stripe_sdk_available = True
    except Exception:
        stripe_sdk_available = False

    return {
        "success": True,
        "tenant_id": tenant_id,
        "stripe_sdk_available": stripe_sdk_available,
        "stripe_secret_key_configured": stripe_secret_configured,
        "return_url_configured": bool(return_url),
        "stripe_customer_mapping_available": bool(mapping and mapping.get("stripe_customer_id")),
        "ready_for_live_billing_portal": bool(
            stripe_sdk_available
            and stripe_secret_configured
            and return_url
            and mapping
            and mapping.get("stripe_customer_id")
        ),
        "credential_values_exposed": False,
        "checked_at": utc_now_iso(),
    }


def create_customer_billing_portal_session(tenant_id: str) -> Dict[str, Any]:
    mapping = _find_mapping_for_tenant(tenant_id)
    readiness = billing_portal_readiness(tenant_id)

    if not mapping or not mapping.get("stripe_customer_id"):
        return {
            "success": False,
            "status": "billing_portal_not_created",
            "reason": "stripe_customer_mapping_missing",
            "tenant_id": tenant_id,
            "readiness": readiness,
            "credential_values_exposed": False,
        }

    if not readiness.get("stripe_secret_key_configured"):
        return {
            "success": False,
            "status": "billing_portal_not_created",
            "reason": "stripe_secret_key_not_configured",
            "tenant_id": tenant_id,
            "readiness": readiness,
            "credential_values_exposed": False,
        }

    if not readiness.get("stripe_sdk_available"):
        return {
            "success": False,
            "status": "billing_portal_not_created",
            "reason": "stripe_sdk_not_installed",
            "tenant_id": tenant_id,
            "readiness": readiness,
            "credential_values_exposed": False,
        }

    return_url = os.getenv("STRIPE_BILLING_PORTAL_RETURN_URL")
    if not return_url:
        return {
            "success": False,
            "status": "billing_portal_not_created",
            "reason": "stripe_billing_portal_return_url_missing",
            "tenant_id": tenant_id,
            "readiness": readiness,
            "credential_values_exposed": False,
        }

    try:
        import stripe  # type: ignore

        stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

        session = stripe.billing_portal.Session.create(
            customer=mapping["stripe_customer_id"],
            return_url=return_url,
        )

        return {
            "success": True,
            "status": "billing_portal_session_created",
            "tenant_id": tenant_id,
            "portal_url": getattr(session, "url", None),
            "stripe_customer_id_present": True,
            "credential_values_exposed": False,
            "created_at": utc_now_iso(),
        }

    except Exception as exc:
        return {
            "success": False,
            "status": "billing_portal_creation_failed",
            "reason": type(exc).__name__,
            "safe_message": str(exc),
            "tenant_id": tenant_id,
            "credential_values_exposed": False,
            "created_at": utc_now_iso(),
        }
