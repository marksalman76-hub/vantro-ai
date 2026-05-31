from pathlib import Path
from datetime import datetime
import py_compile

ROOT = Path.cwd()
TEST = ROOT / "test_step228_real_stripe_checkout_creation.py"
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(parents=True, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

if TEST.exists():
    backup = BACKUPS / f"test_step228_real_stripe_checkout_creation_before_{timestamp}.py"
    backup.write_text(TEST.read_text(encoding="utf-8"), encoding="utf-8")

TEST.write_text(r'''
import json
import urllib.request

BASE = "http://127.0.0.1:8000"

payload = {
    "tenant_id": "client_live_checkout_test_001",
    "package_name": "growth",
    "customer_email": "stripe-live-checkout-test@example.com",
    "success_url": "https://example.com/client/billing/success",
    "cancel_url": "https://example.com/client/billing/cancel",
    "client_reference_id": "client_live_checkout_test_001",
}

req = urllib.request.Request(
    BASE + "/admin/billing/create-checkout-session",
    data=json.dumps(payload).encode("utf-8"),
    headers={
        "Content-Type": "application/json",
        "x-actor-role": "owner",
        "x-tenant-id": "owner",
    },
    method="POST",
)

with urllib.request.urlopen(req, timeout=60) as res:
    data = json.loads(res.read().decode("utf-8"))

data_text = json.dumps(data).lower()

checks = {
    "checkout_success": data.get("success") is True,
    "checkout_session_created": data.get("status") == "checkout_session_created",
    "subscription_mode": data.get("mode") == "subscription",
    "checkout_session_id_present": bool(data.get("stripe_checkout_session_id")),
    "checkout_url_present": bool(data.get("checkout_url")),
    "month_to_month": data.get("contract_type") == "month_to_month",
    "no_secret_values_exposed": all(secret not in data_text for secret in [
        "sk_live_",
        "sk_test_",
        "sk-",
        "whsec_",
        "postgresql://",
        "ecomagentsecure",
    ]),
}

print("STEP_228_REAL_STRIPE_CHECKOUT_CREATION_RESULTS")

for name, passed in checks.items():
    print(name, passed)

print("checkout_url", data.get("checkout_url"))

failed = [name for name, passed in checks.items() if not passed]

if failed:
    print("FAILED", failed)
    print(json.dumps(data, indent=2))
    raise SystemExit(1)

print("STEP_228_REAL_STRIPE_CHECKOUT_CREATION_OK")
'''.lstrip(), encoding="utf-8")

py_compile.compile(str(TEST), doraise=True)

print("STEP_228_REAL_STRIPE_CHECKOUT_CREATION_TEST_INSTALLED")
print(f"Created/updated: {TEST}")
print("STEP_228_OK")