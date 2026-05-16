from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, Header

from backend.app.core.stripe_customer_billing_portal import (
    billing_portal_readiness,
    create_customer_billing_portal_session,
    customer_billing_visibility,
)

router = APIRouter()


def _is_owner_admin(role: Optional[str]) -> bool:
    return role in {"owner", "admin", "system"}


@router.get("/customer/billing/visibility")
async def customer_billing_visibility_route(
    tenant_id: str,
    x_tenant_id: Optional[str] = Header(default=None),
    x_actor_role: Optional[str] = Header(default=None),
) -> Dict[str, Any]:
    if not _is_owner_admin(x_actor_role) and x_tenant_id != tenant_id:
        return {
            "success": False,
            "error": "tenant_access_denied",
        }

    return customer_billing_visibility(tenant_id)


@router.get("/admin/billing/customer-portal-readiness")
async def admin_billing_portal_readiness(
    tenant_id: str,
    x_actor_role: Optional[str] = Header(default=None),
) -> Dict[str, Any]:
    if not _is_owner_admin(x_actor_role):
        return {
            "success": False,
            "error": "owner_admin_required",
        }

    return billing_portal_readiness(tenant_id)


@router.post("/admin/billing/create-customer-portal-session")
async def admin_create_customer_billing_portal_session(
    payload: Dict[str, Any],
    x_actor_role: Optional[str] = Header(default=None),
) -> Dict[str, Any]:
    if not _is_owner_admin(x_actor_role):
        return {
            "success": False,
            "error": "owner_admin_required",
        }

    tenant_id = str(payload.get("tenant_id") or "").strip()
    if not tenant_id:
        return {
            "success": False,
            "error": "tenant_id_required",
        }

    return create_customer_billing_portal_session(tenant_id)
