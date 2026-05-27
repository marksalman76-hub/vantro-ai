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

payload = {
    "tenant_id": "tenant_priority9_test",
    "client_number": "CL-PRIORITY9",
    "package": "growth",
    "purchased_agents": [
        "head_agent",
        "marketing_specialist_agent",
        "crm_ai_agent"
    ],
    "active_agents": [
        "head_agent",
        "marketing_specialist_agent"
    ]
}

response = requests.post(
    f"{BASE}/admin/marketplace/entitlement-summary",
    headers=HEADERS,
    json=payload,
    timeout=30,
)
show("MARKETPLACE_ENTITLEMENT_SUMMARY", response)

data = response.json()

assert response.status_code == 200
assert data["success"] is True
assert data["package"] == "growth"
assert data["package_limit"] == 5
assert data["catalogue_agent_count"] >= 20
assert data["active_agent_count"] == 2
assert data["purchased_agent_count"] == 3

catalogue = data["marketplace_catalogue"]

head = next(a for a in catalogue if a["agent_id"] == "head_agent")
crm = next(a for a in catalogue if a["agent_id"] == "crm_ai_agent")
seo = next(a for a in catalogue if a["agent_id"] == "seo_agent")

assert head["active"] is True
assert head["purchased"] is True
assert crm["purchased"] is True
assert crm["active"] is False
assert crm["available_to_activate"] is True
assert seo["purchased"] is False
assert seo["locked"] is True
assert seo["locked_reason"] == "not_purchased"

assert data["client_access_limited_to_paid_agents"] is True
assert data["internal_config_hidden_from_client"] is True
assert data["secret_exposure"] is False
assert data["entitlement_bypass"] is False
assert data["governance_bypass"] is False

print("\nPRIORITY9_MARKETPLACE_ENTITLEMENT_SUMMARY_OK")
