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

    if bool(agent.get("enterprise_only")) and package != "enterprise":
        return {
            "success": False,
            "error": "enterprise_only_agent",
            "agent_id": agent_id,
            "upgrade_required": True,
            "enterprise_contact_required": True,
            "customer_safe_message": "This agent is available on Enterprise after owner review.",
        }

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
