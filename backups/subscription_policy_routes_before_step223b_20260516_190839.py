from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional

from fastapi import APIRouter, Header, HTTPException, Request
from pydantic import BaseModel

from backend.app.core.durable_billing_state_store import get_billing_runtime_state

from backend.app.core.stripe_tenant_mapping_store import (
    list_stripe_tenant_mappings,
    upsert_stripe_tenant_mapping,
)

from backend.app.core.stripe_billing_runtime_bridge import (
    apply_stripe_classification_to_billing_runtime,
    latest_billing_bridge_events,
)

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


class StripeTenantMappingRequest(BaseModel):
    tenant_id: str
    stripe_customer_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None
    company_name: Optional[str] = None
    subscription_status: Optional[str] = None
    package_name: Optional[str] = None


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

    billing_runtime_update = apply_stripe_classification_to_billing_runtime(event, classification)

    return {
        "success": True,
        "route": "/webhooks/stripe/hardened",
        "signature": signature_result,
        "event": event,
        "classification": classification,
        "billing_runtime_update": billing_runtime_update,
        "policy": {
            "month_to_month": True,
            "lock_in_contract": False,
            "retry_interval_hours": 48,
            "preserve_original_billing_cycle_on_late_payment": True,
        },
        "processed_at": utc_now_iso(),
    }



@router.get("/admin/billing/webhook-runtime-bridge-events")
def webhook_runtime_bridge_events(
    x_actor_role: Optional[str] = Header(default=None),
    limit: int = 20,
) -> Dict[str, Any]:
    require_owner(x_actor_role)
    return latest_billing_bridge_events(limit=limit)



@router.post("/admin/billing/stripe-tenant-mapping")
def create_or_update_stripe_tenant_mapping(
    payload: StripeTenantMappingRequest,
    x_actor_role: Optional[str] = Header(default=None),
) -> Dict[str, Any]:
    require_owner(x_actor_role)
    return upsert_stripe_tenant_mapping(
        tenant_id=payload.tenant_id,
        stripe_customer_id=payload.stripe_customer_id,
        stripe_subscription_id=payload.stripe_subscription_id,
        company_name=payload.company_name,
        subscription_status=payload.subscription_status,
        package_name=payload.package_name,
    )


@router.get("/admin/billing/stripe-tenant-mappings")
def get_stripe_tenant_mappings(
    x_actor_role: Optional[str] = Header(default=None),
    limit: int = 50,
) -> Dict[str, Any]:
    require_owner(x_actor_role)
    return list_stripe_tenant_mappings(limit=limit)



@router.get("/admin/billing/durable-runtime-state")
def admin_billing_durable_runtime_state(
    x_actor_role: Optional[str] = Header(default=None),
    tenant_id: Optional[str] = None,
    limit: int = 50,
) -> Dict[str, Any]:
    require_owner(x_actor_role)
    return get_billing_runtime_state(tenant_id=tenant_id, limit=limit)
