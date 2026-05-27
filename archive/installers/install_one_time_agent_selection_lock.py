from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

runtime_dir = ROOT / "backend" / "app" / "runtime"
target = runtime_dir / "one_time_agent_selection_lock.py"
test_file = ROOT / "test_one_time_agent_selection_lock_direct.py"

backup_dir = ROOT / "backups" / f"one_time_agent_selection_lock_before_{STAMP}"
backup_dir.mkdir(parents=True, exist_ok=True)

for p in [target, test_file]:
    if p.exists():
        (backup_dir / p.name).write_text(p.read_text(encoding="utf-8"), encoding="utf-8")

target.write_text(r'''
from __future__ import annotations

import time
import uuid
from typing import Any, Dict, List, Optional

from backend.app.runtime.signup_agent_selection_bridge import build_signup_activation_packet


_SELECTION_DRAFTS: Dict[str, Dict[str, Any]] = {}
_ACTIVATED_PACKAGE_SELECTIONS: Dict[str, Dict[str, Any]] = {}


def _now_ms() -> int:
    return int(time.time() * 1000)


def _activation_key(tenant_id: str, package_id: str) -> str:
    return f"{tenant_id.strip().lower()}::{package_id.strip().lower()}"


def reset_one_time_agent_selection_lock_for_tests() -> Dict[str, Any]:
    _SELECTION_DRAFTS.clear()
    _ACTIVATED_PACKAGE_SELECTIONS.clear()
    return {
        "reset": True,
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def create_agent_selection_draft(
    *,
    tenant_id: str,
    package_id: str,
    plan: str,
    selected_agent_keys: List[str],
) -> Dict[str, Any]:
    key = _activation_key(tenant_id, package_id)

    if key in _ACTIVATED_PACKAGE_SELECTIONS:
        return {
            "status": "blocked",
            "reason": "package_agent_selection_already_activated",
            "selection_locked": True,
            "owner_admin_required_for_changes": True,
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    packet = build_signup_activation_packet(plan, selected_agent_keys)

    draft_id = f"agent_selection_draft_{uuid.uuid4().hex[:16]}"
    draft = {
        "draft_id": draft_id,
        "tenant_id": tenant_id,
        "package_id": package_id,
        "plan": plan,
        "selected_agent_keys": selected_agent_keys,
        "activation_packet": packet,
        "activation_allowed": packet["packet"]["activation_allowed"],
        "selection_locked": False,
        "created_at_ms": _now_ms(),
        "updated_at_ms": _now_ms(),
        "credential_values_exposed": False,
        "customer_safe": True,
    }

    _SELECTION_DRAFTS[draft_id] = draft

    return {
        "status": "draft_created",
        "draft": draft,
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def get_agent_selection_draft(draft_id: str) -> Dict[str, Any]:
    draft = _SELECTION_DRAFTS.get(draft_id)
    if not draft:
        return {
            "status": "not_found",
            "draft_id": draft_id,
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    return {
        "status": "found",
        "draft": draft,
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def activate_agent_selection_once(
    *,
    tenant_id: str,
    package_id: str,
    draft_id: str,
) -> Dict[str, Any]:
    key = _activation_key(tenant_id, package_id)

    if key in _ACTIVATED_PACKAGE_SELECTIONS:
        existing = _ACTIVATED_PACKAGE_SELECTIONS[key]
        return {
            "status": "blocked",
            "reason": "package_agent_selection_already_activated",
            "selection_locked": True,
            "activated_selection": existing,
            "owner_admin_required_for_changes": True,
            "client_can_change_selection": False,
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    draft = _SELECTION_DRAFTS.get(draft_id)
    if not draft:
        return {
            "status": "not_found",
            "reason": "selection_draft_not_found",
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    if draft["tenant_id"] != tenant_id or draft["package_id"] != package_id:
        return {
            "status": "blocked",
            "reason": "draft_tenant_or_package_mismatch",
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    if not draft["activation_allowed"]:
        return {
            "status": "blocked",
            "reason": "activation_packet_not_allowed",
            "selection_locked": False,
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    activated = {
        "activation_id": f"agent_selection_activation_{uuid.uuid4().hex[:16]}",
        "tenant_id": tenant_id,
        "package_id": package_id,
        "plan": draft["plan"],
        "active_agents": draft["activation_packet"]["packet"]["active_agents"],
        "client_visible_agents": draft["activation_packet"]["packet"]["client_visible_agents"],
        "hidden_unpurchased_agents": draft["activation_packet"]["packet"]["hidden_unpurchased_agents"],
        "client_hidden_agents_count": draft["activation_packet"]["packet"]["client_hidden_agents_count"],
        "selection_locked": True,
        "client_can_change_selection": False,
        "owner_admin_required_for_changes": True,
        "head_agent_enterprise_only_enforced": True,
        "activated_at_ms": _now_ms(),
        "credential_values_exposed": False,
        "customer_safe": True,
    }

    _ACTIVATED_PACKAGE_SELECTIONS[key] = activated
    draft["selection_locked"] = True
    draft["updated_at_ms"] = _now_ms()

    return {
        "status": "activated",
        "activated_selection": activated,
        "selection_locked": True,
        "client_can_change_selection": False,
        "owner_admin_required_for_changes": True,
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def get_activated_agent_selection(
    *,
    tenant_id: str,
    package_id: str,
) -> Dict[str, Any]:
    key = _activation_key(tenant_id, package_id)
    activated = _ACTIVATED_PACKAGE_SELECTIONS.get(key)

    if not activated:
        return {
            "status": "not_found",
            "selection_locked": False,
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    return {
        "status": "found",
        "activated_selection": activated,
        "selection_locked": True,
        "client_can_change_selection": False,
        "owner_admin_required_for_changes": True,
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def request_post_activation_agent_change(
    *,
    tenant_id: str,
    package_id: str,
    requested_agent_keys: List[str],
    reason: Optional[str] = None,
) -> Dict[str, Any]:
    existing = get_activated_agent_selection(tenant_id=tenant_id, package_id=package_id)

    if existing["status"] != "found":
        return {
            "status": "blocked",
            "reason": "no_activated_selection_found",
            "owner_admin_required_for_changes": True,
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    return {
        "status": "owner_admin_review_required",
        "reason": "post_activation_agent_changes_require_owner_admin_approval",
        "tenant_id": tenant_id,
        "package_id": package_id,
        "current_active_agents": existing["activated_selection"]["active_agents"],
        "requested_agent_keys": requested_agent_keys,
        "change_reason_present": bool(reason),
        "client_can_change_selection": False,
        "owner_admin_required_for_changes": True,
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def one_time_agent_selection_lock_status() -> Dict[str, Any]:
    return {
        "one_time_agent_selection_lock_ready": True,
        "client_selects_once_per_package": True,
        "selection_locked_after_activation": True,
        "client_post_activation_changes_blocked": True,
        "owner_admin_required_for_post_activation_changes": True,
        "activated_selection_count": len(_ACTIVATED_PACKAGE_SELECTIONS),
        "draft_count": len(_SELECTION_DRAFTS),
        "credential_values_exposed": False,
        "customer_safe": True,
    }
'''.lstrip(), encoding="utf-8")

