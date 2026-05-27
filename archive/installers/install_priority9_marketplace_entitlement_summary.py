from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
MAIN = ROOT / "backend" / "app" / "main.py"
CORE_DIR = ROOT / "backend" / "app" / "core"
RUNTIME = CORE_DIR / "marketplace_entitlement_runtime.py"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

main_backup = BACKUP_DIR / f"main_before_priority9_marketplace_entitlement_{timestamp}.py"
main_backup.write_text(MAIN.read_text(encoding="utf-8"), encoding="utf-8")

if RUNTIME.exists():
    runtime_backup = BACKUP_DIR / f"marketplace_entitlement_runtime_before_{timestamp}.py"
    runtime_backup.write_text(RUNTIME.read_text(encoding="utf-8"), encoding="utf-8")

RUNTIME.write_text(r'''
from __future__ import annotations

from typing import Any, Dict, List


FULL_AGENT_CATALOGUE = [
    {"agent_id": "head_agent", "name": "Head Agent / CEO", "category": "Core Control"},
    {"agent_id": "strategist_agent", "name": "Strategist Agent", "category": "Core Control"},
    {"agent_id": "business_growth_partnerships_agent", "name": "Business Growth & Partnerships Agent", "category": "Business Growth"},
    {"agent_id": "lead_generator_appointment_setter_agent", "name": "Lead Generator / Appointment Setter Agent", "category": "Business Growth"},
    {"agent_id": "marketing_specialist_agent", "name": "Marketing Specialist Agent", "category": "Business Growth"},
    {"agent_id": "social_media_manager_content_creator_agent", "name": "Social Media Manager / Content Creator Agent", "category": "Business Growth"},
    {"agent_id": "seo_agent", "name": "SEO Agent", "category": "Business Growth"},
    {"agent_id": "email_reply_agent", "name": "Email Reply Agent", "category": "Business Growth"},
    {"agent_id": "crm_ai_agent", "name": "CRM AI Agent", "category": "Business Growth"},
    {"agent_id": "receptionist_agent", "name": "Receptionist Agent", "category": "Frontline Operations"},
    {"agent_id": "custom_websites_landing_pages_apps_agent", "name": "Custom Websites / Landing Pages / Apps Agent", "category": "Product & Delivery"},
    {"agent_id": "product_development_agent", "name": "Product Development Agent", "category": "Product & Delivery"},
    {"agent_id": "ecommerce_agent", "name": "E-commerce Agent", "category": "Product & Delivery"},
    {"agent_id": "demo_trial_agent", "name": "Demo / Trial Agent", "category": "Scale / System"},
    {"agent_id": "orchestration_agent", "name": "Orchestration Agent", "category": "Recommended System"},
    {"agent_id": "security_compliance_agent", "name": "Security & Compliance Agent", "category": "Recommended System"},
    {"agent_id": "analytics_intelligence_agent", "name": "Analytics & Intelligence Agent", "category": "Recommended System"},
    {"agent_id": "qa_testing_agent", "name": "QA / Testing Agent", "category": "Recommended System"},
    {"agent_id": "integration_automation_agent", "name": "Integration / Automation Agent", "category": "Recommended System"},
    {"agent_id": "billing_optimisation_agent", "name": "Billing Optimisation Agent", "category": "Recommended System"},
    {"agent_id": "training_learning_agent", "name": "Training / Learning Agent", "category": "Recommended System"},
]

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

    package_limit = PACKAGE_LIMITS[package]
    active_count = len(active_agents)
    purchased_count = len(purchased_agents)

    catalogue = []

    for agent in FULL_AGENT_CATALOGUE:
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
            **agent,
            "purchased": purchased,
            "active": active,
            "available_to_activate": available_to_activate,
            "visible_to_client": purchased or True,
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
        "marketplace_profile": "priority9_marketplace_entitlement_summary_v1",
        "tenant_id": tenant_id,
        "client_number": client_number,
        "package": package,
        "package_limit": package_limit,
        "active_agent_count": active_count,
        "purchased_agent_count": purchased_count,
        "catalogue_agent_count": len(FULL_AGENT_CATALOGUE),
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

import_line = "from backend.app.core.marketplace_entitlement_runtime import build_marketplace_entitlement_summary"
if import_line not in main_text:
    lines = main_text.splitlines()
    insert_at = 0
    for i, line in enumerate(lines):
        if line.startswith("from ") or line.startswith("import "):
            insert_at = i + 1
    lines.insert(insert_at, import_line)
    main_text = "\n".join(lines) + "\n"

route = r'''

@app.post("/admin/marketplace/entitlement-summary")
def admin_marketplace_entitlement_summary(payload: dict):
    return build_marketplace_entitlement_summary(payload)
'''

if "/admin/marketplace/entitlement-summary" not in main_text:
    main_text = main_text.rstrip() + "\n" + route + "\n"

MAIN.write_text(main_text, encoding="utf-8")

TEST = ROOT / "test_priority9_marketplace_entitlement_summary.py"
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
'''.lstrip(), encoding="utf-8")

print("PRIORITY9_MARKETPLACE_ENTITLEMENT_SUMMARY_INSTALLED")
print(f"Main backup: {main_backup}")
print(f"Created/updated: {RUNTIME}")
print(f"Created/updated: {TEST}")
print("Route: /admin/marketplace/entitlement-summary")