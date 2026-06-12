from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
RUNTIME_DIR = ROOT / "backend" / "app" / "runtime"
TARGET = RUNTIME_DIR / "portal_authority_context.py"
TEST = ROOT / "test_portal_authority_context.py"
BACKUP_DIR = ROOT / "backups" / f"portal_authority_context_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

if TARGET.exists():
    shutil.copy2(TARGET, BACKUP_DIR / TARGET.name)

TARGET.write_text(r'''from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional


ADMIN_PORTAL = "admin"
CLIENT_PORTAL = "client"


@dataclass
class PortalAuthorityContext:
    portal_mode: str
    actor_id: str = ""
    tenant_id: str = ""
    client_id: str = ""
    role: str = ""
    is_owner: bool = False
    is_admin: bool = False
    is_client: bool = False

    unrestricted_execution: bool = False
    package_governed: bool = True
    credit_governed: bool = True
    approval_required: bool = True

    can_view_provider_diagnostics: bool = False
    can_view_provider_details: bool = False
    can_view_internal_config: bool = False
    can_view_raw_provider_errors: bool = False

    can_retry_jobs: bool = False
    can_requeue_jobs: bool = False
    can_cancel_jobs: bool = False
    can_assign_credits: bool = False
    can_issue_refunds: bool = False
    can_view_infrastructure_status: bool = False
    can_view_full_audit_log: bool = False

    client_safe_output_only: bool = True
    hide_provider_secrets: bool = True
    hide_internal_diagnostics: bool = True
    own_tenant_only: bool = True
    privacy_safe_uploads_required: bool = True


def normalise_portal_mode(value: Any) -> str:
    raw = str(value or "").strip().lower()
    if raw in {"admin", "owner", "admin_portal", "owner_portal"}:
        return ADMIN_PORTAL
    return CLIENT_PORTAL


def build_portal_authority_context(payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    payload = dict(payload or {})
    portal_mode = normalise_portal_mode(
        payload.get("portal_mode")
        or payload.get("mode")
        or payload.get("source_portal")
        or payload.get("requested_from_portal")
    )

    role = str(payload.get("role") or payload.get("actor_role") or "").strip().lower()
    is_owner = bool(payload.get("is_owner") or role == "owner")
    is_admin = bool(payload.get("is_admin") or role in {"admin", "owner"} or portal_mode == ADMIN_PORTAL)
    is_client = portal_mode == CLIENT_PORTAL and not is_admin

    if portal_mode == ADMIN_PORTAL:
        ctx = PortalAuthorityContext(
            portal_mode=ADMIN_PORTAL,
            actor_id=str(payload.get("actor_id") or payload.get("admin_id") or ""),
            tenant_id=str(payload.get("tenant_id") or ""),
            client_id=str(payload.get("client_id") or ""),
            role=role or ("owner" if is_owner else "admin"),
            is_owner=is_owner or True,
            is_admin=True,
            is_client=False,
            unrestricted_execution=True,
            package_governed=False,
            credit_governed=False,
            approval_required=False,
            can_view_provider_diagnostics=True,
            can_view_provider_details=True,
            can_view_internal_config=True,
            can_view_raw_provider_errors=True,
            can_retry_jobs=True,
            can_requeue_jobs=True,
            can_cancel_jobs=True,
            can_assign_credits=True,
            can_issue_refunds=True,
            can_view_infrastructure_status=True,
            can_view_full_audit_log=True,
            client_safe_output_only=False,
            hide_provider_secrets=True,
            hide_internal_diagnostics=False,
            own_tenant_only=False,
            privacy_safe_uploads_required=True,
        )
    else:
        ctx = PortalAuthorityContext(
            portal_mode=CLIENT_PORTAL,
            actor_id=str(payload.get("actor_id") or payload.get("client_id") or ""),
            tenant_id=str(payload.get("tenant_id") or payload.get("client_id") or ""),
            client_id=str(payload.get("client_id") or payload.get("actor_id") or ""),
            role=role or "client",
            is_owner=False,
            is_admin=False,
            is_client=True,
            unrestricted_execution=False,
            package_governed=True,
            credit_governed=True,
            approval_required=True,
            can_view_provider_diagnostics=False,
            can_view_provider_details=False,
            can_view_internal_config=False,
            can_view_raw_provider_errors=False,
            can_retry_jobs=False,
            can_requeue_jobs=False,
            can_cancel_jobs=False,
            can_assign_credits=False,
            can_issue_refunds=False,
            can_view_infrastructure_status=False,
            can_view_full_audit_log=False,
            client_safe_output_only=True,
            hide_provider_secrets=True,
            hide_internal_diagnostics=True,
            own_tenant_only=True,
            privacy_safe_uploads_required=True,
        )

    data = asdict(ctx)
    data["customer_safe"] = True
    data["credential_values_exposed"] = False
    data["provider_secret_values_visible"] = False
    return data


def redact_for_portal(payload: Dict[str, Any], authority: Dict[str, Any]) -> Dict[str, Any]:
    """
    Return portal-safe payload without leaking provider secrets/internal diagnostics.

    Admin can see diagnostics and provider details, but raw secret values are always removed.
    Client receives client-safe output only.
    """
    data = dict(payload or {})
    authority = dict(authority or {})

    secret_like_keys = {
        "api_key",
        "secret",
        "token",
        "authorization",
        "provider_api_key",
        "openai_api_key",
        "runway_api_key",
        "elevenlabs_api_key",
        "stripe_secret_key",
    }

    def remove_secret_keys(value: Any) -> Any:
        if isinstance(value, dict):
            cleaned = {}
            for key, item in value.items():
                key_l = str(key).lower()
                if any(secret_key in key_l for secret_key in secret_like_keys):
                    cleaned[key] = "[redacted]"
                else:
                    cleaned[key] = remove_secret_keys(item)
            return cleaned
        if isinstance(value, list):
            return [remove_secret_keys(item) for item in value]
        return value

    data = remove_secret_keys(data)

    if not authority.get("can_view_provider_diagnostics"):
        for key in [
            "provider_diagnostics",
            "internal_diagnostics",
            "raw_provider_response",
            "raw_provider_error",
            "provider_request",
            "provider_headers",
            "internal_config",
            "debug",
            "trace",
        ]:
            data.pop(key, None)

    if authority.get("client_safe_output_only"):
        data["customer_safe"] = True
        data["credential_values_exposed"] = False
        data["internal_config_exposed"] = False
        data["provider_secret_values_visible"] = False

    return data


def enforce_execution_authority(request: Dict[str, Any], authority: Dict[str, Any]) -> Dict[str, Any]:
    """
    Non-final enforcement foundation.

    This does not debit credits or approve jobs yet. It returns the authority decision that
    future AWS API/worker routes must honor.
    """
    request = dict(request or {})
    authority = dict(authority or {})

    if authority.get("unrestricted_execution"):
        return {
            "allowed": True,
            "reason": "admin_owner_unrestricted_execution",
            "requires_credit_check": False,
            "requires_package_check": False,
            "requires_owner_approval": False,
            "portal_mode": authority.get("portal_mode"),
            "customer_safe": True,
            "credential_values_exposed": False,
        }

    return {
        "allowed": True,
        "reason": "client_execution_requires_governance",
        "requires_credit_check": True,
        "requires_package_check": True,
        "requires_owner_approval": bool(request.get("owner_approval_required", True)),
        "portal_mode": authority.get("portal_mode"),
        "customer_safe": True,
        "credential_values_exposed": False,
    }
''', encoding="utf-8")

