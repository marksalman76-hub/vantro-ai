from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from backend.app.core.marketplace_entitlement_runtime import PACKAGE_LIMITS
from backend.app.core.marketplace_state_runtime import get_marketplace_state, upsert_marketplace_state, validate_package_downgrade
from backend.app.core.canonical_billing_state_runtime import evaluate_subscription_status


DATA_DIR = Path.cwd() / "runtime_data"
COMMERCIAL_EVENTS_FILE = DATA_DIR / "marketplace_commercial_events.jsonl"

PACKAGE_PRICING = {
    "starter": {
        "monthly_usd": 99,
        "agent_limit": 1,
        "positioning": "Starter automation package",
        "stripe_checkout_enabled": True,
    },
    "growth": {
        "monthly_usd": 279,
        "agent_limit": 3,
        "positioning": "Growth automation package",
        "stripe_checkout_enabled": True,
    },
    "business": {
        "monthly_usd": 399,
        "agent_limit": 5,
        "positioning": "Business automation package",
        "stripe_checkout_enabled": True,
    },
    "enterprise": {
        "monthly_usd": None,
        "agent_limit": 999,
        "positioning": "Custom enterprise automation package",
        "stripe_checkout_enabled": False,
        "contact_us_required": True,
        "unique_price_link_after_owner_discussion": True,
    },
}


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


def _normalise_package(package: str) -> str:
    package = str(package or "starter").strip().lower()
    return package if package in PACKAGE_PRICING else "starter"


def package_pricing_catalogue() -> Dict[str, Any]:
    return {
        "success": True,
        "pricing_profile": "priority9_package_pricing_catalogue_v1",
        "currency": "USD",
        "billing_interval": "monthly",
        "packages": PACKAGE_PRICING,
        "month_to_month": True,
        "no_lock_in_contract": True,
        "customer_safe_response_mode": True,
        "secret_exposure": False,
    }


def build_purchase_flow_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    tenant_id = payload.get("tenant_id")
    client_number = payload.get("client_number")
    current_package = _normalise_package(payload.get("current_package") or payload.get("package"))
    target_package = _normalise_package(payload.get("target_package"))
    selected_agents = list(dict.fromkeys(payload.get("selected_agents") or payload.get("purchased_agents") or []))

    current_price = PACKAGE_PRICING[current_package]["monthly_usd"]
    target_price = PACKAGE_PRICING[target_package]["monthly_usd"]

    if target_package == "enterprise":
        checkout_required = False
        owner_sales_required = True
        price_delta = None
    else:
        checkout_required = True
        owner_sales_required = False
        price_delta = (target_price or 0) - (current_price or 0)

    event = {
        "timestamp": _now(),
        "event_type": "marketplace_purchase_flow_created",
        "tenant_id": tenant_id,
        "client_number": client_number,
        "current_package": current_package,
        "target_package": target_package,
        "selected_agents": selected_agents,
        "checkout_required": checkout_required,
    }
    _append_jsonl(COMMERCIAL_EVENTS_FILE, event)

    return {
        "success": True,
        "purchase_flow_profile": "priority9_purchase_flow_payload_v1",
        "tenant_id": tenant_id,
        "client_number": client_number,
        "current_package": current_package,
        "target_package": target_package,
        "selected_agents": selected_agents,
        "current_monthly_usd": current_price,
        "target_monthly_usd": target_price,
        "monthly_delta_usd": price_delta,
        "checkout_required": checkout_required,
        "owner_sales_required": owner_sales_required,
        "stripe_checkout_ready": checkout_required,
        "enterprise_contact_required": owner_sales_required,
        "billing_required": checkout_required,
        "customer_safe_message": (
            "Continue to checkout to activate this upgrade."
            if checkout_required else
            "Enterprise package requires owner review and custom setup."
        ),
        "customer_safe_response_mode": True,
        "secret_exposure": False,
        "entitlement_bypass": False,
        "governance_bypass": False,
    }


