from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from backend.app.core.tenant_account_runtime import create_client_activation_invite


DATA_DIR = Path("backend/app/data")
DATA_DIR.mkdir(parents=True, exist_ok=True)

STATE_FILE = DATA_DIR / "admin_deployment_control_state.json"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_state() -> Dict[str, Any]:
    if not STATE_FILE.exists():
        STATE_FILE.write_text(json.dumps({"tenants": {}, "events": []}, indent=2), encoding="utf-8")

    try:
        data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        data = {"tenants": {}, "events": []}

    data.setdefault("tenants", {})
    data.setdefault("events", [])
    return data


def _save_state(data: Dict[str, Any]) -> None:
    STATE_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _event(event_type: str, tenant_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "event_id": f"admin_event_{uuid.uuid4().hex[:12]}",
        "event_type": event_type,
        "tenant_id": tenant_id,
        "payload": payload,
        "credential_values_exposed": False,
        "created_at": utc_now_iso(),
    }


def deploy_manual_client_system(payload: Dict[str, Any]) -> Dict[str, Any]:
    data = _load_state()

    company_name = str(payload.get("company_name") or "Manual Client").strip()
    contact_email = str(payload.get("contact_email") or payload.get("email") or "").strip().lower()
    package_name = str(payload.get("package") or payload.get("selected_package") or "Manual").strip()

    tenant_id = str(payload.get("tenant_id") or f"client_manual_{uuid.uuid4().hex[:10]}").strip()

    active_agents = payload.get("active_agents") or payload.get("paid_agents") or []

    if not isinstance(active_agents, list):
        active_agents = []

    unlimited_credits = bool(payload.get("unlimited_credits", True))

    credit_state = {
        "mode": "unlimited" if unlimited_credits else "allocated",
        "monthly_credits": None if unlimited_credits else int(payload.get("monthly_credits") or 0),
        "credits_used": 0,
        "credits_remaining": "unlimited" if unlimited_credits else int(payload.get("monthly_credits") or 0),
        "admin_override": unlimited_credits,
    }

    invite = create_client_activation_invite({
        "tenant_id": tenant_id,
        "email": contact_email,
        "company_name": company_name,
        "package": package_name,
        "active_agents": active_agents,
    })

    if not invite.get("success"):
        return {
            "success": False,
            "error": invite.get("error") or "activation_invite_failed",
            "credential_values_exposed": False,
        }

    activation_token = invite.get("activation_token")
    activation_link = invite.get("activation_path")

    tenant_record = {
        "tenant_id": tenant_id,
        "company_name": company_name,
        "contact_email": contact_email,
        "package": package_name,
        "active_agents": active_agents,
        "status": "deployed",
        "access_status": "active",
        "execution_status": "allowed",
        "unlimited_credits": unlimited_credits,
        "credit_state": credit_state,
        "activation_token": activation_token,
        "activation_link": activation_link,
        "activation_expires_at": invite.get("expires_at"),
        "created_at": utc_now_iso(),
        "updated_at": utc_now_iso(),
        "credential_values_exposed": False,
    }

    data["tenants"][tenant_id] = tenant_record
    data["events"].append(_event("manual_client_system_deployed", tenant_id, {
        "company_name": company_name,
        "package": package_name,
        "active_agent_count": len(active_agents),
        "unlimited_credits": unlimited_credits,
    }))

    _save_state(data)

    return {
        "success": True,
        "status": "manual_client_system_deployed",
        "tenant": tenant_record,
        "credential_values_exposed": False,
    }