test_file.write_text(r'''
from backend.app.runtime.one_time_agent_selection_lock import (
    activate_agent_selection_once,
    create_agent_selection_draft,
    get_activated_agent_selection,
    one_time_agent_selection_lock_status,
    request_post_activation_agent_change,
    reset_one_time_agent_selection_lock_for_tests,
)

reset = reset_one_time_agent_selection_lock_for_tests()
assert reset["reset"] is True

status = one_time_agent_selection_lock_status()
assert status["client_selects_once_per_package"] is True
assert status["selection_locked_after_activation"] is True

draft = create_agent_selection_draft(
    tenant_id="tenant-test",
    package_id="package-starter-1",
    plan="starter",
    selected_agent_keys=["seo_agent", "marketing_specialist_agent", "email_reply_agent"],
)
assert draft["status"] == "draft_created"
assert draft["draft"]["activation_allowed"] is True

activated = activate_agent_selection_once(
    tenant_id="tenant-test",
    package_id="package-starter-1",
    draft_id=draft["draft"]["draft_id"],
)
assert activated["status"] == "activated"
assert activated["selection_locked"] is True
assert activated["client_can_change_selection"] is False
assert len(activated["activated_selection"]["active_agents"]) == 3

second_draft = create_agent_selection_draft(
    tenant_id="tenant-test",
    package_id="package-starter-1",
    plan="starter",
    selected_agent_keys=["crm_agent"],
)
assert second_draft["status"] == "blocked"
assert second_draft["reason"] == "package_agent_selection_already_activated"

second_activate = activate_agent_selection_once(
    tenant_id="tenant-test",
    package_id="package-starter-1",
    draft_id=draft["draft"]["draft_id"],
)
assert second_activate["status"] == "blocked"
assert second_activate["reason"] == "package_agent_selection_already_activated"

existing = get_activated_agent_selection(
    tenant_id="tenant-test",
    package_id="package-starter-1",
)
assert existing["status"] == "found"
assert existing["client_can_change_selection"] is False

change = request_post_activation_agent_change(
    tenant_id="tenant-test",
    package_id="package-starter-1",
    requested_agent_keys=["crm_agent"],
    reason="Client wants to swap.",
)
assert change["status"] == "owner_admin_review_required"
assert change["client_can_change_selection"] is False

print("ONE_TIME_AGENT_SELECTION_LOCK_DIRECT_TESTS_PASSED")
print("activated_status", activated["status"])
print("active_agents", len(activated["activated_selection"]["active_agents"]))
print("second_draft", second_draft["status"], second_draft["reason"])
print("change_status", change["status"])
'''.lstrip(), encoding="utf-8")

print("ONE_TIME_AGENT_SELECTION_LOCK_INSTALLED")
print(f"Backup folder: {backup_dir}")
print(f"Created/updated: {target}")
print(f"Created/updated: {test_file}")