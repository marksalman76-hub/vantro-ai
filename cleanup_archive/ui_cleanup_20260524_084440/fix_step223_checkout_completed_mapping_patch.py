from pathlib import Path
from datetime import datetime
import py_compile

ROOT = Path.cwd()
ROUTES = ROOT / "backend" / "app" / "api" / "subscription_policy_routes.py"
TEST = ROOT / "test_step223_checkout_completed_mapping_lock.py"
BACKUPS = ROOT / "backups"

BACKUPS.mkdir(parents=True, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

backup = BACKUPS / f"subscription_policy_routes_before_step223b_{timestamp}.py"
backup.write_text(ROUTES.read_text(encoding="utf-8"), encoding="utf-8")

text = ROUTES.read_text(encoding="utf-8")

old = """    billing_runtime_update = apply_stripe_classification_to_billing_runtime(event, classification)

    return {
        "success": True,
        "route": "/webhooks/stripe/hardened",
        "signature": signature_result,
        "event": event,
        "classification": classification,
        "billing_runtime_update": billing_runtime_update,
"""

new = """    checkout_mapping_update = None

    if event["event_type"] == "checkout.session.completed":
        raw_object = payload.get("data", {}).get("object", {}) if isinstance(payload, dict) else {}
        metadata = raw_object.get("metadata", {}) if isinstance(raw_object, dict) else {}

        tenant_id = (
            metadata.get("tenant_id")
            or raw_object.get("client_reference_id")
        )

        package_name = (
            metadata.get("package_name")
            or raw_object.get("package_name")
            or "unknown"
        )

        stripe_customer_id = raw_object.get("customer")
        stripe_subscription_id = raw_object.get("subscription")
        company_name = (
            metadata.get("company_name")
            or raw_object.get("client_reference_id")
            or tenant_id
        )

        if tenant_id and stripe_customer_id and stripe_subscription_id:
            checkout_mapping_update = upsert_stripe_tenant_mapping(
                tenant_id=str(tenant_id),
                stripe_customer_id=str(stripe_customer_id),
                stripe_subscription_id=str(stripe_subscription_id),
                company_name=str(company_name),
                subscription_status="active",
                package_name=str(package_name),
            )
        else:
            checkout_mapping_update = {
                "success": False,
                "reason": "checkout_session_missing_required_mapping_fields",
                "tenant_id_present": bool(tenant_id),
                "stripe_customer_id_present": bool(stripe_customer_id),
                "stripe_subscription_id_present": bool(stripe_subscription_id),
            }

    billing_runtime_update = apply_stripe_classification_to_billing_runtime(event, classification)

    return {
        "success": True,
        "route": "/webhooks/stripe/hardened",
        "signature": signature_result,
        "event": event,
        "classification": classification,
        "checkout_mapping_update": checkout_mapping_update,
        "billing_runtime_update": billing_runtime_update,
"""

if old not in text:
    raise RuntimeError("Expected webhook runtime block not found.")

text = text.replace(old, new)

ROUTES.write_text(text, encoding="utf-8")

TEST.write_text(r'''
import json
import urllib.request

BASE = "http://127.0.0.1:8000"

TENANT_ID = "client_step223_001"
CUSTOMER_ID = "cus_step223_001"
SUBSCRIPTION_ID = "sub_step223_001"


def request_json(path, method="GET", payload=None):
    data = None

    if payload is not None:
        data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(
        BASE + path,
        data=data,
        headers={
            "Content-Type": "application/json",
            "x-tenant-id": "owner",
            "x-actor-role": "owner",
        },
        method=method,
    )

    with urllib.request.urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


checkout_event = {
    "type": "checkout.session.completed",
    "data": {
        "object": {
            "id": "cs_step223_001",
            "mode": "subscription",
            "customer": CUSTOMER_ID,
            "subscription": SUBSCRIPTION_ID,
            "client_reference_id": TENANT_ID,
            "customer_email": "step223@example.com",
            "metadata": {
                "tenant_id": TENANT_ID,
                "package_name": "growth",
                "company_name": "Step 223 Test Client"
            }
        }
    }
}

webhook_result = request_json(
    "/webhooks/stripe/hardened",
    method="POST",
    payload=checkout_event,
)

mappings = request_json("/admin/billing/stripe-tenant-mappings?limit=50")

matching = [
    item for item in mappings.get("mappings", [])
    if item.get("tenant_id") == TENANT_ID
]

checks = {
    "webhook_success": webhook_result.get("success") is True,
    "checkout_mapping_update_present": isinstance(webhook_result.get("checkout_mapping_update"), dict),
    "checkout_mapping_success": webhook_result.get("checkout_mapping_update", {}).get("success") is True,
    "mapping_found": len(matching) >= 1,
    "mapping_customer_match": any(item.get("stripe_customer_id") == CUSTOMER_ID for item in matching),
    "mapping_subscription_match": any(item.get("stripe_subscription_id") == SUBSCRIPTION_ID for item in matching),
    "mapping_active": any(item.get("subscription_status") == "active" for item in matching),
    "mapping_growth_package": any(item.get("package_name") == "growth" for item in matching),
}

print("STEP_223_CHECKOUT_COMPLETED_MAPPING_LOCK_RESULTS")

for name, passed in checks.items():
    print(name, passed)

failed = [name for name, passed in checks.items() if not passed]

if failed:
    print("FAILED", failed)
    print(json.dumps({
        "webhook_result": webhook_result,
        "mappings": mappings,
    }, indent=2))
    raise SystemExit(1)

print("STEP_223_CHECKOUT_COMPLETED_MAPPING_LOCK_OK")
'''.lstrip(), encoding="utf-8")

py_compile.compile(str(ROUTES), doraise=True)
py_compile.compile(str(TEST), doraise=True)

print("STEP_223B_CHECKOUT_MAPPING_PATCH_OK")
print(f"Backup: {backup}")
print(f"Updated: {ROUTES}")
print(f"Created: {TEST}")