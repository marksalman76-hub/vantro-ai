import json
import requests

BASE = "http://127.0.0.1:8000"
HEADERS = {
    "x-actor-role": "admin",
    "x-tenant-id": "owner",
    "Content-Type": "application/json",
}

def show(label, response):
    print("\n" + "=" * 80)
    print(label)
    print("HTTP", response.status_code)
    try:
        print(json.dumps(response.json(), indent=2)[:12000])
    except Exception:
        print(response.text[:12000])

base_payload = {
    "tenant_id": "tenant_priority9_commercial_test",
    "client_number": "CL-P9-COMMERCIAL",
    "current_package": "growth",
    "target_package": "business",
    "purchased_agents": [
        "head_agent",
        "marketing_specialist_agent",
        "crm_ai_agent",
        "ugc_creative_agent",
        "product_image_agent"
    ],
    "active_agents": [
        "head_agent",
        "marketing_specialist_agent",
        "ugc_creative_agent",
        "product_image_agent"
    ],
}

pricing = requests.get(f"{BASE}/client/marketplace/pricing", headers=HEADERS, timeout=30)
show("PRICING_CATALOGUE", pricing)

purchase = requests.post(
    f"{BASE}/client/marketplace/purchase-flow",
    headers=HEADERS,
    json=base_payload,
    timeout=30,
)
show("PURCHASE_FLOW", purchase)

upgrade_request = requests.post(
    f"{BASE}/admin/marketplace/entitlement-change/request",
    headers=HEADERS,
    json={**base_payload, "change_type": "upgrade"},
    timeout=30,
)
show("UPGRADE_CHANGE_REQUEST", upgrade_request)

apply_after_billing = requests.post(
    f"{BASE}/admin/marketplace/entitlement-change/apply-after-billing",
    headers=HEADERS,
    json={**base_payload, "target_package": "business", "billing_status": "paid"},
    timeout=30,
)
show("APPLY_AFTER_BILLING", apply_after_billing)

downgrade_request = requests.post(
    f"{BASE}/admin/marketplace/entitlement-change/request",
    headers=HEADERS,
    json={**base_payload, "change_type": "downgrade", "target_package": "starter"},
    timeout=30,
)
show("DOWNGRADE_CHANGE_REQUEST", downgrade_request)

summary = requests.post(
    f"{BASE}/admin/marketplace/commercial-summary",
    headers=HEADERS,
    json={"tenant_id": "tenant_priority9_commercial_test"},
    timeout=30,
)
show("COMMERCIAL_SUMMARY", summary)

for response in [pricing, purchase, upgrade_request, apply_after_billing, downgrade_request, summary]:
    assert response.status_code == 200

pricing_json = pricing.json()
purchase_json = purchase.json()
upgrade_json = upgrade_request.json()
apply_json = apply_after_billing.json()
downgrade_json = downgrade_request.json()
summary_json = summary.json()

assert pricing_json["success"] is True
assert pricing_json["packages"]["growth"]["monthly_aud"] == 997
assert pricing_json["month_to_month"] is True

assert purchase_json["success"] is True
assert purchase_json["checkout_required"] is True
assert purchase_json["target_package"] == "business"
assert purchase_json["billing_required"] is True
assert purchase_json["secret_exposure"] is False

assert upgrade_json["success"] is True
assert upgrade_json["change_type"] == "upgrade"
assert upgrade_json["status"] == "ready_for_checkout"
assert upgrade_json["checkout_required"] is True

assert apply_json["success"] is True
assert apply_json["package"] == "business"
assert apply_json["billing_status"] == "paid"
assert apply_json["state"]["package"] == "business"

assert downgrade_json["success"] is True
assert downgrade_json["change_type"] == "downgrade"
assert downgrade_json["status"] == "blocked_requires_agent_deactivation"
assert downgrade_json["downgrade_check"]["blocked"] is True

assert summary_json["success"] is True
assert summary_json["event_count"] >= 3
assert summary_json["secret_exposure"] is False

print("\nPRIORITY9_COMMERCIAL_MARKETPLACE_BRIDGE_OK")