def suspend_client_system(payload: Dict[str, Any]) -> Dict[str, Any]:
    data = _load_state()
    tenant_id = str(payload.get("tenant_id") or "").strip()
    reason = str(payload.get("reason") or "Admin suspended system.").strip()

    if not tenant_id:
        return {"success": False, "error": "tenant_id_required"}

    tenant = data["tenants"].get(tenant_id) or {
        "tenant_id": tenant_id,
        "created_at": utc_now_iso(),
    }

    tenant.update({
        "status": "suspended",
        "access_status": "suspended",
        "execution_status": "blocked",
        "suspension_reason": reason,
        "updated_at": utc_now_iso(),
        "credential_values_exposed": False,
    })

    data["tenants"][tenant_id] = tenant
    data["events"].append(_event("client_system_suspended", tenant_id, {"reason": reason}))

    _save_state(data)

    return {
        "success": True,
        "status": "client_system_suspended",
        "tenant": tenant,
        "execution_blocked": True,
        "credential_values_exposed": False,
    }


def cancel_client_system(payload: Dict[str, Any]) -> Dict[str, Any]:
    data = _load_state()
    tenant_id = str(payload.get("tenant_id") or "").strip()
    reason = str(payload.get("reason") or "Admin cancelled system.").strip()

    if not tenant_id:
        return {"success": False, "error": "tenant_id_required"}

    tenant = data["tenants"].get(tenant_id) or {
        "tenant_id": tenant_id,
        "created_at": utc_now_iso(),
    }

    tenant.update({
        "status": "cancelled",
        "access_status": "cancelled",
        "execution_status": "blocked",
        "cancellation_reason": reason,
        "updated_at": utc_now_iso(),
        "credential_values_exposed": False,
    })

    data["tenants"][tenant_id] = tenant
    data["events"].append(_event("client_system_cancelled", tenant_id, {"reason": reason}))

    _save_state(data)

    return {
        "success": True,
        "status": "client_system_cancelled",
        "tenant": tenant,
        "execution_blocked": True,
        "credential_values_exposed": False,
    }


def reactivate_client_system(payload: Dict[str, Any]) -> Dict[str, Any]:
    data = _load_state()
    tenant_id = str(payload.get("tenant_id") or "").strip()
    reason = str(payload.get("reason") or "Admin reactivated system.").strip()

    if not tenant_id:
        return {"success": False, "error": "tenant_id_required"}

    tenant = data["tenants"].get(tenant_id)

    if not tenant:
        return {"success": False, "error": "tenant_not_found"}

    tenant.update({
        "status": "active",
        "access_status": "active",
        "execution_status": "allowed",
        "reactivation_reason": reason,
        "updated_at": utc_now_iso(),
        "credential_values_exposed": False,
    })

    data["tenants"][tenant_id] = tenant
    data["events"].append(_event("client_system_reactivated", tenant_id, {"reason": reason}))

    _save_state(data)

    return {
        "success": True,
        "status": "client_system_reactivated",
        "tenant": tenant,
        "execution_allowed": True,
        "credential_values_exposed": False,
    }


def list_admin_deployments(limit: int = 50) -> Dict[str, Any]:
    data = _load_state()
    tenants = list(data.get("tenants", {}).values())
    events = data.get("events", [])[-limit:]

    tenants = sorted(tenants, key=lambda item: str(item.get("updated_at") or item.get("created_at") or ""), reverse=True)

    return {
        "success": True,
        "tenant_count": len(tenants),
        "tenants": tenants[:limit],
        "events": events,
        "credential_values_exposed": False,
    }


def admin_deployment_control_summary() -> Dict[str, Any]:
    data = _load_state()
    tenants = list(data.get("tenants", {}).values())

    return {
        "success": True,
        "manual_deploy_enabled": True,
        "unlimited_credit_mode_enabled": True,
        "suspend_enabled": True,
        "cancel_enabled": True,
        "reactivate_enabled": True,
        "tenant_count": len(tenants),
        "active_count": len([t for t in tenants if t.get("access_status") == "active"]),
        "suspended_count": len([t for t in tenants if t.get("access_status") == "suspended"]),
        "cancelled_count": len([t for t in tenants if t.get("access_status") == "cancelled"]),
        "credential_values_exposed": False,
    }
