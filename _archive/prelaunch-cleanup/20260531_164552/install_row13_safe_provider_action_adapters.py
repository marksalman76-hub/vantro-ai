from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
runtime_dir = ROOT / "backend" / "app" / "runtime"
target = runtime_dir / "safe_provider_action_adapters.py"
test_file = ROOT / "test_safe_provider_action_adapters.py"

backup_dir = ROOT / "backups" / f"safe_provider_action_adapters_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)

if target.exists():
    shutil.copy2(target, backup_dir / target.name)

target.write_text(r'''
"""
Row 13 safe provider/action adapter layer.

Purpose:
- Prepare live provider/action adapter routing.
- Keep all external/live actions blocked unless explicitly owner-approved and live execution is enabled.
- Preserve owner/admin unrestricted internal execution without bypassing governance/security/audit controls.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


LIVE_ACTION_TYPES = {
    "live_provider_generation",
    "live_provider_action",
    "external_provider_execution",
    "shopify_live_action",
    "stripe_live_action",
    "email_live_send",
    "crm_live_write",
    "ad_platform_live_action",
}


SAFE_INTERNAL_ACTION_TYPES = {
    "admin_owner_execution",
    "internal_execution",
    "preview_generation",
    "draft_generation",
    "safe_draft_action",
}


@dataclass(frozen=True)
class ProviderActionDecision:
    success: bool
    action_type: str
    adapter: str
    execution_status: str
    live_action_allowed: bool
    external_action_performed: bool
    owner_approval_required: bool
    owner_approved: bool
    customer_safe: bool
    credential_values_exposed: bool
    message: str
    reason: str
    provider: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "action_type": self.action_type,
            "adapter": self.adapter,
            "execution_status": self.execution_status,
            "live_action_allowed": self.live_action_allowed,
            "external_action_performed": self.external_action_performed,
            "owner_approval_required": self.owner_approval_required,
            "owner_approved": self.owner_approved,
            "customer_safe": self.customer_safe,
            "credential_values_exposed": self.credential_values_exposed,
            "message": self.message,
            "reason": self.reason,
            "provider": self.provider,
        }


def classify_provider_action(payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    payload = payload or {}
    action_type = str(payload.get("action_type") or payload.get("execution_action") or "unknown").strip()
    provider = payload.get("provider") or payload.get("provider_id") or payload.get("service")

    is_live_action = action_type in LIVE_ACTION_TYPES
    is_safe_internal_action = action_type in SAFE_INTERNAL_ACTION_TYPES

    return {
        "action_type": action_type,
        "provider": provider,
        "is_live_action": is_live_action,
        "is_safe_internal_action": is_safe_internal_action,
        "requires_owner_approval": is_live_action,
    }


def evaluate_safe_provider_action(payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    payload = payload or {}
    classified = classify_provider_action(payload)

    action_type = classified["action_type"]
    provider = classified["provider"]
    is_live_action = classified["is_live_action"]
    is_safe_internal_action = classified["is_safe_internal_action"]

    owner_approved = bool(payload.get("owner_approved") or payload.get("approved_by_owner"))
    live_execution_enabled = bool(payload.get("live_execution_enabled"))
    credential_values_supplied = bool(payload.get("credential_values_supplied"))

    if is_live_action:
        if not owner_approved:
            return ProviderActionDecision(
                success=False,
                action_type=action_type,
                adapter="safe_provider_action_adapter",
                execution_status="blocked_owner_approval_required",
                live_action_allowed=False,
                external_action_performed=False,
                owner_approval_required=True,
                owner_approved=False,
                customer_safe=True,
                credential_values_exposed=False,
                message="Live provider/action execution blocked pending owner approval.",
                reason="owner_approval_required",
                provider=provider,
            ).to_dict()

        if not live_execution_enabled:
            return ProviderActionDecision(
                success=False,
                action_type=action_type,
                adapter="safe_provider_action_adapter",
                execution_status="blocked_live_execution_disabled",
                live_action_allowed=False,
                external_action_performed=False,
                owner_approval_required=True,
                owner_approved=True,
                customer_safe=True,
                credential_values_exposed=False,
                message="Live provider/action execution blocked because live execution is not enabled.",
                reason="live_execution_disabled",
                provider=provider,
            ).to_dict()

        return ProviderActionDecision(
            success=True,
            action_type=action_type,
            adapter="safe_provider_action_adapter",
            execution_status="live_action_ready_for_provider_adapter",
            live_action_allowed=True,
            external_action_performed=False,
            owner_approval_required=True,
            owner_approved=True,
            customer_safe=True,
            credential_values_exposed=False,
            message="Live provider/action passed safety checks and is ready for a concrete provider adapter.",
            reason="ready_for_provider_adapter",
            provider=provider,
        ).to_dict()

    if is_safe_internal_action:
        return ProviderActionDecision(
            success=True,
            action_type=action_type,
            adapter="safe_provider_action_adapter",
            execution_status="safe_internal_action_allowed",
            live_action_allowed=False,
            external_action_performed=False,
            owner_approval_required=False,
            owner_approved=owner_approved,
            customer_safe=True,
            credential_values_exposed=False,
            message="Safe internal action allowed without applying client limits or live provider execution.",
            reason="safe_internal_action",
            provider=provider,
        ).to_dict()

    return ProviderActionDecision(
        success=False,
        action_type=action_type,
        adapter="safe_provider_action_adapter",
        execution_status="unsupported_provider_action",
        live_action_allowed=False,
        external_action_performed=False,
        owner_approval_required=True,
        owner_approved=owner_approved,
        customer_safe=True,
        credential_values_exposed=False,
        message="Provider/action type is not recognised by the safe adapter layer.",
        reason="unsupported_action_type",
        provider=provider,
    ).to_dict()
'''.lstrip(), encoding="utf-8")