TEST.write_text(r'''from backend.app.runtime.portal_authority_context import (
    build_portal_authority_context,
    enforce_execution_authority,
    redact_for_portal,
)


def main():
    admin = build_portal_authority_context({
        "portal_mode": "admin",
        "role": "owner",
        "actor_id": "owner_test",
    })

    assert admin["portal_mode"] == "admin"
    assert admin["unrestricted_execution"] is True
    assert admin["package_governed"] is False
    assert admin["credit_governed"] is False
    assert admin["approval_required"] is False
    assert admin["can_view_provider_diagnostics"] is True
    assert admin["can_retry_jobs"] is True
    assert admin["can_assign_credits"] is True
    assert admin["hide_provider_secrets"] is True

    client = build_portal_authority_context({
        "portal_mode": "client",
        "client_id": "client_test",
    })

    assert client["portal_mode"] == "client"
    assert client["unrestricted_execution"] is False
    assert client["package_governed"] is True
    assert client["credit_governed"] is True
    assert client["approval_required"] is True
    assert client["can_view_provider_diagnostics"] is False
    assert client["can_retry_jobs"] is False
    assert client["can_assign_credits"] is False
    assert client["client_safe_output_only"] is True

    admin_decision = enforce_execution_authority({"owner_approval_required": True}, admin)
    assert admin_decision["allowed"] is True
    assert admin_decision["requires_credit_check"] is False
    assert admin_decision["requires_package_check"] is False
    assert admin_decision["requires_owner_approval"] is False

    client_decision = enforce_execution_authority({"owner_approval_required": True}, client)
    assert client_decision["allowed"] is True
    assert client_decision["requires_credit_check"] is True
    assert client_decision["requires_package_check"] is True
    assert client_decision["requires_owner_approval"] is True

    payload = {
        "status": "completed",
        "api_key": "secret-value",
        "provider_diagnostics": {"runway": "details"},
        "raw_provider_error": "debug error",
        "asset_url": "https://example.com/final.mp4",
    }

    admin_view = redact_for_portal(payload, admin)
    assert admin_view["api_key"] == "[redacted]"
    assert "provider_diagnostics" in admin_view
    assert "raw_provider_error" in admin_view

    client_view = redact_for_portal(payload, client)
    assert client_view["api_key"] == "[redacted]"
    assert "provider_diagnostics" not in client_view
    assert "raw_provider_error" not in client_view
    assert client_view["asset_url"] == "https://example.com/final.mp4"
    assert client_view["credential_values_exposed"] is False

    print("PORTAL_AUTHORITY_CONTEXT_TEST_PASSED")
    print("admin_reason:", admin_decision["reason"])
    print("client_reason:", client_decision["reason"])


if __name__ == "__main__":
    main()
''', encoding="utf-8")

print("PORTAL_AUTHORITY_CONTEXT_INSTALLED")
print(f"Updated: {TARGET}")
print(f"Created test: {TEST}")
print(f"Backup folder: {BACKUP_DIR}")