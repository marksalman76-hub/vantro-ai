from __future__ import annotations

from typing import Any, Dict

from backend.app.core.global_agent_registry import list_global_agents
from backend.app.runtime.canonical_entitlement_activation_runtime import PACKAGE_RULES


PACKAGE_LIMITS = {
    package: int(rules["max_selectable_agents"])
    for package, rules in PACKAGE_RULES.items()
}

PACKAGE_ORDER = ["starter", "growth", "business", "enterprise"]


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
        enterprise_only = bool(agent.get("enterprise_only"))
        purchased = agent_id in purchased_agents
        active = agent_id in active_agents

        locked_reason = None
        if enterprise_only and package != "enterprise":
            purchased = False
            active = False
            locked_reason = "enterprise_only"
        elif not purchased:
            locked_reason = "not_purchased"

        available_to_activate = (
            purchased
            and not active
            and (active_count < package_limit or package == "enterprise")
            and locked_reason is None
        )

        if purchased and not active and not available_to_activate and locked_reason is None:
            locked_reason = "package_limit_reached"

        catalogue.append({
            "agent_id": agent_id,
            "name": agent["name"],
            "category": agent["category"],
            "purchasable": agent.get("purchasable", True),
            "bundle_eligible": agent.get("bundle_eligible", True),
            "requires_owner_approval_for_high_risk": agent.get("requires_owner_approval_for_high_risk", True),
            "enterprise_only": bool(agent.get("enterprise_only")),
            "purchased": purchased,
            "active": active,
            "available_to_activate": available_to_activate,
            "visible_to_client": agent.get("client_visible", True),
            "locked": locked_reason is not None,
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
