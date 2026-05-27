from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
MAIN = ROOT / "backend" / "app" / "main.py"
CORE = ROOT / "backend" / "app" / "core"
RUNTIME = CORE / "live_stripe_bridge_runtime.py"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
main_backup = BACKUP_DIR / f"main_before_priority10_live_stripe_bridge_{timestamp}.py"
main_backup.write_text(MAIN.read_text(encoding="utf-8"), encoding="utf-8")

RUNTIME.write_text(r'''
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from backend.app.core.billing_automation_runtime import create_checkout_session_payload
from backend.app.core.stripe_production_hardening_runtime import (
    route_stripe_webhook_event,
    verify_stripe_webhook_signature,
)


DATA_DIR = Path.cwd() / "runtime_data"
LIVE_STRIPE_EVENTS_FILE = DATA_DIR / "live_stripe_bridge_events.jsonl"


PACKAGE_PRICE_ENV = {
    "starter": "STRIPE_PRICE_STARTER_MONTHLY",
    "growth": "STRIPE_PRICE_GROWTH_MONTHLY",
    "professional": "STRIPE_PRICE_PROFESSIONAL_MONTHLY",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _append_event(record: Dict[str, Any]) -> None:
    LIVE_STRIPE_EVENTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with LIVE_STRIPE_EVENTS_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def _stripe_module():
    try:
        import stripe  # type: ignore
        return stripe
    except Exception:
        return None


def live_stripe_bridge_readiness() -> Dict[str, Any]:
    stripe = _stripe_module()
    stripe_secret = os.getenv("STRIPE_SECRET_KEY")
    frontend_url = os.getenv("FRONTEND_URL")
    backend_url = os.getenv("BACKEND_URL")

    missing_price_keys = [
        key for key in PACKAGE_PRICE_ENV.values()
        if not os.getenv(key)
    ]

    sdk_available = stripe is not None
    ready = bool(sdk_available and stripe_secret and frontend_url and backend_url and not missing_price_keys)

    return {
        "success": True,
        "readiness_profile": "priority10_live_stripe_bridge_readiness_v1",
        "live_stripe_ready": ready,
        "stripe_sdk_available": sdk_available,
        "stripe_secret_configured": bool(stripe_secret),
        "frontend_url_configured": bool(frontend_url),
        "backend_url_configured": bool(backend_url),
        "missing_price_keys": missing_price_keys,
        "safe_fallback_enabled": True,
        "secret_exposure": False,
    }


def create_live_checkout_session(payload: Dict[str, Any]) -> Dict[str, Any]:
    readiness = live_stripe_bridge_readiness()
    base_payload = create_checkout_session_payload(payload)

    target_package = base_payload.get("target_package")
    price_env = PACKAGE_PRICE_ENV.get(str(target_package))
    price_id = os.getenv(price_env or "")

    if not readiness.get("live_stripe_ready"):
        _append_event({
            "timestamp": _now(),
            "event_type": "live_checkout_session_fallback",
            "tenant_id": payload.get("tenant_id"),
            "target_package": target_package,
            "reason": "stripe_not_ready",
        })

        return {
            "success": True,
            "mode": "safe_fallback",
            "live_stripe_ready": False,
            "checkout_session_created": False,
            "checkout_payload": base_payload,
            "readiness": readiness,
            "secret_exposure": False,
        }

    stripe = _stripe_module()
    stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

    frontend_url = os.getenv("FRONTEND_URL", "").rstrip("/")
    success_url = f"{frontend_url}{base_payload.get('success_url_path')}?session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{frontend_url}{base_payload.get('cancel_url_path')}"

    try:
        session = stripe.checkout.Session.create(
            mode="subscription",
            customer_email=base_payload.get("customer_email"),
            line_items=[{"price": price_id, "quantity": 1}],
            success_url=success_url,
            cancel_url=cancel_url,
            metadata=base_payload.get("metadata") or {},
        )

        _append_event({
            "timestamp": _now(),
            "event_type": "live_checkout_session_created",
            "tenant_id": payload.get("tenant_id"),
            "target_package": target_package,
            "session_id": getattr(session, "id", None),
        })

        return {
            "success": True,
            "mode": "live_stripe",
            "live_stripe_ready": True,
            "checkout_session_created": True,
            "session_id": getattr(session, "id", None),
            "checkout_url": getattr(session, "url", None),
            "secret_exposure": False,
        }
    except Exception as error:
        _append_event({
            "timestamp": _now(),
            "event_type": "live_checkout_session_failed",
            "tenant_id": payload.get("tenant_id"),
            "target_package": target_package,
            "error_type": type(error).__name__,
        })

        return {
            "success": False,
            "mode": "live_stripe",
            "error": "stripe_checkout_session_failed",
            "error_type": type(error).__name__,
            "secret_exposure": False,
        }


def create_live_billing_portal_session(payload: Dict[str, Any]) -> Dict[str, Any]:
    readiness = live_stripe_bridge_readiness()
    stripe_customer_id = payload.get("stripe_customer_id")

    if not readiness.get("live_stripe_ready") or not stripe_customer_id:
        return {
            "success": True,
            "mode": "safe_fallback",
            "portal_session_created": False,
            "reason": "stripe_not_ready_or_missing_customer",
            "readiness": readiness,
            "secret_exposure": False,
        }

    stripe = _stripe_module()
    stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

    frontend_url = os.getenv("FRONTEND_URL", "").rstrip("/")
    return_url = f"{frontend_url}/client/billing"

    try:
        session = stripe.billing_portal.Session.create(
            customer=stripe_customer_id,
            return_url=return_url,
        )

        _append_event({
            "timestamp": _now(),
            "event_type": "live_billing_portal_session_created",
            "tenant_id": payload.get("tenant_id"),
        })

        return {
            "success": True,
            "mode": "live_stripe",
            "portal_session_created": True,
            "portal_url": getattr(session, "url", None),
            "secret_exposure": False,
        }
    except Exception as error:
        _append_event({
            "timestamp": _now(),
            "event_type": "live_billing_portal_session_failed",
            "tenant_id": payload.get("tenant_id"),
            "error_type": type(error).__name__,
        })

        return {
            "success": False,
            "mode": "live_stripe",
            "error": "stripe_portal_session_failed",
            "error_type": type(error).__name__,
            "secret_exposure": False,
        }


def ingest_live_stripe_webhook(payload: Dict[str, Any]) -> Dict[str, Any]:
    raw_body = str(payload.get("raw_body") or "")
    signature = str(payload.get("signature") or "")
    event_type = str(payload.get("event_type") or "")
    event_payload = payload.get("payload") or {}

    verify = verify_stripe_webhook_signature({
        "raw_body": raw_body,
        "signature": signature,
        "test_webhook_secret": payload.get("test_webhook_secret"),
    })

    if not verify.get("verified"):
        _append_event({
            "timestamp": _now(),
            "event_type": "live_webhook_rejected_invalid_signature",
            "stripe_event_type": event_type,
        })

        return {
            "success": False,
            "error": "invalid_webhook_signature",
            "verified": False,
            "secret_exposure": False,
        }

    route_result = route_stripe_webhook_event({
        "event_type": event_type,
        "payload": event_payload,
    })

    _append_event({
        "timestamp": _now(),
        "event_type": "live_webhook_ingested",
        "stripe_event_type": event_type,
        "route_success": route_result.get("success"),
    })

    return {
        "success": True,
        "verified": True,
        "stripe_event_type": event_type,
        "route_result": route_result,
        "secret_exposure": False,
    }
'''.lstrip(), encoding="utf-8")

