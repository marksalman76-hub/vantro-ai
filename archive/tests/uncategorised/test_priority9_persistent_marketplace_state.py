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

state_payload = {
    "tenant_id": "tenant_priority9_state_test",
    "client_number": "CL-P9-STATE",
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

upsert = requests.post(f"{BASE}/admin/marketplace/state/upsert", headers=HEADERS, json=state_payload, timeout=30)
show("UPSERT_MARKETPLACE_STATE", upsert)

activate = requests.post(
    f"{BASE}/admin/marketplace/state/action",
    headers=HEADERS,
    json={**state_payload, "action": "activate", "agent_id": "product_image_agent"},
    timeout=30,
)
show("PERSIST_ACTIVATION", activate)

get_state = requests.post(
    f"{BASE}/admin/marketplace/state/get",
    headers=HEADERS,
    json={"tenant_id": "tenant_priority9_state_test"},
    timeout=30,
)
show("GET_MARKETPLACE_STATE", get_state)

downgrade_block = requests.post(
    f"{BASE}/admin/marketplace/downgrade-check",
    headers=HEADERS,
    json={
        "current_package": "growth",
        "target_package": "starter",
        "active_agents": activate.json().get("active_agents", [])
    },
    timeout=30,
)
show("DOWNGRADE_BLOCK_CHECK", downgrade_block)

deactivate = requests.post(
    f"{BASE}/admin/marketplace/state/action",
    headers=HEADERS,
    json={**state_payload, "action": "deactivate", "agent_id": "ugc_creative_agent"},
    timeout=30,
)
show("PERSIST_DEACTIVATION", deactivate)

audit = requests.post(
    f"{BASE}/admin/marketplace/audit-history",
    headers=HEADERS,
    json={"tenant_id": "tenant_priority9_state_test", "limit": 20},
    timeout=30,
)
show("MARKETPLACE_AUDIT_HISTORY", audit)

for response in [upsert, activate, get_state, downgrade_block, deactivate, audit]:
    assert response.status_code == 200

assert upsert.json()["success"] is True
assert upsert.json()["state"]["tenant_id"] == "tenant_priority9_state_test"

assert activate.json()["success"] is True
assert activate.json()["persisted"] is True
assert "product_image_agent" in activate.json()["active_agents"]

state = get_state.json()
assert state["success"] is True
assert state["state"]["tenant_id"] == "tenant_priority9_state_test"
assert "product_image_agent" in state["state"]["active_agents"]
assert state["workspace"]["catalogue_agent_count"] == 27
assert state["secret_exposure"] is False

assert downgrade_block.json()["success"] is True
assert downgrade_block.json()["downgrade_allowed"] is False
assert downgrade_block.json()["agents_to_deactivate_required"] >= 1

assert deactivate.json()["success"] is True
assert deactivate.json()["persisted"] is True
assert "ugc_creative_agent" not in deactivate.json()["active_agents"]

assert audit.json()["success"] is True
assert audit.json()["count"] >= 3
assert audit.json()["secret_exposure"] is False

print("\nPRIORITY9_PERSISTENT_MARKETPLACE_STATE_OK")
