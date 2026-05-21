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
