from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
main_file = ROOT / "backend" / "app" / "main.py"

backup_dir = ROOT / "backups" / f"real_stripe_checkout_session_bridge_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)
shutil.copy2(main_file, backup_dir / "main.py")

text = main_file.read_text(encoding="utf-8")

route_start = text.find('@app.post("/billing-checkout")')
if route_start == -1:
    raise SystemExit("BILLING_CHECKOUT_ROUTE_NOT_FOUND")

next_route = text.find("\n@app.", route_start + 1)
if next_route == -1:
    next_route = len(text)

new_route = r'''
@app.post("/billing-checkout")
def beta_billing_checkout(payload: dict, x_actor_role: str | None = Header(default=None)):
    import os

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

    price_env_map = {
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

    selected_price_env = price_env_map[plan][billing_cycle]
    stripe_secret_key = os.getenv("STRIPE_SECRET_KEY", "").strip()
    stripe_price_id = os.getenv(selected_price_env, "").strip()

    base_payload = {
        "tenant_id": tenant_id,
        "plan": plan,
        "package_tier": plan,
        "billing_cycle": billing_cycle,
        "selected_price_env": selected_price_env,
        "success_url": success_url,
        "cancel_url": cancel_url,
        "customer_safe": True,
        "credential_values_exposed": False,
    }

    if not stripe_secret_key or not stripe_price_id:
        return {
            "success": True,
            "profile": "real_stripe_checkout_session_bridge_v1",
            "checkout_status": "checkout_payload_ready",
            "live_checkout_created": False,
            "stripe_live_required": True,
            "missing_configuration": {
                "stripe_secret_key_configured": bool(stripe_secret_key),
                "stripe_price_id_configured": bool(stripe_price_id),
                "missing_price_env": selected_price_env if not stripe_price_id else None,
            },
            "next_stage": "configure_stripe_secret_and_price_ids",
            "message": "Checkout payload is ready. Configure Stripe secret key and selected price ID to create live checkout sessions.",
            **base_payload,
        }

    try:
        import stripe
    except Exception:
        return {
            "success": True,
            "profile": "real_stripe_checkout_session_bridge_v1",
            "checkout_status": "stripe_library_missing",
            "live_checkout_created": False,
            "stripe_live_required": True,
            "next_stage": "install_stripe_python_package",
            "message": "Stripe credentials are configured, but the stripe Python package is not installed in the backend runtime.",
            **base_payload,
        }

    try:
        stripe.api_key = stripe_secret_key

        session = stripe.checkout.Session.create(
            mode="subscription",
            line_items=[
                {
                    "price": stripe_price_id,
                    "quantity": 1,
                }
            ],
            success_url=success_url,
            cancel_url=cancel_url,
            client_reference_id=str(tenant_id),
            metadata={
                "tenant_id": str(tenant_id),
                "plan": plan,
                "package_tier": plan,
                "billing_cycle": billing_cycle,
                "source": "ecommerce_ai_agent_platform",
            },
        )

        return {
            "success": True,
            "profile": "real_stripe_checkout_session_bridge_v1",
            "checkout_status": "live_checkout_session_created",
            "live_checkout_created": True,
            "checkout_session_id": session.get("id"),
            "checkout_url": session.get("url"),
            "stripe_price_env": selected_price_env,
            "stripe_price_id_present": True,
            "next_stage": "redirect_customer_to_checkout_url",
            **base_payload,
        }

    except Exception as exc:
        return {
            "success": False,
            "profile": "real_stripe_checkout_session_bridge_v1",
            "checkout_status": "stripe_checkout_creation_failed",
            "live_checkout_created": False,
            "error": str(exc)[:500],
            "stripe_price_env": selected_price_env,
            "stripe_price_id_present": True,
            "customer_safe": True,
            "credential_values_exposed": False,
            **base_payload,
        }
'''

text = text[:route_start] + new_route + "\n" + text[next_route:]
main_file.write_text(text, encoding="utf-8")

test_file = ROOT / "test_real_stripe_checkout_session_bridge.py"
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
assert body["profile"] == "real_stripe_checkout_session_bridge_v1"
assert body["tenant_id"] == "client_demo_001"
assert body["plan"] == "starter"
assert body["billing_cycle"] == "monthly"
assert body["selected_price_env"] == "STRIPE_PRICE_STARTER_MONTHLY"
assert body["credential_values_exposed"] is False
assert body["customer_safe"] is True
assert body["checkout_status"] in {
    "checkout_payload_ready",
    "stripe_library_missing",
    "live_checkout_session_created",
}

print("REAL_STRIPE_CHECKOUT_SESSION_BRIDGE_TEST_PASSED")
''', encoding="utf-8")

print("REAL_STRIPE_CHECKOUT_SESSION_BRIDGE_INSTALLED")
print(f"Backup: {backup_dir}")
print(f"Updated: {main_file}")
print(f"Created: {test_file}")