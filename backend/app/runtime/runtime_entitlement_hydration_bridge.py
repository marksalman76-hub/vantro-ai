
from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict

from backend.app.runtime.governed_activation_persistence import (
    persist_activation_packet,
)
from backend.app.core.canonical_billing_state_runtime import owner_admin_bypasses_client_billing
from backend.app.runtime.canonical_entitlement_activation_runtime import evaluate_execution_entitlement, get_entitlement


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

    if owner_admin_bypasses_client_billing(actor_role):
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

    execution_decision = evaluate_execution_entitlement(
        tenant_id=tenant_id,
        requested_agent=requested_agent,
        actor_role=actor_role,
    )
    entitlement_result = get_entitlement(tenant_id)
    entitlement = entitlement_result.get("entitlement") or {}
    allowed = entitlement.get("active_agents", [])
    runtime_entitlements = {
        "allowed_agent_ids": deepcopy(allowed),
        "agent_execution_allowed": bool(execution_decision.get("execution_allowed")),
        "post_activation_client_changes_blocked": True,
        "owner_admin_required_for_post_activation_changes": True,
        "activation_locked": bool(entitlement.get("activation_locked")),
    }

    if not entitlement_result.get("success"):
        return {
            "success": False,
            "status": "blocked",
            "error": "entitlement_not_found",
            "tenant_id": tenant_id,
            "requested_agent": requested_agent,
            "execution_allowed": False,
            "entitlement_source": "canonical_entitlement_activation_runtime",
            "runtime_entitlements": deepcopy(runtime_entitlements),
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    if not execution_decision.get("execution_allowed"):
        return {
            "success": False,
            "status": "blocked",
            "error": execution_decision.get("error") or "requested_agent_not_activated",
            "tenant_id": tenant_id,
            "requested_agent": requested_agent,
            "activated_agents": deepcopy(allowed),
            "execution_allowed": False,
            "entitlement_source": "canonical_entitlement_activation_runtime",
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
        "entitlement_source": "canonical_entitlement_activation_runtime",
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