test_file.write_text(r'''
from backend.app.runtime.safe_provider_action_adapters import (
    classify_provider_action,
    evaluate_safe_provider_action,
)


def assert_true(condition, message):
    if not condition:
        raise AssertionError(message)


internal = evaluate_safe_provider_action({
    "action_type": "admin_owner_execution",
    "owner_approved": True,
})
assert_true(internal["success"] is True, "admin owner internal action should pass")
assert_true(internal["execution_status"] == "safe_internal_action_allowed", "wrong internal status")
assert_true(internal["external_action_performed"] is False, "must not perform external action")
assert_true(internal["credential_values_exposed"] is False, "must not expose credentials")

blocked = evaluate_safe_provider_action({
    "action_type": "live_provider_generation",
    "provider": "openai",
    "owner_approved": False,
    "live_execution_enabled": True,
})
assert_true(blocked["success"] is False, "unapproved live action should block")
assert_true(blocked["execution_status"] == "blocked_owner_approval_required", "wrong approval block status")
assert_true(blocked["external_action_performed"] is False, "must not perform external action")

disabled = evaluate_safe_provider_action({
    "action_type": "live_provider_generation",
    "provider": "openai",
    "owner_approved": True,
    "live_execution_enabled": False,
})
assert_true(disabled["success"] is False, "disabled live execution should block")
assert_true(disabled["execution_status"] == "blocked_live_execution_disabled", "wrong disabled status")

ready = evaluate_safe_provider_action({
    "action_type": "live_provider_generation",
    "provider": "openai",
    "owner_approved": True,
    "live_execution_enabled": True,
})
assert_true(ready["success"] is True, "approved live action should be adapter-ready")
assert_true(ready["execution_status"] == "live_action_ready_for_provider_adapter", "wrong ready status")
assert_true(ready["external_action_performed"] is False, "foundation layer must not call provider")

unknown = evaluate_safe_provider_action({"action_type": "unknown_action"})
assert_true(unknown["success"] is False, "unknown action should not pass")
assert_true(unknown["execution_status"] == "unsupported_provider_action", "wrong unknown status")

classified = classify_provider_action({"action_type": "live_provider_action", "provider": "runway"})
assert_true(classified["is_live_action"] is True, "live action classification failed")
assert_true(classified["requires_owner_approval"] is True, "live action must require approval")

print("SAFE_PROVIDER_ACTION_ADAPTERS_TEST_PASSED")
print("Internal:", internal)
print("Blocked:", blocked)
print("Disabled:", disabled)
print("Ready:", ready)
print("Unknown:", unknown)
'''.lstrip(), encoding="utf-8")

print("ROW13_SAFE_PROVIDER_ACTION_ADAPTERS_INSTALLED")
print(f"Backup folder: {backup_dir}")
print(f"Created/updated: {target}")
print(f"Created/updated: {test_file}")