import json
import os
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:8000"

payload = {
    "type": "invoice.payment_failed",
    "data": {
        "object": {
            "customer": "cus_step224_signature_test",
            "subscription": "sub_step224_signature_test",
            "billing_reason": "subscription_cycle",
            "status": "open",
            "current_period_start": 1767225600,
            "current_period_end": 1769904000,
        }
    },
}

req = urllib.request.Request(
    BASE + "/webhooks/stripe/hardened",
    data=json.dumps(payload).encode("utf-8"),
    headers={"Content-Type": "application/json"},
    method="POST",
)

print("STEP_224_STRIPE_WEBHOOK_SIGNATURE_LOCK_RESULTS")

try:
    with urllib.request.urlopen(req, timeout=30) as res:
        status = res.status
        body = json.loads(res.read().decode("utf-8"))
except urllib.error.HTTPError as err:
    status = err.code
    try:
        body = json.loads(err.read().decode("utf-8"))
    except Exception:
        body = {"raw": "unreadable"}

app_env = os.getenv("APP_ENV", "").lower()
production_mode = app_env in {"production", "prod"}

checks = {
    "controlled_response_received": isinstance(body, dict),
}

if production_mode:
    checks["production_rejects_unsigned_webhook"] = status == 400
    checks["production_does_not_process_unsigned"] = body.get("success") is not True
else:
    checks["non_production_allows_unsigned_for_local_testing"] = status == 200
    checks["non_production_signature_marked_unverified"] = body.get("signature", {}).get("verified") is False
    checks["non_production_signature_config_safe"] = "signature" in body

body_text = json.dumps(body).lower()
checks["no_secret_values_exposed"] = all(secret not in body_text for secret in [
    "sk_",
    "sk-",
    "whsec_",
    "postgresql://",
    "ecomagentsecure",
])

print("APP_ENV", app_env or "not_set")
print("http_status", status)

for name, passed in checks.items():
    print(name, passed)

failed = [name for name, passed in checks.items() if not passed]

if failed:
    print("FAILED", failed)
    print(json.dumps(body, indent=2))
    raise SystemExit(1)

print("STEP_224_STRIPE_WEBHOOK_SIGNATURE_LOCK_OK")
