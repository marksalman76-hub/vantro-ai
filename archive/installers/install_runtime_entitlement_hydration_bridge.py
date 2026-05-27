from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP_DIR = ROOT / "backups" / f"runtime_entitlement_hydration_bridge_before_{STAMP}"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

runtime_path = ROOT / "backend" / "app" / "runtime" / "runtime_entitlement_hydration_bridge.py"
test_path = ROOT / "test_runtime_entitlement_hydration_bridge.py"

for path in [runtime_path, test_path]:
    if path.exists():
        backup = BACKUP_DIR / path.relative_to(ROOT)
        backup.parent.mkdir(parents=True, exist_ok=True)
        backup.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")

runtime_path.parent.mkdir(parents=True, exist_ok=True)

runtime_path.write_text(r'''
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
''', encoding="utf-8")

test_path.write_text(r'''
from backend.app.runtime.runtime_entitlement_hydration_bridge import (
    get_runtime_entitlement_hydration_bridge_status,
    hydrate_entitlements_for_execution,
    seed_execution_entitlements_from_activation_packet,
)

tenant_id = "test-runtime-entitlement-hydration-001"

status = get_runtime_entitlement_hydration_bridge_status()
assert status["runtime_entitlement_hydration_bridge_ready"] is True
assert status["credential_values_exposed"] is False

missing_tenant = hydrate_entitlements_for_execution({
    "actor_role": "client",
    "agent_id": "seo_agent",
})
assert missing_tenant["success"] is False
assert missing_tenant["error"] == "missing_tenant_id"

owner = hydrate_entitlements_for_execution({
    "actor_role": "owner_admin",
    "agent_id": "head_agent",
})
assert owner["success"] is True
assert owner["execution_allowed"] is True
assert owner["runtime_entitlements"]["owner_admin_unrestricted"] is True

missing_activation = hydrate_entitlements_for_execution({
    "actor_role": "client",
    "tenant_id": tenant_id,
    "agent_id": "seo_agent",
})
assert missing_activation["success"] is False
assert missing_activation["error"] == "activation_state_not_found"

seeded = seed_execution_entitlements_from_activation_packet({
    "tenant_id": tenant_id,
    "package_id": "business",
    "selected_agents": ["seo_agent", "email_reply_agent"],
    "actor_role": "system",
})
assert seeded["success"] is True
assert seeded["status"] == "activated"

approved = hydrate_entitlements_for_execution({
    "actor_role": "client",
    "tenant_id": tenant_id,
    "agent_id": "seo_agent",
})
assert approved["success"] is True
assert approved["execution_allowed"] is True
assert approved["status"] == "approved"

blocked = hydrate_entitlements_for_execution({
    "actor_role": "client",
    "tenant_id": tenant_id,
    "agent_id": "head_agent",
})
assert blocked["success"] is False
assert blocked["execution_allowed"] is False
assert blocked["error"] == "requested_agent_not_activated"
assert blocked["next_stage"] == "owner_admin_review_required"

print("RUNTIME_ENTITLEMENT_HYDRATION_BRIDGE_TESTS_PASSED")
print("status_ready", status["runtime_entitlement_hydration_bridge_ready"])
print("missing_tenant_status", missing_tenant["status"])
print("owner_status", owner["status"])
print("missing_activation_error", missing_activation["error"])
print("seeded_status", seeded["status"])
print("approved_status", approved["status"])
print("blocked_error", blocked["error"])
''', encoding="utf-8")

print("RUNTIME_ENTITLEMENT_HYDRATION_BRIDGE_INSTALLED")
print(f"Backup folder: {BACKUP_DIR}")
print(f"Created/updated: {runtime_path}")
print(f"Created/updated: {test_path}")