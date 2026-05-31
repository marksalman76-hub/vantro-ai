from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
BACKEND = ROOT / "backend" / "app"
CORE = BACKEND / "core"
API = BACKEND / "api"
BACKUPS = ROOT / "backups"

CORE.mkdir(parents=True, exist_ok=True)
API.mkdir(parents=True, exist_ok=True)
BACKUPS.mkdir(exist_ok=True)

(CORE / "__init__.py").touch()
(API / "__init__.py").touch()

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

routes_file = API / "subscription_policy_routes.py"
webhook_file = CORE / "stripe_webhook_hardening.py"
main_file = BACKEND / "main.py"

if not main_file.exists():
    raise FileNotFoundError("backend/app/main.py not found")

for file in [main_file, routes_file, webhook_file]:
    if file.exists():
        backup = BACKUPS / f"{file.stem}_before_step201_{timestamp}{file.suffix}"
        backup.write_text(file.read_text(encoding="utf-8"), encoding="utf-8")

webhook_file.write_text(r'''
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
'''.lstrip(), encoding="utf-8")

routes_file.write_text(r'''
from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional

from fastapi import APIRouter, Header, HTTPException, Request
from pydantic import BaseModel

from backend.app.core.stripe_webhook_hardening import (
    SUBSCRIPTION_POLICY,
    classify_subscription_event,
    normalise_stripe_event,
    verify_stripe_signature,
    utc_now_iso,
)

router = APIRouter()


class CancellationRequest(BaseModel):
    tenant_id: str
    subscription_id: Optional[str] = None
    cancel_at_period_end: bool = True
    reason: Optional[str] = None


class ReactivationRequest(BaseModel):
    tenant_id: str
    subscription_id: Optional[str] = None
    reason: Optional[str] = None


def require_owner(actor_role: Optional[str]) -> None:
    if actor_role not in {"owner", "admin", "system"}:
        raise HTTPException(status_code=403, detail="owner_or_admin_required")


@router.get("/admin/billing/subscription-policy-summary")
def subscription_policy_summary(
    x_actor_role: Optional[str] = Header(default=None),
) -> Dict[str, Any]:
    require_owner(x_actor_role)
    return {
        "success": True,
        "route": "/admin/billing/subscription-policy-summary",
        "policy": SUBSCRIPTION_POLICY,
        "checked_at": utc_now_iso(),
    }


@router.post("/admin/billing/cancel-subscription")
def cancel_subscription(
    payload: CancellationRequest,
    x_actor_role: Optional[str] = Header(default=None),
) -> Dict[str, Any]:
    require_owner(x_actor_role)
    return {
        "success": True,
        "route": "/admin/billing/cancel-subscription",
        "tenant_id": payload.tenant_id,
        "subscription_id": payload.subscription_id,
        "requested_action": "cancel_at_period_end" if payload.cancel_at_period_end else "cancel_immediately",
        "month_to_month": True,
        "lock_in_contract": False,
        "client_execution_after_period_end": "blocked_unless_reactivated_or_new_subscription_active",
        "owner_admin_access": "unaffected",
        "reason": payload.reason,
        "recorded_at": utc_now_iso(),
    }


@router.post("/admin/billing/reactivate-subscription")
def reactivate_subscription(
    payload: ReactivationRequest,
    x_actor_role: Optional[str] = Header(default=None),
) -> Dict[str, Any]:
    require_owner(x_actor_role)
    return {
        "success": True,
        "route": "/admin/billing/reactivate-subscription",
        "tenant_id": payload.tenant_id,
        "subscription_id": payload.subscription_id,
        "requested_action": "reactivate_subscription",
        "billing_cycle_rule": "preserve_original_cycle_anchor_where_available",
        "client_execution": "allowed_after_active_subscription_and_credit_state_verified",
        "owner_admin_access": "unaffected",
        "reason": payload.reason,
        "recorded_at": utc_now_iso(),
    }


@router.post("/webhooks/stripe/hardened")
async def hardened_stripe_webhook(
    request: Request,
    stripe_signature: Optional[str] = Header(default=None, alias="stripe-signature"),
) -> Dict[str, Any]:
    raw_body = await request.body()
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

    signature_result = verify_stripe_signature(raw_body, stripe_signature, webhook_secret)

    try:
        payload = json.loads(raw_body.decode("utf-8") or "{}")
    except Exception:
        raise HTTPException(status_code=400, detail="invalid_json_payload")

    event = normalise_stripe_event(payload)
    classification = classify_subscription_event(event["event_type"])

    production_mode = os.getenv("APP_ENV", "").lower() in {"production", "prod"}

    if production_mode and not signature_result.get("verified"):
        raise HTTPException(
            status_code=400,
            detail=signature_result.get("reason", "stripe_signature_not_verified"),
        )

    return {
        "success": True,
        "route": "/webhooks/stripe/hardened",
        "signature": signature_result,
        "event": event,
        "classification": classification,
        "policy": {
            "month_to_month": True,
            "lock_in_contract": False,
            "retry_interval_hours": 48,
            "preserve_original_billing_cycle_on_late_payment": True,
        },
        "processed_at": utc_now_iso(),
    }
'''.lstrip(), encoding="utf-8")

main_text = main_file.read_text(encoding="utf-8")

import_line = "from backend.app.api.subscription_policy_routes import router as subscription_policy_router"

if import_line not in main_text:
    main_text = import_line + "\n" + main_text

if "app.include_router(subscription_policy_router)" not in main_text:
    main_text += "\n\n# Step 201 subscription policy and Stripe webhook hardening\napp.include_router(subscription_policy_router)\n"

main_file.write_text(main_text, encoding="utf-8")

print("STEP_201_SUBSCRIPTION_POLICY_WEBHOOK_HARDENING_INSTALLED")
print(f"Created/updated: {routes_file}")
print(f"Created/updated: {webhook_file}")
print("STEP_201_OK")