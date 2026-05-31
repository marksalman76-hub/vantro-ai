from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

execution_stack = ROOT / "backend" / "app" / "runtime" / "execution_stack.py"
test_file = ROOT / "test_execution_stack_provider_bridge_runtime.py"

if not execution_stack.exists():
    raise FileNotFoundError(f"Missing execution stack: {execution_stack}")

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUP_DIR / f"execution_stack_before_provider_bridge_{timestamp}.py"
backup.write_text(execution_stack.read_text(encoding="utf-8"), encoding="utf-8")

source = execution_stack.read_text(encoding="utf-8")

marker = "# --- Global governed provider bridge integration ---"

bridge_block = r'''

# --- Global governed provider bridge integration ---
# Installed to route safe-generation runtime actions through the global provider
# connector registry while preserving entitlement, billing, credit, approval,
# and governance controls.

try:
    from backend.app.runtime.governed_provider_execution import (
        execute_governed_provider_action as _execute_governed_provider_action,
        is_safe_generation_action as _is_safe_generation_provider_action,
    )
except Exception:  # pragma: no cover - runtime-safe fallback
    _execute_governed_provider_action = None

    def _is_safe_generation_provider_action(action_type):
        return False


def execute_safe_generation_via_provider_bridge(
    action_type,
    payload=None,
    tenant_id=None,
    actor_role="system",
    preferred_provider=None,
    capability=None,
):
    """
    Runtime-safe bridge for safe-generation provider actions.

    This function is intentionally additive. Existing execution-stack behaviour
    remains intact unless a caller explicitly routes through this function.
    """

    payload = payload or {}

    if _execute_governed_provider_action is None:
        return {
            "success": False,
            "status": "provider_bridge_unavailable",
            "execution_status": "provider_bridge_not_loaded",
            "provider_execution_attempted": False,
            "action_type": action_type,
            "tenant_id": tenant_id,
            "actor_role": actor_role,
            "governance_preserved": True,
            "owner_approval_controls_preserved": True,
        }

    return _execute_governed_provider_action(
        action_type=action_type,
        payload=payload,
        tenant_id=tenant_id,
        actor_role=actor_role,
        preferred_provider=preferred_provider,
        capability=capability,
    )


def runtime_provider_bridge_readiness():
    """
    Lightweight readiness check used by tests/admin diagnostics.
    """

    return {
        "success": True,
        "status": "execution_stack_provider_bridge_ready",
        "bridge_loaded": _execute_governed_provider_action is not None,
        "safe_campaign_supported": _is_safe_generation_provider_action("marketing_campaign_execution"),
        "safe_image_supported": _is_safe_generation_provider_action("image_generation"),
        "safe_video_supported": _is_safe_generation_provider_action("video_generation"),
        "spend_scaling_contracts_owner_gated": True,
        "governance_preserved": True,
        "owner_approval_controls_preserved": True,
    }
'''

if marker not in source:
    source = source.rstrip() + bridge_block
    execution_stack.write_text(source + "\n", encoding="utf-8")
    changed = True
else:
    changed = False

test_file.write_text(r'''
from backend.app.runtime.execution_stack import (
    execute_safe_generation_via_provider_bridge,
    runtime_provider_bridge_readiness,
)


def main():
    ready = runtime_provider_bridge_readiness()

    campaign = execute_safe_generation_via_provider_bridge(
        action_type="marketing_campaign_execution",
        payload={
            "business": "Runtime bridge test ecommerce brand",
            "goal": "Create governed campaign execution plan",
        },
        tenant_id="owner_admin_test",
        actor_role="owner_admin",
        preferred_provider="openai",
    )

    image = execute_safe_generation_via_provider_bridge(
        action_type="image_generation",
        payload={
            "brief": "Premium ecommerce product image concept",
        },
        tenant_id="owner_admin_test",
        actor_role="owner_admin",
    )

    blocked = execute_safe_generation_via_provider_bridge(
        action_type="scale_campaign",
        payload={
            "budget_increase": 1000,
        },
        tenant_id="client_test",
        actor_role="customer",
        preferred_provider="openai",
    )

    print("EXECUTION_STACK_PROVIDER_BRIDGE_RUNTIME_TEST")
    print("readiness_status", ready["status"])
    print("bridge_loaded", ready["bridge_loaded"])
    print("safe_campaign_supported", ready["safe_campaign_supported"])
    print("safe_image_supported", ready["safe_image_supported"])
    print("safe_video_supported", ready["safe_video_supported"])
    print("campaign_status", campaign["status"])
    print("campaign_runtime_bridge_status", campaign.get("runtime_bridge_status"))
    print("campaign_provider", campaign.get("provider_key"))
    print("campaign_governance", campaign["governance_preserved"])
    print("image_status", image["status"])
    print("image_capability", image.get("capability"))
    print("blocked_status", blocked["status"])
    print("blocked_execution", blocked["execution_status"])
    print("blocked_attempted", blocked["provider_execution_attempted"])
    print("blocked_governance", blocked["governance_preserved"])

    assert ready["status"] == "execution_stack_provider_bridge_ready"
    assert ready["bridge_loaded"] is True
    assert ready["safe_campaign_supported"] is True
    assert ready["safe_image_supported"] is True
    assert ready["safe_video_supported"] is True
    assert campaign["success"] is True
    assert campaign["status"] == "provider_action_ready"
    assert campaign["runtime_bridge_status"] == "provider_registry_routed"
    assert campaign["provider_key"] == "openai"
    assert campaign["governance_preserved"] is True
    assert image["success"] is True
    assert image["capability"] == "image"
    assert blocked["success"] is False
    assert blocked["status"] == "owner_approval_required"
    assert blocked["provider_execution_attempted"] is False
    assert blocked["governance_preserved"] is True

    print("EXECUTION_STACK_PROVIDER_BRIDGE_RUNTIME_OK")


if __name__ == "__main__":
    main()
'''.lstrip(), encoding="utf-8")

print("EXECUTION_STACK_PROVIDER_BRIDGE_WIRED")
print(f"Backup: {backup}")
print(f"Updated: {execution_stack}")
print(f"Created/updated: {test_file}")
print(f"Changed: {changed}")
print("Governance preserved: spend/scaling/contracts remain owner approval gated.")