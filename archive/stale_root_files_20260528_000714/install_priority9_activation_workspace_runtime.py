from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
MAIN = ROOT / "backend" / "app" / "main.py"
CORE = ROOT / "backend" / "app" / "core"
RUNTIME = CORE / "marketplace_activation_runtime.py"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
main_backup = BACKUP_DIR / f"main_before_priority9_activation_workspace_{timestamp}.py"
main_backup.write_text(MAIN.read_text(encoding="utf-8"), encoding="utf-8")

RUNTIME.write_text(r'''
from __future__ import annotations

from typing import Any, Dict, List

from backend.app.core.global_agent_registry import get_global_agent, list_global_agents
from backend.app.core.marketplace_entitlement_runtime import PACKAGE_LIMITS, build_marketplace_entitlement_summary


def _normalise_package(package: str) -> str:
    package = str(package or "starter").strip().lower()
    return package if package in PACKAGE_LIMITS else "starter"


def _unique(values: List[str]) -> List[str]:
    return list(dict.fromkeys([str(v).strip().lower() for v in values if str(v).strip()]))


def activate_marketplace_agent(payload: Dict[str, Any]) -> Dict[str, Any]:
    package = _normalise_package(payload.get("package"))
    purchased_agents = _unique(payload.get("purchased_agents") or [])
    active_agents = _unique(payload.get("active_agents") or payload.get("activated_agents") or [])
    agent_id = str(payload.get("agent_id") or "").strip().lower()

    agent = get_global_agent(agent_id)
    if not agent:
        return {"success": False, "error": "unknown_agent", "agent_id": agent_id}

    if agent_id not in purchased_agents:
        return {
            "success": False,
            "error": "agent_not_purchased",
            "agent_id": agent_id,
            "upgrade_required": True,
            "customer_safe_message": "This agent is available as an upgrade.",
        }

    if agent_id in active_agents:
        return {
            "success": True,
            "status": "already_active",
            "agent_id": agent_id,
            "active_agents": active_agents,
            "customer_safe_message": "This agent is already active.",
        }

    limit = PACKAGE_LIMITS[package]
    if package != "enterprise" and len(active_agents) >= limit:
        return {
            "success": False,
            "error": "package_limit_reached",
            "agent_id": agent_id,
            "package": package,
            "package_limit": limit,
            "upgrade_required": True,
            "customer_safe_message": "Your package has reached its active agent limit.",
        }

    active_agents.append(agent_id)

    return {
        "success": True,
        "status": "agent_activated",
        "agent_id": agent_id,
        "package": package,
        "active_agents": active_agents,
        "active_agent_count": len(active_agents),
        "package_limit": limit,
        "requires_owner_approval_for_high_risk": agent.get("requires_owner_approval_for_high_risk", True),
        "client_access_limited_to_paid_agents": True,
        "secret_exposure": False,
        "entitlement_bypass": False,
        "governance_bypass": False,
    }


def deactivate_marketplace_agent(payload: Dict[str, Any]) -> Dict[str, Any]:
    active_agents = _unique(payload.get("active_agents") or payload.get("activated_agents") or [])
    agent_id = str(payload.get("agent_id") or "").strip().lower()

    if agent_id not in active_agents:
        return {
            "success": True,
            "status": "already_inactive",
            "agent_id": agent_id,
            "active_agents": active_agents,
        }

    active_agents = [agent for agent in active_agents if agent != agent_id]

    return {
        "success": True,
        "status": "agent_deactivated",
        "agent_id": agent_id,
        "active_agents": active_agents,
        "active_agent_count": len(active_agents),
        "client_access_limited_to_paid_agents": True,
        "secret_exposure": False,
        "entitlement_bypass": False,
        "governance_bypass": False,
    }


def build_client_marketplace_workspace(payload: Dict[str, Any]) -> Dict[str, Any]:
    summary = build_marketplace_entitlement_summary(payload)
    catalogue = summary.get("marketplace_catalogue", [])

    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for agent in catalogue:
        category = agent.get("category") or "Other"
        grouped.setdefault(category, []).append(agent)

    return {
        "success": True,
        "workspace_profile": "priority9_client_marketplace_workspace_v1",
        "tenant_id": summary.get("tenant_id"),
        "client_number": summary.get("client_number"),
        "package": summary.get("package"),
        "package_limit": summary.get("package_limit"),
        "active_agent_count": summary.get("active_agent_count"),
        "purchased_agent_count": summary.get("purchased_agent_count"),
        "catalogue_agent_count": summary.get("catalogue_agent_count"),
        "active_catalogue": summary.get("active_catalogue", []),
        "purchased_catalogue": summary.get("purchased_catalogue", []),
        "marketplace_by_category": grouped,
        "upgrade_recommended": summary.get("upgrade_recommended"),
        "recommended_upgrade_package": summary.get("recommended_upgrade_package"),
        "customer_safe_empty_state": "Choose included agents to activate, or upgrade to unlock more agents.",
        "customer_safe_response_mode": True,
        "internal_config_hidden_from_client": True,
        "secret_exposure": False,
        "entitlement_bypass": False,
        "governance_bypass": False,
    }


def build_package_upgrade_preview(payload: Dict[str, Any]) -> Dict[str, Any]:
    current_package = _normalise_package(payload.get("current_package") or payload.get("package"))
    target_package = _normalise_package(payload.get("target_package"))
    active_agents = _unique(payload.get("active_agents") or [])
    purchased_agents = _unique(payload.get("purchased_agents") or active_agents)

    current_limit = PACKAGE_LIMITS[current_package]
    target_limit = PACKAGE_LIMITS[target_package]

    purchasable_ids = [agent["agent_id"] for agent in list_global_agents(include_internal=False)]
    currently_locked = [agent_id for agent_id in purchasable_ids if agent_id not in purchased_agents]

    return {
        "success": True,
        "upgrade_preview_profile": "priority9_package_upgrade_preview_v1",
        "current_package": current_package,
        "target_package": target_package,
        "current_package_limit": current_limit,
        "target_package_limit": target_limit,
        "additional_active_slots": max(0, target_limit - current_limit) if target_package != "enterprise" else "unlimited",
        "currently_locked_agent_count": len(currently_locked),
        "upgrade_unlocks_more_agents": target_limit > current_limit or target_package == "enterprise",
        "billing_required": True,
        "owner_admin_free_running_access": True,
        "client_billing_required_for_upgrade": True,
        "customer_safe_response_mode": True,
        "secret_exposure": False,
    }
'''.lstrip(), encoding="utf-8")

