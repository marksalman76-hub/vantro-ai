"""
Governed provider execution bridge.

This module connects safe runtime actions to the global provider connector registry
without weakening entitlement, credit, billing, approval, or governance controls.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from backend.app.runtime.provider_connector_registry import (
    action_requires_owner_approval,
    choose_provider_for_capability,
    execute_provider_action,
)


SAFE_GENERATION_ACTIONS = {
    "global_safe_generation_completed",
    "marketing_campaign_execution",
    "content_generation",
    "image_generation",
    "video_generation",
    "ugc_script_generation",
    "email_copy_generation",
    "product_description_generation",
    "ad_copy_generation",
    "seo_content_generation",
}


CAPABILITY_BY_ACTION = {
    "image_generation": "image",
    "video_generation": "video",
    "ugc_script_generation": "text",
    "email_copy_generation": "text",
    "product_description_generation": "text",
    "ad_copy_generation": "text",
    "seo_content_generation": "text",
    "content_generation": "text",
    "marketing_campaign_execution": "text",
    "global_safe_generation_completed": "text",
}


def is_safe_generation_action(action_type: Optional[str]) -> bool:
    return str(action_type or "").strip().lower() in SAFE_GENERATION_ACTIONS


def capability_for_action(action_type: Optional[str], fallback: str = "text") -> str:
    return CAPABILITY_BY_ACTION.get(str(action_type or "").strip().lower(), fallback)


def execute_governed_provider_action(
    action_type: str,
    payload: Optional[Dict[str, Any]] = None,
    tenant_id: Optional[str] = None,
    actor_role: str = "system",
    preferred_provider: Optional[str] = None,
    capability: Optional[str] = None,
) -> Dict[str, Any]:
    payload = payload or {}
    action_key = str(action_type or "").strip().lower()
    resolved_capability = capability or capability_for_action(action_key)

    if action_requires_owner_approval(action_key):
        return execute_provider_action(
            provider_key=preferred_provider,
            action_type=action_key,
            payload=payload,
            capability=resolved_capability,
            tenant_id=tenant_id,
            actor_role=actor_role,
        )

    if not is_safe_generation_action(action_key):
        return {
            "success": False,
            "status": "not_routed_to_provider_registry",
            "execution_status": "ignored_by_provider_bridge",
            "provider_execution_attempted": False,
            "action_type": action_key,
            "tenant_id": tenant_id,
            "actor_role": actor_role,
            "governance_preserved": True,
            "reason": "Action is not registered as a safe generation provider action.",
        }

    selected_provider = preferred_provider or choose_provider_for_capability(resolved_capability)

    provider_result = execute_provider_action(
        provider_key=selected_provider,
        action_type=action_key,
        payload=payload,
        capability=resolved_capability,
        tenant_id=tenant_id,
        actor_role=actor_role,
    )

    return {
        **provider_result,
        "bridge": "governed_provider_execution",
        "safe_generation_action": True,
        "capability_resolved_from_action": resolved_capability,
        "runtime_bridge_status": "provider_registry_routed",
        "governance_preserved": True,
        "owner_approval_controls_preserved": True,
    }


def readiness() -> Dict[str, Any]:
    return {
        "success": True,
        "status": "governed_provider_execution_bridge_ready",
        "safe_generation_action_count": len(SAFE_GENERATION_ACTIONS),
        "capability_mapping_count": len(CAPABILITY_BY_ACTION),
        "governance_preserved": True,
        "owner_approval_controls_preserved": True,
        "spend_scaling_contracts_owner_gated": True,
    }