main_text = MAIN.read_text(encoding="utf-8")

import_line = "from backend.app.core.live_stripe_bridge_runtime import live_stripe_bridge_readiness, create_live_checkout_session, create_live_billing_portal_session, ingest_live_stripe_webhook"
if import_line not in main_text:
    lines = main_text.splitlines()
    insert_at = 0
    for i, line in enumerate(lines):
        if line.startswith("from ") or line.startswith("import "):
            insert_at = i + 1
    lines.insert(insert_at, import_line)
    main_text = "\n".join(lines) + "\n"

routes = r'''

@app.get("/billing/live-stripe-readiness")
def billing_live_stripe_readiness():
    return live_stripe_bridge_readiness()


@app.post("/billing/live-checkout-session")
def billing_live_checkout_session(payload: dict):
    return create_live_checkout_session(payload)


@app.post("/billing/live-portal-session")
def billing_live_portal_session(payload: dict):
    return create_live_billing_portal_session(payload)


@app.post("/webhooks/stripe/live")
def webhooks_stripe_live(payload: dict):
    return ingest_live_stripe_webhook(payload)
'''

if "/billing/live-stripe-readiness" not in main_text:
    main_text = main_text.rstrip() + "\n" + routes + "\n"

MAIN.write_text(main_text, encoding="utf-8")

