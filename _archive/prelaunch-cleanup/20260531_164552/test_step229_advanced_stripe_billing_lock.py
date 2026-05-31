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

    with urllib.request.urlopen(req, timeout=60) as res:
        return json.loads(res.read().decode("utf-8"))


readiness = request_json("/admin/billing/advanced-readiness")

advanced_monthly = request_json(
    "/admin/billing/create-advanced-checkout-session",
    method="POST",
    payload={
        "tenant_id": "client_step229_monthly",
        "package_name": "growth",
        "billing_interval": "monthly",
        "customer_email": "step229-monthly@example.com",
        "trial_enabled": True,
        "trial_days": 7,
        "success_url": "https://trance-formation.com.au/client/billing/success",
        "cancel_url": "https://trance-formation.com.au/client/billing/cancel",
    },
)

annual_attempt = request_json(
    "/admin/billing/create-advanced-checkout-session",
    method="POST",
    payload={
        "tenant_id": "client_step229_yearly",
        "package_name": "growth",
        "billing_interval": "yearly",
        "customer_email": "step229-yearly@example.com",
        "trial_enabled": False,
        "success_url": "https://trance-formation.com.au/client/billing/success",
        "cancel_url": "https://trance-formation.com.au/client/billing/cancel",
    },
)

topup_attempt = request_json(
    "/admin/billing/create-topup-checkout-session",
    method="POST",
    payload={
        "tenant_id": "client_step229_topup",
        "topup_size": "small",
        "customer_email": "step229-topup@example.com",
        "success_url": "https://trance-formation.com.au/client/billing/success",
        "cancel_url": "https://trance-formation.com.au/client/billing/cancel",
    },
)

plan_change = request_json(
    "/admin/billing/prepare-plan-change",
    method="POST",
    payload={
        "tenant_id": "client_step229_plan_change",
        "from_package": "starter",
        "to_package": "pro",
        "billing_interval": "monthly",
    },
)

combined = json.dumps({
    "readiness": readiness,
    "advanced_monthly": advanced_monthly,
    "annual_attempt": annual_attempt,
    "topup_attempt": topup_attempt,
    "plan_change": plan_change,
}).lower()

checks = {
    "readiness_success": readiness.get("success") is True,
    "coupons_supported": readiness.get("coupons_supported") is True,
    "trials_supported": readiness.get("free_trials_supported") is True,
    "upgrade_downgrade_supported": readiness.get("upgrade_downgrade_supported") is True,
    "annual_supported": readiness.get("annual_billing_supported") is True,
    "topup_supported": readiness.get("topup_credit_checkout_supported") is True,
    "tax_supported": readiness.get("tax_gst_supported") is True,
    "invoice_polish_supported": readiness.get("invoice_portal_polish_supported") is True,
    "monthly_checkout_controlled": advanced_monthly.get("status") in {
        "advanced_checkout_session_created",
        "advanced_checkout_not_created",
        "advanced_checkout_creation_failed",
    },
    "monthly_trial_field_present": "trial_enabled" in advanced_monthly or advanced_monthly.get("reason") in {
        "stripe_secret_key_not_configured",
        "stripe_price_id_missing",
    },
    "annual_checkout_controlled": annual_attempt.get("status") in {
        "advanced_checkout_session_created",
        "advanced_checkout_not_created",
        "advanced_checkout_creation_failed",
    },
    "topup_checkout_controlled": topup_attempt.get("status") in {
        "topup_checkout_session_created",
        "topup_checkout_not_created",
        "topup_checkout_creation_failed",
    },
    "plan_change_prepared": plan_change.get("status") == "plan_change_prepared",
    "plan_change_proration_supported": plan_change.get("proration_supported") is True,
    "no_secret_values_exposed": all(secret not in combined for secret in [
        "sk_live_",
        "sk_test_",
        "sk-",
        "whsec_",
        "postgresql://",
        "ecomagentsecure",
    ]),
}

print("STEP_229_ADVANCED_STRIPE_BILLING_LOCK_RESULTS")
for name, passed in checks.items():
    print(name, passed)

print("monthly_status", advanced_monthly.get("status"))
print("annual_status", annual_attempt.get("status"))
print("topup_status", topup_attempt.get("status"))

failed = [name for name, passed in checks.items() if not passed]

if failed:
    print("FAILED", failed)
    print(json.dumps({
        "readiness": readiness,
        "advanced_monthly": advanced_monthly,
        "annual_attempt": annual_attempt,
        "topup_attempt": topup_attempt,
        "plan_change": plan_change,
    }, indent=2))
    raise SystemExit(1)

print("STEP_229_ADVANCED_STRIPE_BILLING_LOCK_OK")