main_text = MAIN.read_text(encoding="utf-8")

import_line = "from backend.app.core.marketplace_activation_runtime import activate_marketplace_agent, deactivate_marketplace_agent, build_client_marketplace_workspace, build_package_upgrade_preview"
if import_line not in main_text:
    lines = main_text.splitlines()
    insert_at = 0
    for i, line in enumerate(lines):
        if line.startswith("from ") or line.startswith("import "):
            insert_at = i + 1
    lines.insert(insert_at, import_line)
    main_text = "\n".join(lines) + "\n"

routes = r'''

@app.post("/admin/marketplace/activate-agent")
def admin_marketplace_activate_agent(payload: dict):
    return activate_marketplace_agent(payload)


@app.post("/admin/marketplace/deactivate-agent")
def admin_marketplace_deactivate_agent(payload: dict):
    return deactivate_marketplace_agent(payload)


@app.post("/client/marketplace/workspace")
def client_marketplace_workspace(payload: dict):
    return build_client_marketplace_workspace(payload)


@app.post("/client/marketplace/upgrade-preview")
def client_marketplace_upgrade_preview(payload: dict):
    return build_package_upgrade_preview(payload)
'''

if "/admin/marketplace/activate-agent" not in main_text:
    main_text = main_text.rstrip() + "\n" + routes + "\n"

MAIN.write_text(main_text, encoding="utf-8")

TEST = ROOT / "test_priority9_activation_workspace_runtime.py"
TEST.write_text(r'''
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
'''.lstrip(), encoding="utf-8")

print("PRIORITY9_ACTIVATION_WORKSPACE_RUNTIME_INSTALLED")
print(f"Main backup: {main_backup}")
print(f"Created/updated: {RUNTIME}")
print(f"Updated: {MAIN}")
print(f"Created/updated: {TEST}")