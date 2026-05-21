from pathlib import Path

files = {
    "signup_page": Path("frontend/src/app/signup/page.tsx"),
    "checkout_route": Path("frontend/src/app/api/billing-checkout/route.ts"),
}

for name, path in files.items():
    print(name, path.exists(), path)

signup = files["signup_page"].read_text(encoding="utf-8")
checkout = files["checkout_route"].read_text(encoding="utf-8") if files["checkout_route"].exists() else ""

checks = {
    "signup_posts_to_billing_checkout": "/api/billing-checkout" in signup,
    "signup_sends_customer_email": "customer_email" in signup,
    "signup_sends_target_package": "target_package" in signup,
    "signup_sends_selected_agents": "selected_agents" in signup,
    "checkout_route_exports_post": "export async function POST" in checkout,
    "checkout_calls_backend_live_checkout_session": "/billing/live-checkout-session" in checkout,
    "checkout_reads_selected_agents": "selected_agents" in checkout,
    "checkout_has_success_url": "success_url" in checkout,
    "checkout_has_cancel_url": "cancel_url" in checkout,
}

print("CHECKOUT_WIRING_RESULTS")
for key, value in checks.items():
    print(key, value)

if not all(checks.values()):
    raise SystemExit("CHECKOUT_WIRING_INCOMPLETE")

print("CHECKOUT_WIRING_OK")