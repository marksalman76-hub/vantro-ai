from pathlib import Path

checks = {
    "frontend/src/lib/billingStripeSubscriptions.ts": [
        "BillingSubscriptionRecord",
        "BILLING_PACKAGE_PRICES",
        "persistBillingSubscription",
        "getBillingSubscription",
        "buildBillingSubscriptionStatus",
        "billing-subscriptions.json",
        "enforcement_ready_for_row14",
    ],
    "frontend/src/app/api/billing-checkout/route.ts": [
        "persistBillingSubscription",
        "billing_stripe_subscriptions_enabled",
        "billing_subscription_persisted",
        "credential_values_exposed: false",
        "enforcement_ready_for_row14",
    ],
    "frontend/src/app/api/billing-subscription-status/route.ts": [
        "buildBillingSubscriptionStatus",
        "cache-control",
    ],
    "frontend/src/app/api/admin-billing-subscription-status/route.ts": [
        "Admin authorisation required",
        "buildBillingSubscriptionStatus",
        "owner_visibility",
        "credential_values_exposed: false",
    ],
}

missing = {}

for file, needles in checks.items():
    text = Path(file).read_text(encoding="utf-8")
    absent = [needle for needle in needles if needle not in text]
    if absent:
        missing[file] = absent

if missing:
    raise SystemExit(f"ROW13_BILLING_STRIPE_SUBSCRIPTIONS_FAILED missing={missing}")

print("ROW13_BILLING_STRIPE_SUBSCRIPTIONS_PASSED")
