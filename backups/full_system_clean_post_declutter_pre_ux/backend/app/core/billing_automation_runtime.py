from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from backend.app.core.marketplace_commercial_bridge import apply_entitlement_change_after_billing, PACKAGE_PRICING


DATA_DIR = Path.cwd() / "runtime_data"
BILLING_STATE_FILE = DATA_DIR / "billing_subscription_state.jsonl"
BILLING_EVENTS_FILE = DATA_DIR / "billing_automation_events.jsonl"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _append_jsonl(path: Path, record: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def _read_jsonl(path: Path, limit: int = 5000) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    records = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            try:
                records.append(json.loads(line))
            except Exception:
                continue
    return records[-limit:]


def _rewrite_jsonl(path: Path, records: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def _normalise_package(package: str) -> str:
    package = str(package or "starter").strip().lower()
    return package if package in PACKAGE_PRICING else "starter"


def _latest_state(tenant_id: str) -> Dict[str, Any] | None:
    states = _read_jsonl(BILLING_STATE_FILE, limit=10000)
    for state in reversed(states):
        if state.get("tenant_id") == tenant_id:
            return state
    return None


def upsert_billing_state(payload: Dict[str, Any]) -> Dict[str, Any]:
    tenant_id = str(payload.get("tenant_id") or "").strip()
    if not tenant_id:
        return {"success": False, "error": "tenant_id_required"}

    package = _normalise_package(payload.get("package") or payload.get("target_package"))
    status = str(payload.get("subscription_status") or payload.get("billing_status") or "active").lower()

    state = {
        "tenant_id": tenant_id,
        "client_number": payload.get("client_number"),
        "customer_email": payload.get("customer_email"),
        "package": package,
        "subscription_status": status,
        "billing_status": status,
        "stripe_customer_id": payload.get("stripe_customer_id"),
        "stripe_subscription_id": payload.get("stripe_subscription_id"),
        "stripe_checkout_session_id": payload.get("stripe_checkout_session_id"),
        "billing_cycle_anchor_rule": "preserve_original_cycle_date",
        "failed_payment_retry_policy": "48_hour_retry_policy",
        "cancel_at_period_end": bool(payload.get("cancel_at_period_end", False)),
        "month_to_month": True,
        "no_lock_in_contract": True,
        "updated_at": _now(),
        "state_profile": "priority10_billing_state_v1",
        "secret_exposure": False,
    }

    states = [s for s in _read_jsonl(BILLING_STATE_FILE, limit=10000) if s.get("tenant_id") != tenant_id]
    states.append(state)
    _rewrite_jsonl(BILLING_STATE_FILE, states)

    _append_jsonl(BILLING_EVENTS_FILE, {
        "timestamp": _now(),
        "event_type": "billing_state_upserted",
        "tenant_id": tenant_id,
        "package": package,
        "subscription_status": status,
    })

    return {"success": True, "state": state}


def create_checkout_session_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    tenant_id = payload.get("tenant_id")
    client_number = payload.get("client_number")
    target_package = _normalise_package(payload.get("target_package") or payload.get("package"))
    customer_email = payload.get("customer_email")
    selected_agents = list(dict.fromkeys(payload.get("selected_agents") or payload.get("purchased_agents") or []))

    pricing = PACKAGE_PRICING[target_package]
    checkout_required = target_package != "enterprise"

    session_reference = f"checkout_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}"

    event = {
        "timestamp": _now(),
        "event_type": "checkout_session_payload_created",
        "session_reference": session_reference,
        "tenant_id": tenant_id,
        "client_number": client_number,
        "target_package": target_package,
        "checkout_required": checkout_required,
    }
    _append_jsonl(BILLING_EVENTS_FILE, event)

    return {
        "success": True,
        "checkout_profile": "priority10_checkout_session_payload_v1",
        "session_reference": session_reference,
        "tenant_id": tenant_id,
        "client_number": client_number,
        "customer_email": customer_email,
        "target_package": target_package,
        "selected_agents": selected_agents,
        "currency": "USD",
        "monthly_amount_usd": pricing["monthly_usd"],
        "checkout_required": checkout_required,
        "stripe_mode": "subscription",
        "stripe_ready": checkout_required,
        "enterprise_owner_review_required": target_package == "enterprise",
        "metadata": {
            "tenant_id": tenant_id,
            "client_number": client_number,
            "target_package": target_package,
            "selected_agents": ",".join(selected_agents),
        },
        "success_url_path": "/client/billing/success",
        "cancel_url_path": "/client/billing/cancelled",
        "secret_exposure": False,
        "customer_safe_response_mode": True,
    }


def handle_checkout_completed(payload: Dict[str, Any]) -> Dict[str, Any]:
    tenant_id = payload.get("tenant_id")
    target_package = _normalise_package(payload.get("target_package") or payload.get("package"))
    purchased_agents = list(dict.fromkeys(payload.get("purchased_agents") or []))
    active_agents = list(dict.fromkeys(payload.get("active_agents") or []))

    billing_state = upsert_billing_state({
        **payload,
        "package": target_package,
        "subscription_status": "active",
        "billing_status": "paid",
    })

    entitlement = apply_entitlement_change_after_billing({
        "tenant_id": tenant_id,
        "client_number": payload.get("client_number"),
        "target_package": target_package,
        "purchased_agents": purchased_agents,
        "active_agents": active_agents,
        "billing_status": "paid",
    })

    _append_jsonl(BILLING_EVENTS_FILE, {
        "timestamp": _now(),
        "event_type": "checkout_completed_entitlement_synced",
        "tenant_id": tenant_id,
        "target_package": target_package,
        "entitlement_success": entitlement.get("success"),
    })

    return {
        "success": True,
        "status": "checkout_completed",
        "billing_state": billing_state.get("state"),
        "entitlement_sync": entitlement,
        "secret_exposure": False,
    }


def handle_invoice_payment_succeeded_runtime(payload: Dict[str, Any]) -> Dict[str, Any]:
    tenant_id = payload.get("tenant_id")
    package = _normalise_package(payload.get("package") or payload.get("target_package"))

    state = upsert_billing_state({
        **payload,
        "package": package,
        "subscription_status": "active",
        "billing_status": "paid",
        "cancel_at_period_end": False,
    })

    _append_jsonl(BILLING_EVENTS_FILE, {
        "timestamp": _now(),
        "event_type": "invoice_payment_succeeded",
        "tenant_id": tenant_id,
        "package": package,
        "credits_reset": True,
    })

    return {
        "success": True,
        "status": "invoice_payment_succeeded",
        "billing_state": state.get("state"),
        "credits_reset": True,
        "client_access_suspended": False,
        "secret_exposure": False,
    }


def handle_invoice_payment_failed_runtime(payload: Dict[str, Any]) -> Dict[str, Any]:
    tenant_id = payload.get("tenant_id")
    package = _normalise_package(payload.get("package") or payload.get("target_package"))

    state = upsert_billing_state({
        **payload,
        "package": package,
        "subscription_status": "past_due",
        "billing_status": "failed",
    })

    _append_jsonl(BILLING_EVENTS_FILE, {
        "timestamp": _now(),
        "event_type": "invoice_payment_failed",
        "tenant_id": tenant_id,
        "package": package,
        "retry_policy": "48_hour_retry_policy",
    })

    return {
        "success": True,
        "status": "invoice_payment_failed",
        "billing_state": state.get("state"),
        "subscription_status": "past_due",
        "client_access_suspended": True,
        "retry_policy": "48_hour_retry_policy",
        "billing_cycle_anchor_rule": "preserve_original_cycle_date",
        "secret_exposure": False,
    }


def cancel_subscription_runtime(payload: Dict[str, Any]) -> Dict[str, Any]:
    tenant_id = payload.get("tenant_id")
    package = _normalise_package(payload.get("package") or payload.get("target_package"))

    state = upsert_billing_state({
        **payload,
        "package": package,
        "subscription_status": "cancelled",
        "billing_status": "cancelled",
        "cancel_at_period_end": bool(payload.get("cancel_at_period_end", True)),
    })

    _append_jsonl(BILLING_EVENTS_FILE, {
        "timestamp": _now(),
        "event_type": "subscription_cancelled",
        "tenant_id": tenant_id,
        "package": package,
        "cancel_at_period_end": bool(payload.get("cancel_at_period_end", True)),
    })

    return {
        "success": True,
        "status": "subscription_cancelled",
        "billing_state": state.get("state"),
        "client_access_suspended": True,
        "secret_exposure": False,
    }


def reactivate_subscription_runtime(payload: Dict[str, Any]) -> Dict[str, Any]:
    tenant_id = payload.get("tenant_id")
    package = _normalise_package(payload.get("package") or payload.get("target_package"))

    state = upsert_billing_state({
        **payload,
        "package": package,
        "subscription_status": "active",
        "billing_status": "paid",
        "cancel_at_period_end": False,
    })

    _append_jsonl(BILLING_EVENTS_FILE, {
        "timestamp": _now(),
        "event_type": "subscription_reactivated",
        "tenant_id": tenant_id,
        "package": package,
        "billing_cycle_anchor_rule": "preserve_original_cycle_date",
    })

    return {
        "success": True,
        "status": "subscription_reactivated",
        "billing_state": state.get("state"),
        "client_access_suspended": False,
        "billing_cycle_anchor_rule": "preserve_original_cycle_date",
        "secret_exposure": False,
    }


def billing_automation_summary(payload: Dict[str, Any]) -> Dict[str, Any]:
    tenant_id = payload.get("tenant_id")
    events = _read_jsonl(BILLING_EVENTS_FILE, limit=5000)

    if tenant_id:
        events = [event for event in events if event.get("tenant_id") == tenant_id]

    counts: Dict[str, int] = {}
    for event in events:
        event_type = event.get("event_type") or "unknown"
        counts[event_type] = counts.get(event_type, 0) + 1

    latest_state = _latest_state(str(tenant_id)) if tenant_id else None

    return {
        "success": True,
        "summary_profile": "priority10_billing_automation_summary_v1",
        "tenant_id": tenant_id,
        "latest_state": latest_state,
        "event_count": len(events),
        "event_counts": counts,
        "recent_events": events[-25:],
        "secret_exposure": False,
        "customer_safe_response_mode": True,
    }
