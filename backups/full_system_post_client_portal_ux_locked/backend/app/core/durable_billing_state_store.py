from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, Optional


DATA_DIR = Path(__file__).resolve().parents[1] / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

BILLING_STATE_FILE = DATA_DIR / "durable_billing_state.json"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load() -> Dict[str, Any]:
    if not BILLING_STATE_FILE.exists():
        return {
            "version": "step204_durable_billing_state_v1",
            "tenants": {},
            "events": [],
            "updated_at": utc_now_iso(),
        }

    try:
        return json.loads(BILLING_STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {
            "version": "step204_durable_billing_state_v1",
            "tenants": {},
            "events": [],
            "updated_at": utc_now_iso(),
            "recovered_from_invalid_json": True,
        }


def _save(data: Dict[str, Any]) -> None:
    data["updated_at"] = utc_now_iso()
    BILLING_STATE_FILE.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def apply_billing_runtime_mutation(
    tenant_id: str,
    stripe_customer_id: Optional[str],
    stripe_subscription_id: Optional[str],
    event_type: str,
    target_subscription_status: str,
    target_client_execution_allowed: Any,
    target_credit_action: str,
    preserve_cycle_anchor: bool = True,
    retry_interval_hours: Optional[int] = None,
    cancel_at_period_end: Optional[bool] = None,
) -> Dict[str, Any]:
    if not tenant_id:
        return {
            "success": False,
            "mutation_committed": False,
            "reason": "tenant_id_required",
        }

    data = _load()
    tenants = data.setdefault("tenants", {})
    events = data.setdefault("events", [])

    tenant_state = tenants.setdefault(tenant_id, {
        "tenant_id": tenant_id,
        "created_at": utc_now_iso(),
        "client_execution_allowed": True,
        "subscription_status": "unknown",
        "credit_state": "unknown",
    })

    previous_state = dict(tenant_state)

    tenant_state["tenant_id"] = tenant_id
    tenant_state["stripe_customer_id"] = stripe_customer_id
    tenant_state["stripe_subscription_id"] = stripe_subscription_id
    tenant_state["subscription_status"] = target_subscription_status
    tenant_state["last_event_type"] = event_type
    tenant_state["last_webhook_processed_at"] = utc_now_iso()
    tenant_state["preserve_cycle_anchor"] = preserve_cycle_anchor

    if isinstance(target_client_execution_allowed, bool):
        tenant_state["client_execution_allowed"] = target_client_execution_allowed

    tenant_state["credit_action"] = target_credit_action

    if target_credit_action == "reset_monthly_credits":
        tenant_state["credit_state"] = "monthly_credits_reset_required"
        tenant_state["execution_block_reason"] = None

    elif target_credit_action in {"block_credit_consuming_execution", "block_client_execution"}:
        tenant_state["credit_state"] = "blocked"
        tenant_state["execution_block_reason"] = target_subscription_status

    elif target_credit_action == "sync_only":
        tenant_state["credit_state"] = "sync_only"

    if retry_interval_hours is not None:
        tenant_state["retry_interval_hours"] = retry_interval_hours

    if cancel_at_period_end is not None:
        tenant_state["cancel_at_period_end"] = cancel_at_period_end

    tenant_state["updated_at"] = utc_now_iso()

    event_record = {
        "tenant_id": tenant_id,
        "event_type": event_type,
        "stripe_customer_id": stripe_customer_id,
        "stripe_subscription_id": stripe_subscription_id,
        "target_subscription_status": target_subscription_status,
        "target_client_execution_allowed": target_client_execution_allowed,
        "target_credit_action": target_credit_action,
        "processed_at": utc_now_iso(),
    }

    events.append(event_record)
    data["events"] = events[-200:]

    _save(data)

    return {
        "success": True,
        "mutation_committed": True,
        "tenant_id": tenant_id,
        "previous_state": previous_state,
        "updated_state": tenant_state,
        "event_record": event_record,
        "billing_state_file": str(BILLING_STATE_FILE),
    }


def get_billing_runtime_state(tenant_id: Optional[str] = None, limit: int = 50) -> Dict[str, Any]:
    data = _load()

    if tenant_id:
        return {
            "success": True,
            "tenant_id": tenant_id,
            "state": data.get("tenants", {}).get(tenant_id),
            "checked_at": utc_now_iso(),
        }

    return {
        "success": True,
        "tenant_count": len(data.get("tenants", {})),
        "tenants": data.get("tenants", {}),
        "event_count": len(data.get("events", [])[-limit:]),
        "events": data.get("events", [])[-limit:],
        "billing_state_file": str(BILLING_STATE_FILE),
        "checked_at": utc_now_iso(),
    }