TEST = ROOT / "test_priority10_live_stripe_bridge.py"
TEST.write_text(r'''
import hashlib
import hmac
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
        print(json.dumps(response.json(), indent=2)[:14000])
    except Exception:
        print(response.text[:14000])

payload = {
    "tenant_id": "tenant_priority10_live_stripe_test",
    "client_number": "CL-P10-LIVE",
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
    "stripe_customer_id": "cus_test_priority10_live"
}

readiness = requests.get(f"{BASE}/billing/live-stripe-readiness", headers=HEADERS, timeout=30)
show("LIVE_STRIPE_READINESS", readiness)

checkout = requests.post(f"{BASE}/billing/live-checkout-session", headers=HEADERS, json=payload, timeout=30)
show("LIVE_CHECKOUT_SESSION", checkout)

portal = requests.post(f"{BASE}/billing/live-portal-session", headers=HEADERS, json=payload, timeout=30)
show("LIVE_PORTAL_SESSION", portal)

raw_body = '{"id":"evt_live_test","type":"invoice.payment_succeeded"}'
secret = "whsec_live_bridge_test"
signature = hmac.new(secret.encode("utf-8"), raw_body.encode("utf-8"), hashlib.sha256).hexdigest()

webhook = requests.post(
    f"{BASE}/webhooks/stripe/live",
    headers=HEADERS,
    json={
        "raw_body": raw_body,
        "signature": signature,
        "test_webhook_secret": secret,
        "event_type": "invoice.payment_succeeded",
        "payload": payload,
    },
    timeout=30,
)
show("LIVE_WEBHOOK_INGESTION", webhook)

for response in [readiness, checkout, portal, webhook]:
    assert response.status_code == 200

readiness_json = readiness.json()
checkout_json = checkout.json()
portal_json = portal.json()
webhook_json = webhook.json()

assert readiness_json["success"] is True
assert readiness_json["secret_exposure"] is False

assert checkout_json["success"] is True
assert checkout_json["secret_exposure"] is False
assert checkout_json["mode"] in {"safe_fallback", "live_stripe"}

assert portal_json["success"] is True
assert portal_json["secret_exposure"] is False
assert portal_json["mode"] in {"safe_fallback", "live_stripe"}

assert webhook_json["success"] is True
assert webhook_json["verified"] is True
assert webhook_json["route_result"]["success"] is True
assert webhook_json["secret_exposure"] is False

print("\nPRIORITY10_LIVE_STRIPE_BRIDGE_OK")
'''.lstrip(), encoding="utf-8")

print("PRIORITY10_LIVE_STRIPE_BRIDGE_INSTALLED")
print(f"Main backup: {main_backup}")
print(f"Created/updated: {RUNTIME}")
print(f"Updated: {MAIN}")
print(f"Created/updated: {TEST}")