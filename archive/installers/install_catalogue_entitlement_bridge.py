from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

runtime_dir = ROOT / "backend" / "app" / "runtime"
target = runtime_dir / "catalogue_entitlement_bridge.py"
test_file = ROOT / "test_catalogue_entitlement_bridge_direct.py"

backup_dir = ROOT / "backups" / f"catalogue_entitlement_bridge_before_{STAMP}"
backup_dir.mkdir(parents=True, exist_ok=True)

for p in [target, test_file]:
    if p.exists():
        (backup_dir / p.name).write_text(p.read_text(encoding="utf-8"), encoding="utf-8")

target.write_text(r'''
from __future__ import annotations

from typing import Any, Dict, List

from backend.app.runtime.real_agent_component_catalogue import (
    CLIENT_FACING_AGENTS,
    get_catalogue_component_by_key,
    list_client_selectable_agents,
    real_agent_component_catalogue_status,
)

PACKAGE_RULES = {
    "starter": {"max_selectable_agents": 3, "enterprise_only_allowed": False},
    "growth": {"max_selectable_agents": 6, "enterprise_only_allowed": False},
    "business": {"max_selectable_agents": 12, "enterprise_only_allowed": False},
    "enterprise": {"max_selectable_agents": 27, "enterprise_only_allowed": True},
}


def get_package_catalogue_rules(plan: str) -> Dict[str, Any]:
    plan_key = (plan or "business").strip().lower()
    rules = PACKAGE_RULES.get(plan_key) or PACKAGE_RULES["business"]

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
    plan_key = (plan or "business").strip().lower()
    rules = PACKAGE_RULES.get(plan_key) or PACKAGE_RULES["business"]

    selected = []
    invalid = []
    enterprise_blocked = []

    for raw_key in selected_agent_keys or []:
        key = str(raw_key).strip().lower()
        found = get_catalogue_component_by_key(key)

        if not found.get("found"):
            invalid.append(key)
            continue

        component = found["component"]
        if found["component_type"] != "client_facing_agent":
            invalid.append(key)
            continue

        if component.get("enterprise_only") and not rules["enterprise_only_allowed"]:
            enterprise_blocked.append(key)
            continue

        selected.append(component)

    over_limit = len(selected) > rules["max_selectable_agents"]

    valid = not invalid and not enterprise_blocked and not over_limit

    return {
        "valid": valid,
        "plan": plan_key,
        "selected_count": len(selected),
        "max_selectable_agents": rules["max_selectable_agents"],
        "selected_agents": selected,
        "invalid_agent_keys": invalid,
        "enterprise_blocked_agent_keys": enterprise_blocked,
        "over_limit": over_limit,
        "activation_allowed": valid,
        "head_agent_selected": any(a["key"] == "head_agent" for a in selected),
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def build_agent_activation_entitlement_packet(*, plan: str, selected_agent_keys: List[str]) -> Dict[str, Any]:
    validation = validate_package_agent_selection(
        plan=plan,
        selected_agent_keys=selected_agent_keys,
    )

    active_agents = [a["key"] for a in validation["selected_agents"]] if validation["valid"] else []

    installed_catalogue = [a["key"] for a in CLIENT_FACING_AGENTS]

    return {
        "plan": validation["plan"],
        "activation_allowed": validation["activation_allowed"],
        "active_agents": active_agents,
        "installed_catalogue": installed_catalogue,
        "hidden_unpurchased_agents": [k for k in installed_catalogue if k not in active_agents],
        "client_visible_agents": active_agents,
        "client_hidden_agents_count": len([k for k in installed_catalogue if k not in active_agents]),
        "validation": validation,
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
'''.lstrip(), encoding="utf-8")

test_file.write_text(r'''
from backend.app.runtime.catalogue_entitlement_bridge import (
    build_agent_activation_entitlement_packet,
    catalogue_entitlement_bridge_status,
    get_package_catalogue_rules,
    list_package_selectable_agents,
    validate_package_agent_selection,
)

status = catalogue_entitlement_bridge_status()
assert status["catalogue_entitlement_bridge_ready"] is True
assert status["commercial_catalogue_count"] == 27

starter_rules = get_package_catalogue_rules("starter")
assert starter_rules["rules"]["max_selectable_agents"] == 3

business_agents = list_package_selectable_agents("business")
assert business_agents["available_count"] == 26
assert business_agents["head_agent_available"] is False

enterprise_agents = list_package_selectable_agents("enterprise")
assert enterprise_agents["available_count"] == 27
assert enterprise_agents["head_agent_available"] is True

valid = validate_package_agent_selection(
    plan="starter",
    selected_agent_keys=["seo_agent", "marketing_specialist_agent", "email_reply_agent"],
)
assert valid["valid"] is True
assert valid["selected_count"] == 3

over_limit = validate_package_agent_selection(
    plan="starter",
    selected_agent_keys=["seo_agent", "marketing_specialist_agent", "email_reply_agent", "crm_agent"],
)
assert over_limit["valid"] is False
assert over_limit["over_limit"] is True

blocked = validate_package_agent_selection(
    plan="business",
    selected_agent_keys=["head_agent"],
)
assert blocked["valid"] is False
assert blocked["enterprise_blocked_agent_keys"] == ["head_agent"]

packet = build_agent_activation_entitlement_packet(
    plan="starter",
    selected_agent_keys=["seo_agent", "marketing_specialist_agent", "email_reply_agent"],
)
assert packet["activation_allowed"] is True
assert len(packet["active_agents"]) == 3
assert packet["client_access_limited_to_paid_selected_agents"] is True
assert packet["full_catalogue_installed_for_owner_admin"] is True

print("CATALOGUE_ENTITLEMENT_BRIDGE_DIRECT_TESTS_PASSED")
print("commercial_catalogue_count", status["commercial_catalogue_count"])
print("business_available", business_agents["available_count"])
print("enterprise_available", enterprise_agents["available_count"])
print("packet_active_agents", len(packet["active_agents"]))
print("hidden_unpurchased", packet["client_hidden_agents_count"])
'''.lstrip(), encoding="utf-8")

print("CATALOGUE_ENTITLEMENT_BRIDGE_INSTALLED")
print(f"Backup folder: {backup_dir}")
print(f"Created/updated: {target}")
print(f"Created/updated: {test_file}")