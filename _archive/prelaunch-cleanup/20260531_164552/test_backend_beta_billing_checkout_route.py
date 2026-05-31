
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
