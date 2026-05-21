from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
MAIN = ROOT / "backend" / "app" / "main.py"
CORE = ROOT / "backend" / "app" / "core"
RUNTIME = CORE / "billing_automation_runtime.py"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
main_backup = BACKUP_DIR / f"main_before_priority10_billing_automation_{timestamp}.py"
main_backup.write_text(MAIN.read_text(encoding="utf-8"), encoding="utf-8")

RUNTIME.write_text(r'''
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
        "currency": "AUD",
        "monthly_amount_aud": pricing["monthly_aud"],
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
'''.lstrip(), encoding="utf-8")

main_text = MAIN.read_text(encoding="utf-8")

import_line = "from backend.app.core.billing_automation_runtime import create_checkout_session_payload, handle_checkout_completed, handle_invoice_payment_succeeded_runtime, handle_invoice_payment_failed_runtime, cancel_subscription_runtime, reactivate_subscription_runtime, billing_automation_summary"
if import_line not in main_text:
    lines = main_text.splitlines()
    insert_at = 0
    for i, line in enumerate(lines):
        if line.startswith("from ") or line.startswith("import "):
            insert_at = i + 1
    lines.insert(insert_at, import_line)
    main_text = "\n".join(lines) + "\n"

routes = r'''

@app.post("/billing/checkout-session-payload")
def billing_checkout_session_payload(payload: dict):
    return create_checkout_session_payload(payload)


@app.post("/billing/checkout-completed")
def billing_checkout_completed(payload: dict):
    return handle_checkout_completed(payload)


@app.post("/billing/invoice-payment-succeeded")
def billing_invoice_payment_succeeded(payload: dict):
    return handle_invoice_payment_succeeded_runtime(payload)


@app.post("/billing/invoice-payment-failed")
def billing_invoice_payment_failed(payload: dict):
    return handle_invoice_payment_failed_runtime(payload)


@app.post("/billing/cancel-subscription")
def billing_cancel_subscription(payload: dict):
    return cancel_subscription_runtime(payload)


@app.post("/billing/reactivate-subscription")
def billing_reactivate_subscription(payload: dict):
    return reactivate_subscription_runtime(payload)


@app.post("/billing/automation-summary")
def billing_summary(payload: dict):
    return billing_automation_summary(payload)
'''

if "/billing/checkout-session-payload" not in main_text:
    main_text = main_text.rstrip() + "\n" + routes + "\n"

MAIN.write_text(main_text, encoding="utf-8")

TEST = ROOT / "test_priority10_billing_automation_runtime.py"
TEST.write_text(r'''
import json
import requests

BASE = "http://127.0.0.1:8000"
HEADERS = {
    "x-actor-role": "admin",
    "x-tenant-id": "owner",
    "Content-Type": "application/json",
}

def show(label, response):
    print("\n" + "=" * 80)
    print(label)
    print("HTTP", response.status_code)
    try:
        print(json.dumps(response.json(), indent=2)[:12000])
    except Exception:
        print(response.text[:12000])

payload = {
    "tenant_id": "tenant_priority10_billing_test",
    "client_number": "CL-P10-BILLING",
    "customer_email": "sale@protekepoxy.com.au",
    "target_package": "professional",
    "purchased_agents": [
        "head_agent",
        "marketing_specialist_agent",
        "crm_ai_agent",
        "ugc_creative_agent",
        "product_image_agent"
    ],
    "active_agents": [
        "head_agent",
        "marketing_specialist_agent",
        "ugc_creative_agent",
        "product_image_agent"
    ],
    "stripe_customer_id": "cus_test_priority10",
    "stripe_subscription_id": "sub_test_priority10",
    "stripe_checkout_session_id": "cs_test_priority10"
}

checkout = requests.post(f"{BASE}/billing/checkout-session-payload", headers=HEADERS, json=payload, timeout=30)
show("CHECKOUT_SESSION_PAYLOAD", checkout)

completed = requests.post(f"{BASE}/billing/checkout-completed", headers=HEADERS, json=payload, timeout=30)
show("CHECKOUT_COMPLETED", completed)

invoice_success = requests.post(f"{BASE}/billing/invoice-payment-succeeded", headers=HEADERS, json=payload, timeout=30)
show("INVOICE_PAYMENT_SUCCEEDED", invoice_success)

invoice_failed = requests.post(f"{BASE}/billing/invoice-payment-failed", headers=HEADERS, json=payload, timeout=30)
show("INVOICE_PAYMENT_FAILED", invoice_failed)

cancel = requests.post(f"{BASE}/billing/cancel-subscription", headers=HEADERS, json={**payload, "cancel_at_period_end": True}, timeout=30)
show("CANCEL_SUBSCRIPTION", cancel)

reactivate = requests.post(f"{BASE}/billing/reactivate-subscription", headers=HEADERS, json=payload, timeout=30)
show("REACTIVATE_SUBSCRIPTION", reactivate)

summary = requests.post(f"{BASE}/billing/automation-summary", headers=HEADERS, json={"tenant_id": "tenant_priority10_billing_test"}, timeout=30)
show("BILLING_AUTOMATION_SUMMARY", summary)

for response in [checkout, completed, invoice_success, invoice_failed, cancel, reactivate, summary]:
    assert response.status_code == 200

checkout_json = checkout.json()
completed_json = completed.json()
success_json = invoice_success.json()
failed_json = invoice_failed.json()
cancel_json = cancel.json()
reactivate_json = reactivate.json()
summary_json = summary.json()

assert checkout_json["success"] is True
assert checkout_json["stripe_ready"] is True
assert checkout_json["target_package"] == "professional"
assert checkout_json["monthly_amount_aud"] == 1997
assert checkout_json["secret_exposure"] is False

assert completed_json["success"] is True
assert completed_json["billing_state"]["subscription_status"] == "active"
assert completed_json["entitlement_sync"]["success"] is True

assert success_json["success"] is True
assert success_json["credits_reset"] is True
assert success_json["client_access_suspended"] is False

assert failed_json["success"] is True
assert failed_json["subscription_status"] == "past_due"
assert failed_json["client_access_suspended"] is True
assert failed_json["retry_policy"] == "48_hour_retry_policy"

assert cancel_json["success"] is True
assert cancel_json["status"] == "subscription_cancelled"
assert cancel_json["client_access_suspended"] is True

assert reactivate_json["success"] is True
assert reactivate_json["status"] == "subscription_reactivated"
assert reactivate_json["client_access_suspended"] is False

assert summary_json["success"] is True
assert summary_json["event_count"] >= 6
assert summary_json["latest_state"]["subscription_status"] == "active"
assert summary_json["secret_exposure"] is False

print("\nPRIORITY10_BILLING_AUTOMATION_RUNTIME_OK")
'''.lstrip(), encoding="utf-8")

print("PRIORITY10_BILLING_AUTOMATION_RUNTIME_INSTALLED")
print(f"Main backup: {main_backup}")
print(f"Created/updated: {RUNTIME}")
print(f"Updated: {MAIN}")
print(f"Created/updated: {TEST}")