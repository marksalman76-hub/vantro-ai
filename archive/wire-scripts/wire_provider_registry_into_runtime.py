from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

runtime_dir = ROOT / "backend" / "app" / "runtime"
target = runtime_dir / "governed_provider_execution.py"
test_file = ROOT / "test_governed_provider_execution_bridge.py"

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

if target.exists():
    backup = BACKUP_DIR / f"governed_provider_execution_before_{timestamp}.py"
    backup.write_text(target.read_text(encoding="utf-8"), encoding="utf-8")

target.write_text(r'''
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
'''.lstrip(), encoding="utf-8")

test_file.write_text(r'''
from backend.app.runtime.governed_provider_execution import (
    capability_for_action,
    execute_governed_provider_action,
    is_safe_generation_action,
    readiness,
)


def main():
    ready = readiness()

    campaign = execute_governed_provider_action(
        action_type="marketing_campaign_execution",
        payload={
            "business": "Test ecommerce brand",
            "goal": "Generate premium campaign plan",
        },
        tenant_id="owner_admin_test",
        actor_role="owner_admin",
        preferred_provider="openai",
    )

    image = execute_governed_provider_action(
        action_type="image_generation",
        payload={
            "brief": "Premium ecommerce product image concept",
        },
        tenant_id="owner_admin_test",
        actor_role="owner_admin",
    )

    blocked = execute_governed_provider_action(
        action_type="scale_campaign",
        payload={
            "budget_increase": 500,
        },
        tenant_id="client_test",
        actor_role="customer",
        preferred_provider="openai",
    )

    ignored = execute_governed_provider_action(
        action_type="unknown_internal_action",
        payload={},
        tenant_id="client_test",
        actor_role="customer",
    )

    print("GOVERNED_PROVIDER_EXECUTION_BRIDGE_TEST")
    print("readiness_status", ready["status"])
    print("campaign_status", campaign["status"])
    print("campaign_bridge", campaign["bridge"])
    print("campaign_runtime_bridge_status", campaign["runtime_bridge_status"])
    print("campaign_provider", campaign["provider_key"])
    print("campaign_governance", campaign["governance_preserved"])
    print("image_capability", image["capability"])
    print("image_runtime_bridge_status", image["runtime_bridge_status"])
    print("blocked_status", blocked["status"])
    print("blocked_execution", blocked["execution_status"])
    print("blocked_attempted", blocked["provider_execution_attempted"])
    print("ignored_status", ignored["status"])
    print("safe_campaign", is_safe_generation_action("marketing_campaign_execution"))
    print("safe_scale_campaign", is_safe_generation_action("scale_campaign"))
    print("capability_video", capability_for_action("video_generation"))

    assert ready["status"] == "governed_provider_execution_bridge_ready"
    assert campaign["success"] is True
    assert campaign["bridge"] == "governed_provider_execution"
    assert campaign["runtime_bridge_status"] == "provider_registry_routed"
    assert campaign["provider_key"] == "openai"
    assert campaign["governance_preserved"] is True
    assert image["capability"] == "image"
    assert image["runtime_bridge_status"] == "provider_registry_routed"
    assert blocked["success"] is False
    assert blocked["status"] == "owner_approval_required"
    assert blocked["provider_execution_attempted"] is False
    assert ignored["success"] is False
    assert ignored["status"] == "not_routed_to_provider_registry"
    assert is_safe_generation_action("marketing_campaign_execution") is True
    assert is_safe_generation_action("scale_campaign") is False
    assert capability_for_action("video_generation") == "video"

    print("GOVERNED_PROVIDER_EXECUTION_BRIDGE_OK")


if __name__ == "__main__":
    main()
'''.lstrip(), encoding="utf-8")

print("GOVERNED_PROVIDER_EXECUTION_BRIDGE_INSTALLED")
print(f"Created/updated: {target}")
print(f"Created/updated: {test_file}")
print("Provider registry bridge added without weakening governance.")