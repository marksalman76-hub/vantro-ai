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

payload = {
    "tenant_id": "tenant_priority9_activation_test",
    "client_number": "CL-P9-ACT",
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

workspace = requests.post(f"{BASE}/client/marketplace/workspace", headers=HEADERS, json=payload, timeout=30)
show("CLIENT_MARKETPLACE_WORKSPACE", workspace)

activate = requests.post(
    f"{BASE}/admin/marketplace/activate-agent",
    headers=HEADERS,
    json={**payload, "agent_id": "product_image_agent"},
    timeout=30,
)
show("ACTIVATE_PURCHASED_AGENT", activate)

blocked = requests.post(
    f"{BASE}/admin/marketplace/activate-agent",
    headers=HEADERS,
    json={**payload, "agent_id": "seo_agent"},
    timeout=30,
)
show("BLOCK_UNPURCHASED_AGENT", blocked)

deactivate = requests.post(
    f"{BASE}/admin/marketplace/deactivate-agent",
    headers=HEADERS,
    json={**payload, "agent_id": "ugc_creative_agent"},
    timeout=30,
)
show("DEACTIVATE_AGENT", deactivate)

upgrade = requests.post(
    f"{BASE}/client/marketplace/upgrade-preview",
    headers=HEADERS,
    json={**payload, "current_package": "growth", "target_package": "professional"},
    timeout=30,
)
show("UPGRADE_PREVIEW", upgrade)

for response in [workspace, activate, blocked, deactivate, upgrade]:
    assert response.status_code == 200

workspace_json = workspace.json()
activate_json = activate.json()
blocked_json = blocked.json()
deactivate_json = deactivate.json()
upgrade_json = upgrade.json()

assert workspace_json["success"] is True
assert workspace_json["catalogue_agent_count"] == 27
assert workspace_json["secret_exposure"] is False
assert workspace_json["entitlement_bypass"] is False
assert "E-commerce Growth" in workspace_json["marketplace_by_category"]

assert activate_json["success"] is True
assert activate_json["status"] == "agent_activated"
assert "product_image_agent" in activate_json["active_agents"]
assert activate_json["package_limit"] == 5

assert blocked_json["success"] is False
assert blocked_json["error"] == "agent_not_purchased"
assert blocked_json["upgrade_required"] is True

assert deactivate_json["success"] is True
assert deactivate_json["status"] == "agent_deactivated"
assert "ugc_creative_agent" not in deactivate_json["active_agents"]

assert upgrade_json["success"] is True
assert upgrade_json["current_package"] == "growth"
assert upgrade_json["target_package"] == "professional"
assert upgrade_json["upgrade_unlocks_more_agents"] is True
assert upgrade_json["client_billing_required_for_upgrade"] is True
assert upgrade_json["secret_exposure"] is False

print("\nPRIORITY9_ACTIVATION_WORKSPACE_RUNTIME_OK")
