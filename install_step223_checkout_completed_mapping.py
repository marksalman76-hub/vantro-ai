from pathlib import Path
from datetime import datetime
import py_compile

ROOT = Path.cwd()
BACKEND = ROOT / "backend" / "app"
CORE = BACKEND / "core"
API = BACKEND / "api"
BACKUPS = ROOT / "backups"

CORE.mkdir(parents=True, exist_ok=True)
API.mkdir(parents=True, exist_ok=True)
BACKUPS.mkdir(parents=True, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

routes_file = API / "subscription_policy_routes.py"
test_file = ROOT / "test_step223_checkout_completed_mapping_lock.py"

for file in [routes_file, test_file]:
    if file.exists():
        backup = BACKUPS / f"{file.stem}_before_step223_{timestamp}{file.suffix}"
        backup.write_text(file.read_text(encoding="utf-8"), encoding="utf-8")

text = routes_file.read_text(encoding="utf-8")

if "upsert_stripe_tenant_mapping" not in text:
    text = text.replace(
        "from backend.app.core.stripe_billing_runtime_bridge import (",
        "from backend.app.core.stripe_tenant_mapping_store import upsert_stripe_tenant_mapping\nfrom backend.app.core.stripe_billing_runtime_bridge import (",
    )

old = '''    billing_runtime_update = apply_stripe_classification_to_billing_runtime(event, classification)

    return {
        "success": True,
        "route": "/webhooks/stripe/hardened",
        "signature": signature,
        "event": event,
        "classification": classification,
        "billing_runtime_update": billing_runtime_update,
        "policy": {
'''

new = '''    checkout_mapping_update = None

    if event["event_type"] == "checkout.session.completed":
        raw_object = payload.get("data", {}).get("object", {}) if isinstance(payload, dict) else {}
        metadata = raw_object.get("metadata", {}) if isinstance(raw_object, dict) else {}
        subscription_metadata = raw_object.get("subscription_data", {}).get("metadata", {}) if isinstance(raw_object.get("subscription_data", {}), dict) else {}

        tenant_id = (
            metadata.get("tenant_id")
            or subscription_metadata.get("tenant_id")
            or raw_object.get("client_reference_id")
        )

        package_name = (
            metadata.get("package_name")
            or subscription_metadata.get("package_name")
            or raw_object.get("package_name")
            or "unknown"
        )

        stripe_customer_id = raw_object.get("customer") or event.get("stripe_customer_id")
        stripe_subscription_id = raw_object.get("subscription") or event.get("stripe_subscription_id")
        customer_email = (
            raw_object.get("customer_email")
            or raw_object.get("customer_details", {}).get("email")
            if isinstance(raw_object.get("customer_details", {}), dict)
            else raw_object.get("customer_email")
        )

        if tenant_id and stripe_customer_id and stripe_subscription_id:
            checkout_mapping_update = upsert_stripe_tenant_mapping(
                tenant_id=str(tenant_id),
                stripe_customer_id=str(stripe_customer_id),
                stripe_subscription_id=str(stripe_subscription_id),
                company_name=str(metadata.get("company_name") or raw_object.get("client_reference_id") or tenant_id),
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
                "customer_email_present": bool(customer_email),
            }

    billing_runtime_update = apply_stripe_classification_to_billing_runtime(event, classification)

    return {
        "success": True,
        "route": "/webhooks/stripe/hardened",
        "signature": signature,
        "event": event,
        "classification": classification,
        "checkout_mapping_update": checkout_mapping_update,
        "billing_runtime_update": billing_runtime_update,
        "policy": {
'''

if old not in text:
    raise RuntimeError("Expected hardened webhook return block not found.")

text = text.replace(old, new)

routes_file.write_text(text, encoding="utf-8")

test_file.write_text(r'''
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
            "x-actor-role": "owner",
            "x-tenant-id": "owner",
        },
        method=method,
    )

    with urllib.request.urlopen(req, timeout=30) as res:
        return json.loads(res.read().decode("utf-8"))


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

result = request_json("/webhooks/stripe/hardened", method="POST", payload=checkout_event)
mappings = request_json("/admin/billing/stripe-tenant-mappings?limit=20")

matching = [
    item for item in mappings.get("mappings", [])
    if item.get("tenant_id") == TENANT_ID
    and item.get("stripe_customer_id") == CUSTOMER_ID
    and item.get("stripe_subscription_id") == SUBSCRIPTION_ID
]

checks = {
    "webhook_success": result.get("success") is True,
    "event_type_checkout_completed": result.get("event", {}).get("event_type") == "checkout.session.completed",
    "checkout_mapping_success": result.get("checkout_mapping_update", {}).get("success") is True,
    "mapping_list_success": mappings.get("success") is True,
    "mapping_persisted": len(matching) == 1,
    "subscription_status_active": matching[0].get("subscription_status") == "active" if matching else False,
    "package_growth": matching[0].get("package_name") == "growth" if matching else False,
}

print("STEP_223_CHECKOUT_COMPLETED_MAPPING_LOCK_RESULTS")
for name, passed in checks.items():
    print(name, passed)

failed = [name for name, passed in checks.items() if not passed]

if failed:
    print("FAILED", failed)
    print(json.dumps({"webhook_result": result, "mappings": mappings}, indent=2))
    raise SystemExit(1)

print("STEP_223_CHECKOUT_COMPLETED_MAPPING_LOCK_OK")
'''.lstrip(), encoding="utf-8")

py_compile.compile(str(routes_file), doraise=True)
py_compile.compile(str(test_file), doraise=True)

print("STEP_223_CHECKOUT_COMPLETED_MAPPING_INSTALLED")
print(f"Updated: {routes_file}")
print(f"Created/updated: {test_file}")
print("STEP_223_OK")