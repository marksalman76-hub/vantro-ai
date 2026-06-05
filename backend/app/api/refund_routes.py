from fastapi import APIRouter, Header, HTTPException, Query
from backend.app.core.governed_refund_runtime import (
    submit_refund_request,
    list_refund_requests,
    get_refund_request,
    decide_refund_request,
    execute_stripe_refund,
)

router = APIRouter()


def _is_admin(role: str | None) -> bool:
    return (role or "").lower() in {"owner", "admin", "owner_admin", "system"}


@router.post("/billing/refund-request")
def billing_refund_request(payload: dict):
    return submit_refund_request(payload)


@router.get("/billing/refund-request/{refund_id}")
def billing_refund_request_status(refund_id: str):
    return get_refund_request(refund_id)


@router.get("/admin/billing/refund-requests")
def admin_billing_refund_requests(
    status: str | None = Query(default=None),
    limit: int = Query(default=50),
    x_actor_role: str | None = Header(default=None),
):
    if not _is_admin(x_actor_role):
        raise HTTPException(status_code=403, detail="admin_required")
    return list_refund_requests(status=status, limit=limit)


@router.post("/admin/billing/refund-decision")
def admin_billing_refund_decision(payload: dict, x_actor_role: str | None = Header(default=None)):
    if not _is_admin(x_actor_role):
        raise HTTPException(status_code=403, detail="admin_required")
    return decide_refund_request(payload)


@router.post("/admin/billing/refund-execute")
def admin_billing_refund_execute(payload: dict, x_actor_role: str | None = Header(default=None)):
    if not _is_admin(x_actor_role):
        raise HTTPException(status_code=403, detail="admin_required")
    return execute_stripe_refund(payload)
