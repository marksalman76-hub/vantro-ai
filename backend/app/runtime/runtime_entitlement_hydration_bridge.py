
from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict

from backend.app.runtime.governed_activation_persistence import (
    hydrate_runtime_entitlements,
    persist_activation_packet,
)


OWNER_ADMIN_ROLES = {"owner", "admin", "owner_admin", "system_admin", "platform_admin"}


def hydrate_entitlements_for_execution(execution_request: Dict[str, Any]) -> Dict[str, Any]:
    tenant_id = str(
        execution_request.get("tenant_id")
        or execution_request.get("client_id")
        or ""
    ).strip()

    actor_role = str(execution_request.get("actor_role") or "client").strip().lower()
    requested_agent = str(
        execution_request.get("agent_id")
        or execution_request.get("agent_key")
        or execution_request.get("requested_agent")
        or ""
    ).strip()

    if actor_role in OWNER_ADMIN_ROLES:
        return {
            "success": True,
            "status": "owner_admin_unrestricted",
            "tenant_id": tenant_id,
            "requested_agent": requested_agent,
            "execution_allowed": True,
            "entitlement_source": "owner_admin_unrestricted_access",
            "runtime_entitlements": {
                "allowed_agent_ids": ["*"],
                "agent_execution_allowed": True,
                "owner_admin_unrestricted": True,
            },
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    if not tenant_id:
        return {
            "success": False,
            "status": "blocked",
            "error": "missing_tenant_id",
            "execution_allowed": False,
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    if not requested_agent:
        return {
            "success": False,
            "status": "blocked",
            "error": "missing_requested_agent",
            "tenant_id": tenant_id,
            "execution_allowed": False,
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    hydrated = hydrate_runtime_entitlements(tenant_id)
    runtime_entitlements = hydrated.get("runtime_entitlements", {})
    allowed = runtime_entitlements.get("allowed_agent_ids", [])

    if not hydrated.get("success"):
        return {
            "success": False,
            "status": "blocked",
            "error": "activation_state_not_found",
            "tenant_id": tenant_id,
            "requested_agent": requested_agent,
            "execution_allowed": False,
            "entitlement_source": "governed_activation_persistence",
            "runtime_entitlements": deepcopy(runtime_entitlements),
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    if requested_agent not in allowed:
        return {
            "success": False,
            "status": "blocked",
            "error": "requested_agent_not_activated",
            "tenant_id": tenant_id,
            "requested_agent": requested_agent,
            "activated_agents": deepcopy(allowed),
            "execution_allowed": False,
            "entitlement_source": "governed_activation_persistence",
            "next_stage": "owner_admin_review_required",
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    return {
        "success": True,
        "status": "approved",
        "tenant_id": tenant_id,
        "requested_agent": requested_agent,
        "execution_allowed": True,
        "entitlement_source": "governed_activation_persistence",
        "runtime_entitlements": deepcopy(runtime_entitlements),
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def seed_execution_entitlements_from_activation_packet(packet: Dict[str, Any]) -> Dict[str, Any]:
    return persist_activation_packet(packet, actor_role=str(packet.get("actor_role", "system")))


def get_runtime_entitlement_hydration_bridge_status() -> Dict[str, Any]:
    return {
        "success": True,
        "runtime_entitlement_hydration_bridge_ready": True,
        "governed_activation_persistence_connected": True,
        "owner_admin_unrestricted_access_preserved": True,
        "client_execution_limited_to_activated_agents": True,
        "missing_activation_blocks_execution": True,
        "unactivated_agent_blocks_execution": True,
        "credential_values_exposed": False,
        "customer_safe": True,
    }
