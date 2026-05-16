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
