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
    "target_package": "business",
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
