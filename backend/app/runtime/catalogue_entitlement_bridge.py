from __future__ import annotations

from typing import Any, Dict, List

from backend.app.runtime.canonical_entitlement_activation_runtime import (
    PACKAGE_RULES,
    build_activation_packet,
    get_package_rules,
    validate_agent_selection,
)
from backend.app.runtime.real_agent_component_catalogue import (
    CLIENT_FACING_AGENTS,
    list_client_selectable_agents,
    real_agent_component_catalogue_status,
)


def get_package_catalogue_rules(plan: str) -> Dict[str, Any]:
    canonical = get_package_rules(plan or "business")
    plan_key = canonical["package"]
    rules = canonical["rules"]

    return {
        "plan": plan_key,
        "rules": rules,
        "catalogue_count": real_agent_component_catalogue_status()["commercial_catalogue_count"],
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def list_package_selectable_agents(plan: str) -> Dict[str, Any]:
    plan_key = (plan or "business").strip().lower()
    rules = PACKAGE_RULES.get(plan_key) or PACKAGE_RULES["business"]
    selectable = list_client_selectable_agents(plan_key)["agents"]

    return {
        "plan": plan_key,
        "max_selectable_agents": rules["max_selectable_agents"],
        "enterprise_only_allowed": rules["enterprise_only_allowed"],
        "agents": selectable,
        "available_count": len(selectable),
        "selection_required_before_activation": True,
        "head_agent_available": any(a["key"] == "head_agent" for a in selectable),
        "orchestration_agent_client_selectable": False,
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def validate_package_agent_selection(*, plan: str, selected_agent_keys: List[str]) -> Dict[str, Any]:
    canonical = validate_agent_selection(plan, selected_agent_keys)
    selected_keys = set(canonical["selected_agents"])
    selected = [
        agent
        for agent in CLIENT_FACING_AGENTS
        if agent.get("key") in selected_keys
    ]

    return {
        "valid": canonical["valid"],
        "plan": canonical["plan"],
        "selected_count": len(selected),
        "max_selectable_agents": canonical["max_selectable_agents"],
        "selected_agents": selected,
        "invalid_agent_keys": canonical["invalid_agent_keys"],
        "enterprise_blocked_agent_keys": canonical["enterprise_blocked_agent_keys"],
        "over_limit": canonical["over_limit"],
        "activation_allowed": canonical["activation_allowed"],
        "head_agent_selected": any(a["key"] == "head_agent" for a in selected),
        "canonical_source": canonical["canonical_source"],
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def build_agent_activation_entitlement_packet(*, plan: str, selected_agent_keys: List[str]) -> Dict[str, Any]:
    packet = build_activation_packet(plan, selected_agent_keys)
    installed_catalogue = [a["key"] for a in CLIENT_FACING_AGENTS]

    return {
        "plan": packet["plan"],
        "activation_allowed": packet["activation_allowed"],
        "active_agents": packet["active_agents"],
        "installed_catalogue": installed_catalogue,
        "hidden_unpurchased_agents": [k for k in installed_catalogue if k not in packet["active_agents"]],
        "client_visible_agents": packet["active_agents"],
        "client_hidden_agents_count": len([k for k in installed_catalogue if k not in packet["active_agents"]]),
        "validation": packet["validation"],
        "canonical_source": "canonical_entitlement_activation_runtime",
        "full_catalogue_installed_for_owner_admin": True,
        "client_access_limited_to_paid_selected_agents": True,
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def catalogue_entitlement_bridge_status() -> Dict[str, Any]:
    return {
        "catalogue_entitlement_bridge_ready": True,
        "commercial_catalogue_count": 27,
        "package_rules": PACKAGE_RULES,
        "selection_validation_enabled": True,
        "activation_packet_enabled": True,
        "client_access_limited_to_paid_selected_agents": True,
        "owner_admin_full_catalogue_access_preserved": True,
        "credential_values_exposed": False,
        "customer_safe": True,
    }
