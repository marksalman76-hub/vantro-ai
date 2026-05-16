import json
import os
import urllib.request

import sitecustomize  # force local .env loading

BASE = "http://127.0.0.1:8000"

required_env = [
    "STRIPE_SECRET_KEY",
    "STRIPE_WEBHOOK_SECRET",
    "STRIPE_PRICE_STARTER_MONTHLY",
    "STRIPE_PRICE_GROWTH_MONTHLY",
    "STRIPE_PRICE_PRO_MONTHLY",
    "STRIPE_PRICE_ENTERPRISE_MONTHLY",
    "STRIPE_CHECKOUT_SUCCESS_URL",
    "STRIPE_CHECKOUT_CANCEL_URL",
    "STRIPE_BILLING_PORTAL_RETURN_URL",
]

env_status = {
    key: bool(os.getenv(key))
    for key in required_env
}

def request_json(path):
    req = urllib.request.Request(
        BASE + path,
        headers={
            "Content-Type": "application/json",
            "x-actor-role": "owner",
            "x-tenant-id": "owner",
        },
        method="GET",
    )
    with urllib.request.urlopen(req, timeout=30) as res:
        return json.loads(res.read().decode("utf-8"))

checkout_readiness = request_json("/admin/billing/stripe-checkout-readiness")

combined_text = json.dumps({
    "env_status": env_status,
    "checkout_readiness": checkout_readiness,
}).lower()

checks = {
    "all_required_env_present": all(env_status.values()),
    "checkout_readiness_route_success": checkout_readiness.get("success") is True,
    "stripe_secret_configured": checkout_readiness.get("stripe_secret_key_configured") is True,
    "webhook_secret_configured": checkout_readiness.get("stripe_webhook_secret_configured") is True,
    "all_package_prices_configured": len(checkout_readiness.get("missing_price_packages", [])) == 0,
    "ready_for_live_checkout": checkout_readiness.get("ready_for_live_checkout") is True,
    "no_secret_values_exposed": all(secret not in combined_text for secret in [
        "sk_live_",
        "sk_test_",
        "sk-",
        "whsec_",
        "postgresql://",
        "ecomagentsecure",
    ]),
}

print("STEP_227_LIVE_STRIPE_ENV_READINESS_RESULTS")
print("env_status", env_status)

for name, passed in checks.items():
    print(name, passed)

failed = [name for name, passed in checks.items() if not passed]

if failed:
    print("FAILED", failed)
    print("Missing env:", [key for key, value in env_status.items() if not value])
    raise SystemExit(1)

print("STEP_227_LIVE_STRIPE_ENV_READINESS_OK")
