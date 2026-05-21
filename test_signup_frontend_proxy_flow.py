import requests

FRONTEND = "http://localhost:3000"

payload = {
    "customer_email": "frontend-proxy-growth@example.com",
    "target_package": "growth",
    "selected_agents": ["marketing_specialist_agent", "seo_agent", "email_reply_agent"],
}

r = requests.post(
    f"{FRONTEND}/api/billing-checkout",
    json=payload,
    headers={"Content-Type": "application/json"},
    timeout=60,
)

print("CHECKOUT_PROXY_HTTP", r.status_code)
print(r.text[:3000])

data = r.json()

print("success", data.get("success"))
print("mode", data.get("mode"))
print("live_stripe_ready", data.get("live_stripe_ready"))
print("checkout_session_created", data.get("checkout_session_created"))
print("secret_exposure", data.get("secret_exposure"))

if not data.get("success"):
    raise SystemExit("FRONTEND_CHECKOUT_PROXY_FAILED")

print("FRONTEND_SIGNUP_CHECKOUT_PROXY_OK")