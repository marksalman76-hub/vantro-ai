import json
import urllib.request

BASE = "http://127.0.0.1:8000"

def request_json(path, method="GET", payload=None):
    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(
        BASE + path,
        data=data,
        headers={
            "Content-Type": "application/json",
            "x-actor-role": "owner",
            "x-tenant-id": "owner",
        },
        method=method,
    )

    with urllib.request.urlopen(req, timeout=30) as res:
        return json.loads(res.read().decode("utf-8"))


readiness = request_json("/admin/billing/stripe-checkout-readiness")

checkout_attempt = request_json(
    "/admin/billing/create-checkout-session",
    method="POST",
    payload={
        "tenant_id": "client_step222_001",
        "package_name": "growth",
        "customer_email": "step222@example.com",
        "success_url": "https://example.com/success",
        "cancel_url": "https://example.com/cancel",
    },
)

readiness_text = json.dumps(readiness).lower()
checkout_text = json.dumps(checkout_attempt).lower()

checks = {
    "readiness_route_success": readiness.get("success") is True,
    "readiness_has_package_prices": isinstance(readiness.get("package_prices"), dict),
    "readiness_no_secret_values": all(secret not in readiness_text for secret in ["sk_", "sk-", "postgresql://", "ecomagentsecure"]),
    "checkout_route_returns_controlled_response": "status" in checkout_attempt,
    "checkout_no_secret_values": all(secret not in checkout_text for secret in ["sk_", "sk-", "postgresql://", "ecomagentsecure"]),
    "checkout_subscription_mode_or_safe_not_created": checkout_attempt.get("mode") == "subscription" or checkout_attempt.get("status") in {
        "checkout_not_created",
        "checkout_creation_failed",
    },
}

print("STEP_222_STRIPE_CHECKOUT_ENDPOINT_LOCK_RESULTS")
for name, passed in checks.items():
    print(name, passed)

failed = [name for name, passed in checks.items() if not passed]

if failed:
    print("FAILED", failed)
    print(json.dumps({"readiness": readiness, "checkout_attempt": checkout_attempt}, indent=2))
    raise SystemExit(1)

print("STEP_222_STRIPE_CHECKOUT_ENDPOINT_LOCK_OK")
