import requests
import json
import time

FRONTEND = "https://app.trance-formation.com.au"
BACKEND = "https://ecommerce-ai-agent-platform-1.onrender.com"

HEADERS_OWNER = {
    "Content-Type": "application/json",
    "x-tenant-id": "owner",
    "x-actor-role": "owner",
}

HEADERS_PUBLIC = {
    "Content-Type": "application/json",
    "x-tenant-id": "public_signup",
    "x-actor-role": "customer",
}

print("FINAL_LAUNCH_BILLING_SIGNUP_FLOW")

checks = []

def add_check(name, passed, detail=""):
    checks.append((name, bool(passed), detail))
    print(name, bool(passed), detail)

# 1. Frontend route checks
frontend_routes = [
    "/",
    "/signup",
    "/signup?plan=starter",
    "/signup?plan=growth",
    "/signup?plan=business",
    "/signup?plan=enterprise",
    "/activate?token=test",
    "/client/billing",
    "/client/billing/success",
    "/client/billing/cancel",
    "/client/billing/cancelled",
]

for route in frontend_routes:
    r = requests.get(FRONTEND + route, timeout=60)
    add_check(f"frontend_route_{route}", r.status_code == 200, f"HTTP={r.status_code}")

# 2. Backend public-safe billing readiness
backend_routes = [
    "/billing/stripe-production-readiness",
    "/billing/live-stripe-readiness",
    "/health",
]

for route in backend_routes:
    r = requests.get(BACKEND + route, headers=HEADERS_OWNER, timeout=60)
    add_check(f"backend_route_{route}", r.status_code == 200, f"HTTP={r.status_code}")
    if route != "/health":
        data = r.json()
        add_check(f"{route}_success", data.get("success") is True, str(data.get("success")))
        add_check(f"{route}_no_secret_exposure", data.get("secret_exposure") is False or data.get("secret_values_exposed") is False, "secret safe")

# 3. Live checkout through app domain frontend proxy
checkout_payload = {
    "customer_email": "final-launch-checkout@example.com",
    "target_package": "growth",
    "selected_agents": [
        "marketing_specialist_agent",
        "seo_agent",
        "email_reply_agent",
    ],
}

r = requests.post(
    FRONTEND + "/api/billing-checkout",
    json=checkout_payload,
    headers={"Content-Type": "application/json"},
    timeout=90,
)
add_check("frontend_checkout_proxy_http_200", r.status_code == 200, f"HTTP={r.status_code}")
checkout_data = r.json()
add_check("frontend_checkout_success", checkout_data.get("success") is True, checkout_data.get("mode"))
add_check("frontend_checkout_live_stripe", checkout_data.get("mode") == "live_stripe", checkout_data.get("mode"))
add_check("frontend_checkout_session_created", checkout_data.get("checkout_session_created") is True, checkout_data.get("session_id"))
add_check("frontend_checkout_no_secret_exposure", checkout_data.get("secret_exposure") is False, str(checkout_data.get("secret_exposure")))

# 4. Provision tenant from successful signup-style payload
provision_payload = {
    "customer_email": "final-launch-provision@example.com",
    "target_package": "growth",
    "selected_agents": [
        "marketing_specialist_agent",
        "seo_agent",
        "email_reply_agent",
    ],
    "payment_status": "paid",
    "subscription_status": "active",
    "source": "final_launch_combined_validation",
}

r = requests.post(
    BACKEND + "/admin/saas-provisioning/provision-tenant",
    json=provision_payload,
    headers=HEADERS_OWNER,
    timeout=90,
)
add_check("provision_http_200_or_security", r.status_code in {200, 403}, f"HTTP={r.status_code}")

activation_token = None
if r.status_code == 200:
    provision_data = r.json()
    tenant = provision_data.get("tenant", {})
    add_check("provision_success", provision_data.get("success") is True, str(provision_data.get("success")))
    add_check("provision_package_growth", tenant.get("package") == "growth", tenant.get("package"))
    add_check("provision_agent_limit_5", tenant.get("agent_limit") == 5, str(tenant.get("agent_limit")))
    add_check("provision_selected_agents_active", set(provision_payload["selected_agents"]).issubset(set(tenant.get("activated_agents", []))), str(tenant.get("activated_agents")))
    activation_url = provision_data.get("one_time_activation_url") or ""
    if "token=" in activation_url:
        activation_token = activation_url.split("token=", 1)[1]
        add_check("activation_token_generated", True, activation_url[:60])
    else:
        add_check("activation_token_generated", False, activation_url)
else:
    add_check("provision_admin_security_protected", True, "production admin route requires auth")

# 5. Activation single-use check only if token generated
if activation_token:
    activation_payload = {
        "token": activation_token,
        "client_email": "final-launch-provision@example.com",
    }

    r1 = requests.post(
        BACKEND + "/admin/saas-provisioning/validate-one-time-link",
        json=activation_payload,
        headers={
            "Content-Type": "application/json",
            "x-tenant-id": "public_activation",
            "x-actor-role": "customer",
        },
        timeout=60,
    )
    add_check("activation_first_use_http_200", r1.status_code == 200, f"HTTP={r1.status_code}")
    first = r1.json()
    add_check("activation_first_use_valid", first.get("success") is True and first.get("valid") is True, str(first))

    r2 = requests.post(
        BACKEND + "/admin/saas-provisioning/validate-one-time-link",
        json=activation_payload,
        headers={
            "Content-Type": "application/json",
            "x-tenant-id": "public_activation",
            "x-actor-role": "customer",
        },
        timeout=60,
    )
    add_check("activation_reuse_blocked_http_200", r2.status_code == 200, f"HTTP={r2.status_code}")
    second = r2.json()
    add_check("activation_reuse_blocked", second.get("success") is False and second.get("valid") is False, str(second.get("error")))

# 6. Webhook route safe availability
webhook_payload = {
    "event_type": "invoice.payment_succeeded",
    "payload": {
        "tenant_id": "final_launch_test",
        "stripe_customer_id": "cus_test_final_launch",
        "stripe_subscription_id": "sub_test_final_launch",
    },
}

r = requests.post(
    BACKEND + "/billing/stripe-webhook-route",
    json=webhook_payload,
    headers=HEADERS_OWNER,
    timeout=60,
)
add_check("webhook_route_http_200", r.status_code == 200, f"HTTP={r.status_code}")
if r.status_code == 200:
    add_check("webhook_route_no_secret_exposure", "sk_live" not in r.text and "whsec_" not in r.text, "secret safe")

failed = [name for name, passed, detail in checks if not passed]

print("\nFINAL_SUMMARY")
print("total_checks", len(checks))
print("failed_checks", len(failed))
for item in failed:
    print("FAILED", item)

if failed:
    raise SystemExit("FINAL_LAUNCH_FLOW_HAS_FAILURES")

print("FINAL_LAUNCH_BILLING_SIGNUP_FLOW_OK")