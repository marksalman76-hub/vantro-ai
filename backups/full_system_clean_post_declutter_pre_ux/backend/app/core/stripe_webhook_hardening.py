from __future__ import annotations

import hmac
import hashlib
from datetime import datetime, timezone
from typing import Any, Dict, Optional


RETRY_POLICY_HOURS = 48

SUBSCRIPTION_POLICY = {
    "billing_model": "automatic_recurring_stripe_subscription",
    "contract_type": "month_to_month",
    "lock_in_contract": False,
    "billing_cycle_anchor_rule": "original_cycle_date_preserved_on_failed_payment",
    "failed_payment_retry_interval_hours": RETRY_POLICY_HOURS,
    "late_payment_rule": "reactivation_does_not_shift_renewal_date",
    "cancellation_rule": "cancel_at_period_end_unless_owner_or_policy_requires_immediate",
    "owner_admin_credit_bypass": True,
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def verify_stripe_signature(
    raw_body: bytes,
    signature_header: Optional[str],
    webhook_secret: Optional[str],
) -> Dict[str, Any]:
    if not webhook_secret:
        return {
            "verified": False,
            "configured": False,
            "reason": "stripe_webhook_secret_not_configured",
        }

    if not signature_header:
        return {
            "verified": False,
            "configured": True,
            "reason": "missing_stripe_signature_header",
        }

    try:
        parts = dict(item.split("=", 1) for item in signature_header.split(",") if "=" in item)
        timestamp = parts.get("t")
        received_signature = parts.get("v1")

        if not timestamp or not received_signature:
            return {
                "verified": False,
                "configured": True,
                "reason": "invalid_stripe_signature_format",
            }

        signed_payload = f"{timestamp}.".encode("utf-8") + raw_body
        expected_signature = hmac.new(
            webhook_secret.encode("utf-8"),
            signed_payload,
            hashlib.sha256,
        ).hexdigest()

        verified = hmac.compare_digest(expected_signature, received_signature)

        return {
            "verified": verified,
            "configured": True,
            "reason": "signature_verified" if verified else "signature_mismatch",
        }

    except Exception as exc:
        return {
            "verified": False,
            "configured": True,
            "reason": f"signature_verification_error:{type(exc).__name__}",
        }


def normalise_stripe_event(payload: Dict[str, Any]) -> Dict[str, Any]:
    event_type = payload.get("type", "unknown")
    data = payload.get("data", {})
    data_object = data.get("object", {}) if isinstance(data, dict) else {}

    return {
        "event_type": event_type,
        "stripe_customer_id": data_object.get("customer"),
        "stripe_subscription_id": data_object.get("subscription") or data_object.get("id"),
        "billing_reason": data_object.get("billing_reason"),
        "status": data_object.get("status"),
        "current_period_start": data_object.get("current_period_start"),
        "current_period_end": data_object.get("current_period_end"),
        "cancel_at_period_end": data_object.get("cancel_at_period_end"),
        "received_at": utc_now_iso(),
    }


def classify_subscription_event(event_type: str) -> Dict[str, Any]:
    if event_type == "invoice.payment_succeeded":
        return {
            "action": "mark_subscription_active_and_reset_monthly_credits",
            "preserve_cycle_anchor": True,
            "client_execution_allowed": True,
        }

    if event_type == "invoice.payment_failed":
        return {
            "action": "mark_subscription_past_due_and_block_client_credit_consuming_execution",
            "retry_interval_hours": RETRY_POLICY_HOURS,
            "preserve_cycle_anchor": True,
            "client_execution_allowed": False,
        }

    if event_type == "customer.subscription.deleted":
        return {
            "action": "mark_subscription_cancelled_and_block_client_execution",
            "client_execution_allowed": False,
        }

    if event_type == "customer.subscription.updated":
        return {
            "action": "sync_subscription_status_cancel_policy_and_cycle_dates",
            "preserve_cycle_anchor": True,
        }

    return {
        "action": "record_event_no_runtime_mutation",
    }
