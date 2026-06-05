from pathlib import Path

ROOT = Path.cwd()

runtime = ROOT / "backend/app/core/governed_refund_runtime.py"
runtime.write_text(r'''from __future__ import annotations

import json
import os
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

DATA_DIR = Path(os.getenv("REFUND_LEDGER_DIR", "data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)
REFUND_LEDGER = DATA_DIR / "governed_refund_ledger.json"


def _load() -> Dict[str, Any]:
    if not REFUND_LEDGER.exists():
        return {"refunds": []}
    try:
        return json.loads(REFUND_LEDGER.read_text(encoding="utf-8"))
    except Exception:
        return {"refunds": []}


def _save(data: Dict[str, Any]) -> None:
    REFUND_LEDGER.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def _now() -> int:
    return int(time.time())


def _used_evidence(payload: Dict[str, Any]) -> Dict[str, Any]:
    evidence = payload.get("usage_evidence") or {}
    flags = {
        "account_activated": bool(payload.get("account_activated") or evidence.get("account_activated")),
        "agent_executed": bool(payload.get("agent_executed") or evidence.get("agent_executed")),
        "workflow_executed": bool(payload.get("workflow_executed") or evidence.get("workflow_executed")),
        "credits_consumed": int(payload.get("credits_consumed") or evidence.get("credits_consumed") or 0) > 0,
        "deliverables_generated": int(payload.get("deliverables_generated") or evidence.get("deliverables_generated") or 0) > 0,
        "assets_generated": int(payload.get("assets_generated") or evidence.get("assets_generated") or 0) > 0,
        "integration_execution_used": bool(payload.get("integration_execution_used") or evidence.get("integration_execution_used")),
        "provider_execution_used": bool(payload.get("provider_execution_used") or evidence.get("provider_execution_used")),
    }
    return {
        "flags": flags,
        "platform_used": any(flags.values()),
        "policy": "refund_ineligible_if_account_activated_or_platform_used",
    }


def submit_refund_request(payload: Dict[str, Any]) -> Dict[str, Any]:
    usage = _used_evidence(payload)
    refund_id = f"refund_{uuid.uuid4().hex[:16]}"
    status = "refund_ineligible_platform_used" if usage["platform_used"] else "pending_owner_review"

    item = {
        "refund_id": refund_id,
        "tenant_id": payload.get("tenant_id") or payload.get("account_reference") or "unknown_tenant",
        "customer_email": payload.get("customer_email") or "",
        "stripe_customer_id": payload.get("stripe_customer_id"),
        "stripe_subscription_id": payload.get("stripe_subscription_id"),
        "payment_intent": payload.get("payment_intent"),
        "charge_id": payload.get("charge_id"),
        "requested_amount_cents": int(payload.get("requested_amount_cents") or 0),
        "currency": payload.get("currency") or "usd",
        "reason": payload.get("reason") or "not_provided",
        "details": payload.get("details") or "",
        "status": status,
        "usage_verification": usage,
        "owner_approval_required": True,
        "stripe_refund_executed": False,
        "stripe_refund_id": None,
        "created_at": _now(),
        "updated_at": _now(),
        "audit_events": [
            {
                "event": "refund_request_submitted",
                "status": status,
                "timestamp": _now(),
                "policy_applied": usage["policy"],
            }
        ],
    }

    data = _load()
    data.setdefault("refunds", []).insert(0, item)
    _save(data)

    return {
        "success": True,
        "refund_id": refund_id,
        "status": status,
        "eligible_for_owner_review": status == "pending_owner_review",
        "refund_ineligible_reason": "platform_used_or_activated" if usage["platform_used"] else None,
        "usage_verification": usage,
    }


def list_refund_requests(status: Optional[str] = None, limit: int = 50) -> Dict[str, Any]:
    data = _load()
    refunds = data.get("refunds", [])
    if status:
        refunds = [r for r in refunds if r.get("status") == status]
    return {"success": True, "count": len(refunds[:limit]), "refunds": refunds[:limit]}


def get_refund_request(refund_id: str) -> Dict[str, Any]:
    for item in _load().get("refunds", []):
        if item.get("refund_id") == refund_id:
            return {"success": True, "refund": item}
    return {"success": False, "error": "refund_request_not_found"}


def decide_refund_request(payload: Dict[str, Any]) -> Dict[str, Any]:
    refund_id = payload.get("refund_id")
    decision = payload.get("decision")
    actor = payload.get("approved_by") or payload.get("actor") or "owner_admin"
    note = payload.get("note") or ""

    data = _load()
    for item in data.get("refunds", []):
        if item.get("refund_id") != refund_id:
            continue

        if item.get("usage_verification", {}).get("platform_used") and decision == "approve":
            item["status"] = "refund_rejected_platform_used"
            item["updated_at"] = _now()
            item["audit_events"].append({
                "event": "refund_approval_blocked_platform_used",
                "actor": actor,
                "note": note,
                "timestamp": _now(),
            })
            _save(data)
            return {"success": False, "status": item["status"], "error": "refund_ineligible_platform_used"}

        if decision == "reject":
            item["status"] = "refund_rejected"
            item["updated_at"] = _now()
            item["audit_events"].append({"event": "refund_rejected", "actor": actor, "note": note, "timestamp": _now()})
            _save(data)
            return {"success": True, "status": item["status"], "refund_id": refund_id}

        if decision != "approve":
            return {"success": False, "error": "invalid_refund_decision"}

        item["status"] = "owner_approved_pending_stripe_refund"
        item["approved_by"] = actor
        item["approved_at"] = _now()
        item["updated_at"] = _now()
        item["audit_events"].append({"event": "refund_owner_approved", "actor": actor, "note": note, "timestamp": _now()})
        _save(data)
        return {"success": True, "status": item["status"], "refund_id": refund_id}

    return {"success": False, "error": "refund_request_not_found"}


def execute_stripe_refund(payload: Dict[str, Any]) -> Dict[str, Any]:
    refund_id = payload.get("refund_id")
    actor = payload.get("actor") or "owner_admin"
    data = _load()

    for item in data.get("refunds", []):
        if item.get("refund_id") != refund_id:
            continue

        if item.get("status") != "owner_approved_pending_stripe_refund":
            return {"success": False, "error": "refund_not_owner_approved", "status": item.get("status")}

        if item.get("usage_verification", {}).get("platform_used"):
            return {"success": False, "error": "refund_ineligible_platform_used"}

        stripe_key = os.getenv("STRIPE_SECRET_KEY", "").strip()
        live_mode = bool(stripe_key and stripe_key.startswith("sk_"))
        amount = int(payload.get("amount_cents") or item.get("requested_amount_cents") or 0)

        if amount <= 0:
            return {"success": False, "error": "valid_refund_amount_required"}

        try:
            if live_mode:
                import stripe
                stripe.api_key = stripe_key
                kwargs: Dict[str, Any] = {"amount": amount}
                if item.get("payment_intent"):
                    kwargs["payment_intent"] = item["payment_intent"]
                elif item.get("charge_id"):
                    kwargs["charge"] = item["charge_id"]
                else:
                    return {"success": False, "error": "payment_intent_or_charge_required_for_live_refund"}
                refund = stripe.Refund.create(**kwargs)
                stripe_refund_id = getattr(refund, "id", None) or dict(refund).get("id")
                mode = "live_stripe_refund_executed"
            else:
                stripe_refund_id = f"simulated_refund_{uuid.uuid4().hex[:12]}"
                mode = "simulated_refund_no_live_stripe_key"

            item["status"] = "refund_completed"
            item["stripe_refund_executed"] = live_mode
            item["stripe_refund_id"] = stripe_refund_id
            item["refunded_amount_cents"] = amount
            item["updated_at"] = _now()
            item["audit_events"].append({
                "event": "stripe_refund_execution",
                "actor": actor,
                "mode": mode,
                "stripe_refund_id": stripe_refund_id,
                "amount_cents": amount,
                "timestamp": _now(),
            })
            _save(data)

            return {
                "success": True,
                "status": item["status"],
                "refund_id": refund_id,
                "stripe_refund_id": stripe_refund_id,
                "live_stripe_refund_executed": live_mode,
                "mode": mode,
            }
        except Exception as exc:
            item["status"] = "refund_execution_failed"
            item["updated_at"] = _now()
            item["audit_events"].append({
                "event": "stripe_refund_execution_failed",
                "actor": actor,
                "error": str(exc),
                "timestamp": _now(),
            })
            _save(data)
            return {"success": False, "status": item["status"], "error": str(exc)}

    return {"success": False, "error": "refund_request_not_found"}
''', encoding="utf-8")

routes = ROOT / "backend/app/api/refund_routes.py"
routes.write_text(r'''from fastapi import APIRouter, Header, HTTPException, Query
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
''', encoding="utf-8")

main = ROOT / "backend/app/main.py"
text = main.read_text(encoding="utf-8")
if "refund_routes" not in text:
    text += '''

# Governed refund workflow routes
try:
    from backend.app.api.refund_routes import router as refund_router
    app.include_router(refund_router)
except Exception as exc:
    print(f"GOVERNED_REFUND_ROUTES_NOT_LOADED: {exc}")
'''
    main.write_text(text, encoding="utf-8")
    print("PATCHED backend/app/main.py")
else:
    print("NO_CHANGE backend/app/main.py")

print("GOVERNED_REFUND_WORKFLOW_INSTALLED")