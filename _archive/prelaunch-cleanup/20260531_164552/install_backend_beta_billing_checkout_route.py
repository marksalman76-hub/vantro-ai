from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
main_file = ROOT / "backend" / "app" / "main.py"

backup_dir = ROOT / "backups" / f"backend_beta_billing_checkout_route_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)
shutil.copy2(main_file, backup_dir / "main.py")

text = main_file.read_text(encoding="utf-8")

route = r'''

@app.post("/billing-checkout")
def beta_billing_checkout(payload: dict, x_actor_role: str | None = Header(default=None)):
    tenant_id = (
        payload.get("tenant_id")
        or payload.get("tenantId")
        or "client_demo_001"
    )

    plan = str(
        payload.get("plan")
        or payload.get("package_tier")
        or payload.get("package")
        or "starter"
    ).lower()

    if plan not in {"starter", "growth", "business", "enterprise"}:
        plan = "starter"

    billing_cycle = str(
        payload.get("billing_cycle")
        or payload.get("billingCycle")
        or "monthly"
    ).lower()

    if billing_cycle == "annual":
        billing_cycle = "yearly"

    if billing_cycle not in {"monthly", "yearly"}:
        billing_cycle = "monthly"

    success_url = (
        payload.get("success_url")
        or payload.get("successUrl")
        or "https://app.trance-formation.com.au/client/billing/success"
    )

    cancel_url = (
        payload.get("cancel_url")
        or payload.get("cancelUrl")
        or "https://app.trance-formation.com.au/client/billing/cancel"
    )

    price_map = {
        "starter": {
            "monthly": "STRIPE_PRICE_STARTER_MONTHLY",
            "yearly": "STRIPE_PRICE_STARTER_YEARLY",
        },
        "growth": {
            "monthly": "STRIPE_PRICE_GROWTH_MONTHLY",
            "yearly": "STRIPE_PRICE_GROWTH_YEARLY",
        },
        "business": {
            "monthly": "STRIPE_PRICE_BUSINESS_MONTHLY",
            "yearly": "STRIPE_PRICE_BUSINESS_YEARLY",
        },
        "enterprise": {
            "monthly": "STRIPE_PRICE_ENTERPRISE_MONTHLY",
            "yearly": "STRIPE_PRICE_ENTERPRISE_YEARLY",
        },
    }

    selected_price_env = price_map[plan][billing_cycle]

    return {
        "success": True,
        "profile": "backend_beta_billing_checkout_route_v1",
        "checkout_status": "checkout_payload_ready",
        "live_checkout_created": False,
        "stripe_live_required": True,
        "tenant_id": tenant_id,
        "plan": plan,
        "package_tier": plan,
        "billing_cycle": billing_cycle,
        "selected_price_env": selected_price_env,
        "success_url": success_url,
        "cancel_url": cancel_url,
        "next_stage": "connect_live_stripe_checkout_session_creation",
        "message": "Beta checkout payload is ready. Live Stripe checkout session creation requires final Stripe price/env mapping.",
        "customer_safe": True,
        "credential_values_exposed": False,
    }
'''

if '@app.post("/billing-checkout")' not in text:
    text = text.rstrip() + "\n" + route + "\n"

main_file.write_text(text, encoding="utf-8")

test_file = ROOT / "test_backend_beta_billing_checkout_route.py"
test_file.write_text(r'''
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

response = client.post(
    "/billing-checkout",
    json={
        "tenant_id": "client_demo_001",
        "plan": "starter",
        "billing_cycle": "monthly",
        "success_url": "https://app.trance-formation.com.au/client/billing/success",
        "cancel_url": "https://app.trance-formation.com.au/client/billing/cancel",
    },
)

assert response.status_code == 200
body = response.json()

assert body["success"] is True
assert body["profile"] == "backend_beta_billing_checkout_route_v1"
assert body["tenant_id"] == "client_demo_001"
assert body["plan"] == "starter"
assert body["billing_cycle"] == "monthly"
assert body["selected_price_env"] == "STRIPE_PRICE_STARTER_MONTHLY"
assert body["credential_values_exposed"] is False
assert body["customer_safe"] is True

print("BACKEND_BETA_BILLING_CHECKOUT_ROUTE_TEST_PASSED")
''', encoding="utf-8")

print("BACKEND_BETA_BILLING_CHECKOUT_ROUTE_INSTALLED")
print(f"Backup: {backup_dir}")
print(f"Updated: {main_file}")
print(f"Created: {test_file}")