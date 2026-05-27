from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

runtime_dir = ROOT / "backend" / "app" / "runtime"
target = runtime_dir / "signup_agent_selection_bridge.py"
test_file = ROOT / "test_signup_agent_selection_bridge_direct.py"

backup_dir = ROOT / "backups" / f"signup_agent_selection_bridge_before_{STAMP}"
backup_dir.mkdir(parents=True, exist_ok=True)

for p in [target, test_file]:
    if p.exists():
        (backup_dir / p.name).write_text(p.read_text(encoding="utf-8"), encoding="utf-8")

target.write_text(r'''
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
'''.lstrip(), encoding="utf-8")

test_file.write_text(r'''
from backend.app.runtime.signup_agent_selection_bridge import (
    build_signup_activation_packet,
    get_signup_agent_selection_options,
    signup_agent_selection_bridge_status,
    validate_signup_agent_selection,
)

status = signup_agent_selection_bridge_status()
assert status["signup_agent_selection_bridge_ready"] is True
assert status["uses_locked_27_agent_catalogue"] is True

starter = get_signup_agent_selection_options("starter")
assert starter["max_selectable_agents"] == 3
assert starter["available_count"] == 26
assert starter["head_agent_available"] is False

enterprise = get_signup_agent_selection_options("enterprise")
assert enterprise["max_selectable_agents"] == 27
assert enterprise["available_count"] == 27
assert enterprise["head_agent_available"] is True

valid = validate_signup_agent_selection(
    "starter",
    ["seo_agent", "marketing_specialist_agent", "email_reply_agent"],
)
assert valid["valid"] is True
assert valid["activation_allowed"] is True

blocked = validate_signup_agent_selection("business", ["head_agent"])
assert blocked["valid"] is False
assert blocked["enterprise_blocked_agent_keys"] == ["head_agent"]

packet = build_signup_activation_packet(
    "starter",
    ["seo_agent", "marketing_specialist_agent", "email_reply_agent"],
)
assert packet["status"] == "activation_packet_ready"
assert packet["selected_count"] == 3
assert len(packet["client_visible_agents"]) == 3

print("SIGNUP_AGENT_SELECTION_BRIDGE_DIRECT_TESTS_PASSED")
print("starter_available", starter["available_count"])
print("enterprise_available", enterprise["available_count"])
print("valid_selected", valid["selected_count"])
print("packet_selected", packet["selected_count"])
'''.lstrip(), encoding="utf-8")

print("SIGNUP_AGENT_SELECTION_BRIDGE_INSTALLED")
print(f"Backup folder: {backup_dir}")
print(f"Created/updated: {target}")
print(f"Created/updated: {test_file}")