def create_entitlement_change_request(payload: Dict[str, Any]) -> Dict[str, Any]:
    tenant_id = payload.get("tenant_id")
    client_number = payload.get("client_number")
    change_type = str(payload.get("change_type") or "upgrade").strip().lower()
    current_package = _normalise_package(payload.get("current_package") or payload.get("package"))
    target_package = _normalise_package(payload.get("target_package"))
    active_agents = list(dict.fromkeys(payload.get("active_agents") or []))
    purchased_agents = list(dict.fromkeys(payload.get("purchased_agents") or []))

    request_id = f"entchg_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}"

    downgrade_check = None
    if change_type == "downgrade":
        downgrade_check = validate_package_downgrade({
            "current_package": current_package,
            "target_package": target_package,
            "active_agents": active_agents,
        })
        if downgrade_check.get("blocked"):
            status = "blocked_requires_agent_deactivation"
        else:
            status = "ready_for_billing_sync"
    elif target_package == "enterprise":
        status = "owner_sales_review_required"
    else:
        status = "ready_for_checkout"

    event = {
        "timestamp": _now(),
        "event_type": "entitlement_change_requested",
        "request_id": request_id,
        "tenant_id": tenant_id,
        "client_number": client_number,
        "change_type": change_type,
        "current_package": current_package,
        "target_package": target_package,
        "active_agents": active_agents,
        "purchased_agents": purchased_agents,
        "status": status,
    }
    _append_jsonl(COMMERCIAL_EVENTS_FILE, event)

    return {
        "success": True,
        "request_id": request_id,
        "change_type": change_type,
        "status": status,
        "tenant_id": tenant_id,
        "client_number": client_number,
        "current_package": current_package,
        "target_package": target_package,
        "downgrade_check": downgrade_check,
        "billing_sync_required": status in {"ready_for_billing_sync", "ready_for_checkout"},
        "checkout_required": status == "ready_for_checkout",
        "owner_sales_review_required": status == "owner_sales_review_required",
        "customer_safe_response_mode": True,
        "secret_exposure": False,
        "entitlement_bypass": False,
        "governance_bypass": False,
    }


def apply_entitlement_change_after_billing(payload: Dict[str, Any]) -> Dict[str, Any]:
    tenant_id = payload.get("tenant_id")
    client_number = payload.get("client_number")
    target_package = _normalise_package(payload.get("target_package"))
    purchased_agents = list(dict.fromkeys(payload.get("purchased_agents") or []))
    active_agents = list(dict.fromkeys(payload.get("active_agents") or []))
    billing_status = str(payload.get("billing_status") or "paid").lower()

    subscription_decision = evaluate_subscription_status(
        "active" if billing_status == "trial_active" else billing_status
    )

    if not subscription_decision.get("subscription_execution_allowed"):
        return {
            "success": False,
            "error": "billing_not_active",
            "billing_status": billing_status,
            "subscription_decision": subscription_decision,
            "customer_safe_message": "Billing must be active before this change can be applied.",
        }

    state_result = upsert_marketplace_state({
        "tenant_id": tenant_id,
        "client_number": client_number,
        "package": target_package,
        "purchased_agents": purchased_agents,
        "active_agents": active_agents,
    })

    event = {
        "timestamp": _now(),
        "event_type": "entitlement_change_applied_after_billing",
        "tenant_id": tenant_id,
        "client_number": client_number,
        "target_package": target_package,
        "billing_status": billing_status,
        "success": state_result.get("success"),
    }
    _append_jsonl(COMMERCIAL_EVENTS_FILE, event)

    return {
        "success": state_result.get("success"),
        "status": "entitlement_change_applied",
        "tenant_id": tenant_id,
        "client_number": client_number,
        "package": target_package,
        "state": state_result.get("state"),
        "billing_status": billing_status,
        "customer_safe_response_mode": True,
        "secret_exposure": False,
        "entitlement_bypass": False,
        "governance_bypass": False,
    }


def marketplace_commercial_summary(payload: Dict[str, Any]) -> Dict[str, Any]:
    tenant_id = payload.get("tenant_id")
    events = _read_jsonl(COMMERCIAL_EVENTS_FILE, limit=5000)

    if tenant_id:
        events = [event for event in events if event.get("tenant_id") == tenant_id]

    event_counts: Dict[str, int] = {}
    for event in events:
        event_type = event.get("event_type") or "unknown"
        event_counts[event_type] = event_counts.get(event_type, 0) + 1

    return {
        "success": True,
        "summary_profile": "priority9_marketplace_commercial_summary_v1",
        "tenant_id": tenant_id,
        "event_count": len(events),
        "event_counts": event_counts,
        "recent_events": events[-25:],
        "pricing_catalogue": PACKAGE_PRICING,
        "customer_safe_response_mode": True,
        "secret_exposure": False,
    }
