from __future__ import annotations

from typing import Any, Dict, List

from backend.app.runtime.catalogue_entitlement_bridge import (
    build_agent_activation_entitlement_packet,
    list_package_selectable_agents,
    validate_package_agent_selection,
)


def get_signup_agent_selection_options(plan: str = "business") -> Dict[str, Any]:
    selectable = list_package_selectable_agents(plan)

    return {
        "status": "ready",
        "plan": selectable["plan"],
        "max_selectable_agents": selectable["max_selectable_agents"],
        "available_agents": selectable["agents"],
        "available_count": selectable["available_count"],
        "selection_required": True,
        "head_agent_available": selectable["head_agent_available"],
        "orchestration_agent_client_selectable": False,
        "customer_safe": True,
        "credential_values_exposed": False,
    }


def validate_signup_agent_selection(plan: str, selected_agent_keys: List[str]) -> Dict[str, Any]:
    validation = validate_package_agent_selection(
        plan=plan,
        selected_agent_keys=selected_agent_keys,
    )

    return {
        "status": "validated",
        "plan": validation["plan"],
        "valid": validation["valid"],
        "selected_count": validation["selected_count"],
        "max_selectable_agents": validation["max_selectable_agents"],
        "selected_agents": validation["selected_agents"],
        "invalid_agent_keys": validation["invalid_agent_keys"],
        "enterprise_blocked_agent_keys": validation["enterprise_blocked_agent_keys"],
        "over_limit": validation["over_limit"],
        "activation_allowed": validation["activation_allowed"],
        "customer_safe": True,
        "credential_values_exposed": False,
    }


def build_signup_activation_packet(plan: str, selected_agent_keys: List[str]) -> Dict[str, Any]:
    packet = build_agent_activation_entitlement_packet(
        plan=plan,
        selected_agent_keys=selected_agent_keys,
    )

    return {
        "status": "activation_packet_ready" if packet["activation_allowed"] else "activation_packet_blocked",
        "packet": packet,
        "selected_count": len(packet["active_agents"]),
        "hidden_unpurchased_agents": packet["hidden_unpurchased_agents"],
        "client_visible_agents": packet["client_visible_agents"],
        "customer_safe": True,
        "credential_values_exposed": False,
    }


def signup_agent_selection_bridge_status() -> Dict[str, Any]:
    return {
        "signup_agent_selection_bridge_ready": True,
        "uses_locked_27_agent_catalogue": True,
        "plan_based_selection_enabled": True,
        "selection_validation_enabled": True,
        "activation_packet_enabled": True,
        "head_agent_enterprise_only_enforced": True,
        "customer_safe": True,
        "credential_values_exposed": False,
    }
