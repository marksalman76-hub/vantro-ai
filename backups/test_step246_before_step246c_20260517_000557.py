import json
import urllib.request
import urllib.error
from pathlib import Path

BASE = "http://127.0.0.1:8000"
ROOT = Path.cwd()

record_path = ROOT / "backend" / "app" / "data" / "step246_paid_checkout_smoke_lock.json"
record = json.loads(record_path.read_text(encoding="utf-8"))


def post_json(path, payload):
    req = urllib.request.Request(
        BASE + path,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-actor-role": "owner",
            "x-tenant-id": "owner",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as res:
            return res.status, json.loads(res.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8")
        try:
            data = json.loads(body)
        except Exception:
            data = {"raw": body}
        return exc.code, data


def get_json(path):
    req = urllib.request.Request(
        BASE + path,
        headers={
            "x-actor-role": "owner",
            "x-tenant-id": "owner",
        },
        method="GET",
    )
    with urllib.request.urlopen(req, timeout=30) as res:
        return res.status, json.loads(res.read().decode("utf-8"))


readiness_status, readiness = get_json("/admin/billing/stripe-checkout-readiness")

payload = {
    "tenant_id": "client_step246_checkout",
    "customer_email": "step246-checkout@example.com",
    "package_name": "growth",
    "billing_cycle": "monthly",
    "success_url": "https://trance-formation.com.au/client/billing/success",
    "cancel_url": "https://trance-formation.com.au/client/billing/cancel",
}

checkout_status, checkout = post_json("/admin/billing/create-checkout-session", payload)

combined = json.dumps({
    "record": record,
    "readiness": readiness,
    "checkout": checkout,
}).lower()

checkout_url = checkout.get("checkout_url") or checkout.get("url")
session_id = checkout.get("checkout_session_id") or checkout.get("session_id")

checks = {
    "record_success": record.get("success") is True,
    "status_locked": record.get("status") == "paid_checkout_smoke_requirements_locked",
    "readiness_route_ok": readiness_status == 200 and readiness.get("success") is True,
    "stripe_ready_for_live_checkout": readiness.get("ready_for_live_checkout") is True,
    "checkout_route_controlled": checkout_status in {200, 201, 400, 422},
    "checkout_success": checkout.get("success") is True,
    "checkout_session_id_present": bool(session_id),
    "checkout_url_present": bool(checkout_url),
    "stripe_checkout_url": isinstance(checkout_url, str) and "checkout.stripe.com" in checkout_url,
    "subscription_or_checkout_mode": (
        checkout.get("mode") == "subscription"
        or checkout.get("checkout_mode") == "subscription"
        or checkout.get("status") in {"checkout_session_created", "advanced_checkout_session_created"}
    ),
    "no_secret_values_exposed": all(secret not in combined for secret in [
        "sk_live_",
        "sk_test_",
        "sk-",
        "whsec_",
        "postgresql://",
        "ecomagentsecure",
    ]),
}

print("STEP_246_PAID_CHECKOUT_SMOKE_LOCK_RESULTS")
for name, passed in checks.items():
    print(name, passed)

print("readiness_status", readiness_status)
print("checkout_status", checkout_status)
print("checkout_url_present", bool(checkout_url))

failed = [name for name, passed in checks.items() if not passed]

if failed:
    print("FAILED", failed)
    print(json.dumps({
        "readiness": readiness,
        "checkout": checkout,
    }, indent=2))
    raise SystemExit(1)

print("STEP_246_PAID_CHECKOUT_SMOKE_LOCK_OK")
