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
        print(json.dumps(response.json(), indent=2)[:14000])
    except Exception:
        print(response.text[:14000])

registry = requests.get(
    f"{BASE}/admin/agents/global-registry",
    headers=HEADERS,
    timeout=30,
)
show("GLOBAL_AGENT_REGISTRY", registry)

payload = {
    "tenant_id": "tenant_priority9_registry_test",
    "client_number": "CL-P9-REGISTRY",
    "package": "growth",
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
        "ugc_creative_agent"
    ]
}

marketplace = requests.post(
    f"{BASE}/admin/marketplace/entitlement-summary",
    headers=HEADERS,
    json=payload,
    timeout=30,
)
show("MARKETPLACE_ENTITLEMENT_SUMMARY_GLOBAL_REGISTRY", marketplace)

registry_json = registry.json()
marketplace_json = marketplace.json()

assert registry.status_code == 200
assert registry_json["success"] is True
assert registry_json["registry_profile"] == "global_agent_registry_v27"
assert registry_json["agent_count"] == 27
assert registry_json["purchasable_count"] == 27
assert registry_json["client_visible_count"] == 27

ids = [a["agent_id"] for a in registry_json["agents"]]
required = [
    "head_agent",
    "marketing_specialist_agent",
    "crm_ai_agent",
    "ugc_creative_agent",
    "analytics_optimisation_agent",
    "product_research_agent",
    "ad_creative_agent",
    "product_image_agent",
    "influencer_collaboration_agent",
]
for agent_id in required:
    assert agent_id in ids, f"missing required agent: {agent_id}"

assert marketplace.status_code == 200
assert marketplace_json["success"] is True
assert marketplace_json["registry_profile"] == "global_agent_registry_v27"
assert marketplace_json["catalogue_agent_count"] == 27
assert marketplace_json["package"] == "growth"
assert marketplace_json["package_limit"] == 5

catalogue = marketplace_json["marketplace_catalogue"]
ugc = next(a for a in catalogue if a["agent_id"] == "ugc_creative_agent")
product_image = next(a for a in catalogue if a["agent_id"] == "product_image_agent")
seo = next(a for a in catalogue if a["agent_id"] == "seo_agent")

assert ugc["active"] is True
assert ugc["purchased"] is True
assert product_image["purchased"] is True
assert product_image["active"] is False
assert product_image["available_to_activate"] is True
assert seo["purchased"] is False
assert seo["locked"] is True
assert seo["locked_reason"] == "not_purchased"

assert marketplace_json["client_access_limited_to_paid_agents"] is True
assert marketplace_json["internal_config_hidden_from_client"] is True
assert marketplace_json["secret_exposure"] is False
assert marketplace_json["entitlement_bypass"] is False
assert marketplace_json["governance_bypass"] is False

print("\nPRIORITY9_GLOBAL_AGENT_REGISTRY_27_OK")
