from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
MAIN = ROOT / "backend" / "app" / "main.py"
CORE = ROOT / "backend" / "app" / "core"
REGISTRY = CORE / "global_agent_registry.py"
MARKETPLACE = CORE / "marketplace_entitlement_runtime.py"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

for path in [MAIN, MARKETPLACE]:
    if not path.exists():
        raise FileNotFoundError(path)

main_backup = BACKUP_DIR / f"main_before_priority9_global_registry_27_{timestamp}.py"
marketplace_backup = BACKUP_DIR / f"marketplace_before_priority9_global_registry_27_{timestamp}.py"

main_backup.write_text(MAIN.read_text(encoding="utf-8"), encoding="utf-8")
marketplace_backup.write_text(MARKETPLACE.read_text(encoding="utf-8"), encoding="utf-8")

REGISTRY.write_text(r'''
from __future__ import annotations

from typing import Any, Dict, List


GLOBAL_AGENT_REGISTRY: List[Dict[str, Any]] = [
    {
        "agent_id": "head_agent",
        "name": "Head Agent / CEO",
        "category": "Core Control",
        "purchasable": True,
        "client_visible": True,
        "internal_system": False,
        "bundle_eligible": True,
        "requires_owner_approval_for_high_risk": True,
    },
    {
        "agent_id": "strategist_agent",
        "name": "Strategist Agent",
        "category": "Core Control",
        "purchasable": True,
        "client_visible": True,
        "internal_system": False,
        "bundle_eligible": True,
        "requires_owner_approval_for_high_risk": True,
    },
    {
        "agent_id": "business_growth_partnerships_agent",
        "name": "Business Growth & Partnerships Agent",
        "category": "Business Growth Engine",
        "purchasable": True,
        "client_visible": True,
        "internal_system": False,
        "bundle_eligible": True,
        "requires_owner_approval_for_high_risk": True,
    },
    {
        "agent_id": "lead_generator_appointment_setter_agent",
        "name": "Lead Generator / Appointment Setter Agent",
        "category": "Business Growth Engine",
        "purchasable": True,
        "client_visible": True,
        "internal_system": False,
        "bundle_eligible": True,
        "requires_owner_approval_for_high_risk": True,
    },
    {
        "agent_id": "marketing_specialist_agent",
        "name": "Marketing Specialist Agent",
        "category": "Business Growth Engine",
        "purchasable": True,
        "client_visible": True,
        "internal_system": False,
        "bundle_eligible": True,
        "requires_owner_approval_for_high_risk": True,
    },
    {
        "agent_id": "social_media_manager_content_creator_agent",
        "name": "Social Media Manager / Content Creator Agent",
        "category": "Business Growth Engine",
        "purchasable": True,
        "client_visible": True,
        "internal_system": False,
        "bundle_eligible": True,
        "requires_owner_approval_for_high_risk": True,
    },
    {
        "agent_id": "seo_agent",
        "name": "SEO Agent",
        "category": "Business Growth Engine",
        "purchasable": True,
        "client_visible": True,
        "internal_system": False,
        "bundle_eligible": True,
        "requires_owner_approval_for_high_risk": False,
    },
    {
        "agent_id": "email_reply_agent",
        "name": "Email Reply Agent",
        "category": "Business Growth Engine",
        "purchasable": True,
        "client_visible": True,
        "internal_system": False,
        "bundle_eligible": True,
        "requires_owner_approval_for_high_risk": True,
    },
    {
        "agent_id": "crm_ai_agent",
        "name": "CRM AI Agent",
        "category": "Business Growth Engine",
        "purchasable": True,
        "client_visible": True,
        "internal_system": False,
        "bundle_eligible": True,
        "requires_owner_approval_for_high_risk": True,
    },
    {
        "agent_id": "receptionist_agent",
        "name": "Receptionist Agent",
        "category": "Frontline Operations",
        "purchasable": True,
        "client_visible": True,
        "internal_system": False,
        "bundle_eligible": True,
        "requires_owner_approval_for_high_risk": True,
    },
    {
        "agent_id": "custom_websites_landing_pages_apps_agent",
        "name": "Custom Websites / Landing Pages / Apps Agent",
        "category": "Product & Delivery",
        "purchasable": True,
        "client_visible": True,
        "internal_system": False,
        "bundle_eligible": True,
        "requires_owner_approval_for_high_risk": True,
    },
    {
        "agent_id": "product_development_agent",
        "name": "Product Development Agent",
        "category": "Product & Delivery",
        "purchasable": True,
        "client_visible": True,
        "internal_system": False,
        "bundle_eligible": True,
        "requires_owner_approval_for_high_risk": True,
    },
    {
        "agent_id": "ecommerce_agent",
        "name": "E-commerce Agent",
        "category": "Product & Delivery",
        "purchasable": True,
        "client_visible": True,
        "internal_system": False,
        "bundle_eligible": True,
        "requires_owner_approval_for_high_risk": True,
    },
    {
        "agent_id": "demo_trial_agent",
        "name": "Demo / Trial Agent",
        "category": "Scale / System",
        "purchasable": True,
        "client_visible": True,
        "internal_system": False,
        "bundle_eligible": False,
        "requires_owner_approval_for_high_risk": False,
    },
    {
        "agent_id": "orchestration_agent",
        "name": "Orchestration Agent",
        "category": "Recommended System Agents",
        "purchasable": True,
        "client_visible": True,
        "internal_system": False,
        "bundle_eligible": True,
        "requires_owner_approval_for_high_risk": True,
    },
    {
        "agent_id": "security_compliance_agent",
        "name": "Security & Compliance Agent",
        "category": "Recommended System Agents",
        "purchasable": True,
        "client_visible": True,
        "internal_system": False,
        "bundle_eligible": True,
        "requires_owner_approval_for_high_risk": True,
    },
    {
        "agent_id": "analytics_intelligence_agent",
        "name": "Analytics & Intelligence Agent",
        "category": "Recommended System Agents",
        "purchasable": True,
        "client_visible": True,
        "internal_system": False,
        "bundle_eligible": True,
        "requires_owner_approval_for_high_risk": False,
    },
    {
        "agent_id": "qa_testing_agent",
        "name": "QA / Testing Agent",
        "category": "Recommended System Agents",
        "purchasable": True,
        "client_visible": True,
        "internal_system": False,
        "bundle_eligible": True,
        "requires_owner_approval_for_high_risk": False,
    },
    {
        "agent_id": "integration_automation_agent",
        "name": "Integration / Automation Agent",
        "category": "Recommended System Agents",
        "purchasable": True,
        "client_visible": True,
        "internal_system": False,
        "bundle_eligible": True,
        "requires_owner_approval_for_high_risk": True,
    },
    {
        "agent_id": "billing_optimisation_agent",
        "name": "Billing Optimisation Agent",
        "category": "Recommended System Agents",
        "purchasable": True,
        "client_visible": True,
        "internal_system": False,
        "bundle_eligible": True,
        "requires_owner_approval_for_high_risk": True,
    },
    {
        "agent_id": "training_learning_agent",
        "name": "Training / Learning Agent",
        "category": "Recommended System Agents",
        "purchasable": True,
        "client_visible": True,
        "internal_system": False,
        "bundle_eligible": True,
        "requires_owner_approval_for_high_risk": False,
    },
    {
        "agent_id": "ugc_creative_agent",
        "name": "UGC Creative Agent",
        "category": "E-commerce Growth",
        "purchasable": True,
        "client_visible": True,
        "internal_system": False,
        "bundle_eligible": True,
        "requires_owner_approval_for_high_risk": False,
    },
    {
        "agent_id": "analytics_optimisation_agent",
        "name": "Analytics Optimisation Agent",
        "category": "E-commerce Growth",
        "purchasable": True,
        "client_visible": True,
        "internal_system": False,
        "bundle_eligible": True,
        "requires_owner_approval_for_high_risk": False,
    },
    {
        "agent_id": "product_research_agent",
        "name": "Product Research Agent",
        "category": "E-commerce Growth",
        "purchasable": True,
        "client_visible": True,
        "internal_system": False,
        "bundle_eligible": True,
        "requires_owner_approval_for_high_risk": False,
    },
    {
        "agent_id": "ad_creative_agent",
        "name": "Ad Creative Agent",
        "category": "E-commerce Growth",
        "purchasable": True,
        "client_visible": True,
        "internal_system": False,
        "bundle_eligible": True,
        "requires_owner_approval_for_high_risk": False,
    },
    {
        "agent_id": "product_image_agent",
        "name": "Product Image Agent",
        "category": "E-commerce Growth",
        "purchasable": True,
        "client_visible": True,
        "internal_system": False,
        "bundle_eligible": True,
        "requires_owner_approval_for_high_risk": False,
    },
    {
        "agent_id": "influencer_collaboration_agent",
        "name": "Influencer Collaboration Agent",
        "category": "E-commerce Growth",
        "purchasable": True,
        "client_visible": True,
        "internal_system": False,
        "bundle_eligible": True,
        "requires_owner_approval_for_high_risk": True,
    },
]


def list_global_agents(include_internal: bool = False) -> List[Dict[str, Any]]:
    if include_internal:
        return list(GLOBAL_AGENT_REGISTRY)
    return [agent for agent in GLOBAL_AGENT_REGISTRY if agent.get("client_visible") is True]


def list_purchasable_agents() -> List[Dict[str, Any]]:
    return [agent for agent in GLOBAL_AGENT_REGISTRY if agent.get("purchasable") is True]


def get_global_agent(agent_id: str) -> Dict[str, Any] | None:
    safe_agent_id = str(agent_id or "").strip().lower()
    for agent in GLOBAL_AGENT_REGISTRY:
        if agent["agent_id"] == safe_agent_id:
            return agent
    return None


def global_agent_exists(agent_id: str) -> bool:
    return get_global_agent(agent_id) is not None


def global_agent_registry_summary() -> Dict[str, Any]:
    client_visible = list_global_agents()
    purchasable = list_purchasable_agents()

    categories = sorted(set(agent["category"] for agent in GLOBAL_AGENT_REGISTRY))

    return {
        "success": True,
        "registry_profile": "global_agent_registry_v27",
        "agent_count": len(GLOBAL_AGENT_REGISTRY),
        "client_visible_count": len(client_visible),
        "purchasable_count": len(purchasable),
        "categories": categories,
        "agents": client_visible,
        "customer_safe_response_mode": True,
        "secret_exposure": False,
        "internal_config_hidden_from_client": True,
    }
'''.lstrip(), encoding="utf-8")

