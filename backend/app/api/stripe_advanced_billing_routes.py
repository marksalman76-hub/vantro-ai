from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, Header

from backend.app.core.canonical_billing_state_runtime import owner_admin_bypasses_client_billing
from backend.app.core.stripe_advanced_billing_runtime import (
    advanced_billing_readiness,
    create_advanced_subscription_checkout,
    create_topup_credit_checkout,
    prepare_plan_change,
)

router = APIRouter()


def _owner_admin(role: Optional[str]) -> bool:
    return owner_admin_bypasses_client_billing(role)


@router.get("/admin/billing/advanced-readiness")
async def advanced_billing_readiness_route(
    x_actor_role: Optional[str] = Header(default=None),
) -> Dict[str, Any]:
    if not _owner_admin(x_actor_role):
        return {"success": False, "error": "owner_admin_required"}

    return advanced_billing_readiness()


@router.post("/admin/billing/create-advanced-checkout-session")
async def create_advanced_checkout_session_route(
    payload: Dict[str, Any],
    x_actor_role: Optional[str] = Header(default=None),
) -> Dict[str, Any]:
    if not _owner_admin(x_actor_role):
        return {"success": False, "error": "owner_admin_required"}

    return create_advanced_subscription_checkout(payload)


@router.post("/admin/billing/create-topup-checkout-session")
async def create_topup_checkout_session_route(
    payload: Dict[str, Any],
    x_actor_role: Optional[str] = Header(default=None),
) -> Dict[str, Any]:
    if not _owner_admin(x_actor_role):
        return {"success": False, "error": "owner_admin_required"}

    return create_topup_credit_checkout(payload)


@router.post("/admin/billing/prepare-plan-change")
async def prepare_plan_change_route(
    payload: Dict[str, Any],
    x_actor_role: Optional[str] = Header(default=None),
) -> Dict[str, Any]:
    if not _owner_admin(x_actor_role):
        return {"success": False, "error": "owner_admin_required"}

    return prepare_plan_change(payload)
