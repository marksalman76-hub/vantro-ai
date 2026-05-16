import json
import urllib.request

BASE = "http://127.0.0.1:8000"
TENANT_ID = "client_step223_001"


def request_json(path, method="GET", payload=None, tenant_header="owner", role="owner"):
    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(
        BASE + path,
        data=data,
        headers={
            "Content-Type": "application/json",
            "x-tenant-id": tenant_header,
            "x-actor-role": role,
        },
        method=method,
    )

    with urllib.request.urlopen(req, timeout=30) as res:
        return json.loads(res.read().decode("utf-8"))


visibility = request_json(f"/customer/billing/visibility?tenant_id={TENANT_ID}")
readiness = request_json(f"/admin/billing/customer-portal-readiness?tenant_id={TENANT_ID}")
portal_attempt = request_json(
    "/admin/billing/create-customer-portal-session",
    method="POST",
    payload={"tenant_id": TENANT_ID},
)

combined_text = json.dumps({
    "visibility": visibility,
    "readiness": readiness,
    "portal_attempt": portal_attempt,
}).lower()

checks = {
    "visibility_success": visibility.get("success") is True,
    "billing_visibility_present": isinstance(visibility.get("billing_visibility"), dict),
    "month_to_month_visible": visibility.get("billing_visibility", {}).get("month_to_month") is True,
    "no_lock_in_visible": visibility.get("billing_visibility", {}).get("lock_in_contract") is False,
    "mapping_available": visibility.get("stripe_mapping", {}).get("mapping_available") is True,
    "customer_id_presence_only": visibility.get("stripe_mapping", {}).get("stripe_customer_id_present") is True,
    "subscription_id_presence_only": visibility.get("stripe_mapping", {}).get("stripe_subscription_id_present") is True,
    "invoice_visibility_safe_placeholder": visibility.get("invoices", {}).get("safe_placeholder") is True,
    "portal_readiness_success": readiness.get("success") is True,
    "portal_attempt_controlled": portal_attempt.get("status") in {
        "billing_portal_not_created",
        "billing_portal_session_created",
        "billing_portal_creation_failed",
    },
    "no_secret_values_exposed": all(secret not in combined_text for secret in [
        "sk_",
        "sk-",
        "whsec_",
        "postgresql://",
        "ecomagentsecure",
    ]),
}

print("STEP_226_CUSTOMER_BILLING_PORTAL_INVOICE_LOCK_RESULTS")
for name, passed in checks.items():
    print(name, passed)

failed = [name for name, passed in checks.items() if not passed]

if failed:
    print("FAILED", failed)
    print(json.dumps({
        "visibility": visibility,
        "readiness": readiness,
        "portal_attempt": portal_attempt,
    }, indent=2))
    raise SystemExit(1)

print("STEP_226_CUSTOMER_BILLING_PORTAL_INVOICE_LOCK_OK")