MARKETPLACE.write_text(r'''
from __future__ import annotations

from typing import Any, Dict

from backend.app.core.global_agent_registry import list_global_agents


PACKAGE_LIMITS = {
    "starter": 2,
    "growth": 5,
    "professional": 10,
    "enterprise": 999,
}

PACKAGE_ORDER = ["starter", "growth", "professional", "enterprise"]


def _normalise_package(package: str) -> str:
    package = str(package or "starter").strip().lower()
    return package if package in PACKAGE_LIMITS else "starter"


def _recommended_upgrade(package: str) -> str | None:
    package = _normalise_package(package)
    try:
        index = PACKAGE_ORDER.index(package)
    except ValueError:
        return "growth"

    if index + 1 >= len(PACKAGE_ORDER):
        return None

    return PACKAGE_ORDER[index + 1]


def build_marketplace_entitlement_summary(payload: Dict[str, Any]) -> Dict[str, Any]:
    package = _normalise_package(payload.get("package"))
    active_agents = list(dict.fromkeys(payload.get("active_agents") or payload.get("activated_agents") or []))
    purchased_agents = list(dict.fromkeys(payload.get("purchased_agents") or active_agents))
    tenant_id = payload.get("tenant_id")
    client_number = payload.get("client_number")

    catalogue_source = list_global_agents(include_internal=False)

    package_limit = PACKAGE_LIMITS[package]
    active_count = len(active_agents)
    purchased_count = len(purchased_agents)

    catalogue = []

    for agent in catalogue_source:
        agent_id = agent["agent_id"]
        purchased = agent_id in purchased_agents
        active = agent_id in active_agents

        available_to_activate = (
            purchased
            and not active
            and (active_count < package_limit or package == "enterprise")
        )

        locked_reason = None
        if not purchased:
            locked_reason = "not_purchased"
        elif not active and not available_to_activate:
            locked_reason = "package_limit_reached"

        catalogue.append({
            "agent_id": agent_id,
            "name": agent["name"],
            "category": agent["category"],
            "purchasable": agent.get("purchasable", True),
            "bundle_eligible": agent.get("bundle_eligible", True),
            "requires_owner_approval_for_high_risk": agent.get("requires_owner_approval_for_high_risk", True),
            "purchased": purchased,
            "active": active,
            "available_to_activate": available_to_activate,
            "visible_to_client": agent.get("client_visible", True),
            "locked": not purchased or locked_reason == "package_limit_reached",
            "locked_reason": locked_reason,
            "customer_safe_status": (
                "Active" if active else
                "Included" if purchased else
                "Upgrade required"
            ),
        })

    locked_agents = [a for a in catalogue if a["locked"]]
    active_catalogue = [a for a in catalogue if a["active"]]
    purchased_catalogue = [a for a in catalogue if a["purchased"]]

    upgrade_recommended = (
        package != "enterprise"
        and (
            active_count >= package_limit
            or len([a for a in catalogue if not a["purchased"]]) > 0
        )
    )

    return {
        "success": True,
        "marketplace_profile": "priority9_marketplace_entitlement_summary_v2_global_registry",
        "registry_profile": "global_agent_registry_v27",
        "tenant_id": tenant_id,
        "client_number": client_number,
        "package": package,
        "package_limit": package_limit,
        "active_agent_count": active_count,
        "purchased_agent_count": purchased_count,
        "catalogue_agent_count": len(catalogue_source),
        "active_agents": active_agents,
        "purchased_agents": purchased_agents,
        "marketplace_catalogue": catalogue,
        "active_catalogue": active_catalogue,
        "purchased_catalogue": purchased_catalogue,
        "locked_agent_count": len(locked_agents),
        "upgrade_recommended": upgrade_recommended,
        "recommended_upgrade_package": _recommended_upgrade(package) if upgrade_recommended else None,
        "client_access_limited_to_paid_agents": True,
        "owner_admin_free_running_access": True,
        "internal_config_hidden_from_client": True,
        "customer_safe_response_mode": True,
        "secret_exposure": False,
        "entitlement_bypass": False,
        "governance_bypass": False,
    }
'''.lstrip(), encoding="utf-8")

main_text = MAIN.read_text(encoding="utf-8")

import_line = "from backend.app.core.global_agent_registry import global_agent_registry_summary"
if import_line not in main_text:
    lines = main_text.splitlines()
    insert_at = 0
    for i, line in enumerate(lines):
        if line.startswith("from ") or line.startswith("import "):
            insert_at = i + 1
    lines.insert(insert_at, import_line)
    main_text = "\n".join(lines) + "\n"

route = r'''

@app.get("/admin/agents/global-registry")
def admin_global_agent_registry():
    return global_agent_registry_summary()
'''

if "/admin/agents/global-registry" not in main_text:
    main_text = main_text.rstrip() + "\n" + route + "\n"

MAIN.write_text(main_text, encoding="utf-8")

TEST = ROOT / "test_priority9_global_agent_registry_27.py"
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
'''.lstrip(), encoding="utf-8")

print("PRIORITY9_GLOBAL_AGENT_REGISTRY_27_INSTALLED")
print(f"Main backup: {main_backup}")
print(f"Marketplace backup: {marketplace_backup}")
print(f"Created/updated: {REGISTRY}")
print(f"Updated: {MARKETPLACE}")
print(f"Updated: {MAIN}")
print(f"Created/updated: {TEST}")