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
    print(json.dumps(response.json(), indent=2)[:12000])

pricing = requests.get(f"{BASE}/client/marketplace/pricing", headers=HEADERS, timeout=30)
show("PRICING", pricing)

workspace = requests.post(
    f"{BASE}/client/marketplace/workspace",
    headers=HEADERS,
    json={
        "tenant_id": "tenant_real_rules",
        "client_number": "CL-REAL-RULES",
        "package": "business",
        "purchased_agents": [
            "marketing_specialist_agent",
            "crm_ai_agent",
            "ugc_creative_agent",
            "product_image_agent",
            "seo_agent",
            "head_agent",
            "orchestration_agent"
        ],
        "active_agents": [
            "marketing_specialist_agent",
            "crm_ai_agent",
            "ugc_creative_agent"
        ]
    },
    timeout=30,
)
show("BUSINESS_WORKSPACE", workspace)

activate_head = requests.post(
    f"{BASE}/admin/marketplace/activate-agent",
    headers=HEADERS,
    json={
        "tenant_id": "tenant_real_rules",
        "package": "business",
        "purchased_agents": ["head_agent"],
        "active_agents": [],
        "agent_id": "head_agent",
    },
    timeout=30,
)
show("BLOCK_HEAD_AGENT_ON_BUSINESS", activate_head)

enterprise_head = requests.post(
    f"{BASE}/admin/marketplace/activate-agent",
    headers=HEADERS,
    json={
        "tenant_id": "tenant_real_rules_enterprise",
        "package": "enterprise",
        "purchased_agents": ["head_agent"],
        "active_agents": [],
        "agent_id": "head_agent",
    },
    timeout=30,
)
show("ALLOW_HEAD_AGENT_ON_ENTERPRISE", enterprise_head)

checkout = requests.post(
    f"{BASE}/billing/checkout-session-payload",
    headers=HEADERS,
    json={
        "tenant_id": "tenant_real_rules_checkout",
        "client_number": "CL-REAL-CHECKOUT",
        "customer_email": "sale@protekepoxy.com.au",
        "target_package": "business",
        "purchased_agents": ["marketing_specialist_agent"],
        "active_agents": ["marketing_specialist_agent"],
    },
    timeout=30,
)
show("BUSINESS_CHECKOUT_PAYLOAD", checkout)

pricing_json = pricing.json()
workspace_json = workspace.json()
activate_head_json = activate_head.json()
enterprise_head_json = enterprise_head.json()
checkout_json = checkout.json()

assert pricing_json["success"] is True
assert pricing_json["currency"] == "USD"
assert pricing_json["packages"]["starter"]["monthly_usd"] == 99
assert pricing_json["packages"]["starter"]["agent_limit"] == 1
assert pricing_json["packages"]["growth"]["monthly_usd"] == 279
assert pricing_json["packages"]["growth"]["agent_limit"] == 3
assert pricing_json["packages"]["business"]["monthly_usd"] == 399
assert pricing_json["packages"]["business"]["agent_limit"] == 5
assert pricing_json["packages"]["enterprise"]["monthly_usd"] is None
assert pricing_json["packages"]["enterprise"]["contact_us_required"] is True

assert workspace_json["success"] is True
assert workspace_json["package_limit"] == 5
catalogue = []
for items in workspace_json["marketplace_by_category"].values():
    catalogue.extend(items)

head = next(a for a in catalogue if a["agent_id"] == "head_agent")
orch = next(a for a in catalogue if a["agent_id"] == "orchestration_agent")
assert head["locked"] is True
assert head["locked_reason"] == "enterprise_only"
assert orch["locked"] is True
assert orch["locked_reason"] == "enterprise_only"

assert activate_head_json["success"] is False
assert activate_head_json["error"] == "enterprise_only_agent"

assert enterprise_head_json["success"] is True
assert enterprise_head_json["status"] == "agent_activated"

assert checkout_json["success"] is True
assert checkout_json["currency"] == "USD"
assert checkout_json["monthly_amount_usd"] == 399
assert checkout_json["target_package"] == "business"

print("\nPRIORITY10_REAL_SUBSCRIPTION_PACKAGE_RULES_OK")
