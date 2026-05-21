from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Header
from pydantic import BaseModel

from backend.app.core.stripe_checkout_runtime import (
    create_subscription_checkout_session,
    get_stripe_checkout_readiness,
)


router = APIRouter()


class CheckoutSessionRequest(BaseModel):
    tenant_id: str
    package_name: str
    customer_email: str
    success_url: str
    cancel_url: str
    client_reference_id: str | None = None


@router.get("/admin/billing/stripe-checkout-readiness")
async def stripe_checkout_readiness(x_actor_role: str = Header(default="owner")) -> Dict[str, Any]:
    if x_actor_role not in {"owner", "admin", "system"}:
        return {
            "success": False,
            "error": "owner_admin_required",
        }

    return get_stripe_checkout_readiness()


@router.post("/admin/billing/create-checkout-session")
async def create_checkout_session(
    payload: CheckoutSessionRequest,
    x_actor_role: str = Header(default="owner"),
) -> Dict[str, Any]:
    if x_actor_role not in {"owner", "admin", "system"}:
        return {
            "success": False,
            "error": "owner_admin_required",
        }

    return create_subscription_checkout_session(payload.model_dump())
