from pathlib import Path
from datetime import datetime
import py_compile

ROOT = Path.cwd()
CORE = ROOT / "backend" / "app" / "core"
API = ROOT / "backend" / "app" / "api"
MAIN = ROOT / "backend" / "app" / "main.py"
BACKUPS = ROOT / "backups"

CORE.mkdir(parents=True, exist_ok=True)
API.mkdir(parents=True, exist_ok=True)
BACKUPS.mkdir(parents=True, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

RUNTIME = CORE / "admin_deployment_control_runtime.py"
ROUTES = API / "admin_deployment_control_routes.py"
TEST = ROOT / "test_step250_admin_deployment_control_layer.py"

for file in [RUNTIME, ROUTES, MAIN, TEST]:
    if file.exists():
        backup = BACKUPS / f"{file.stem}_before_step250_{timestamp}{file.suffix}"
        backup.write_text(file.read_text(encoding="utf-8"), encoding="utf-8")

RUNTIME.write_text(r'''
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


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

    activation_token = f"act_{uuid.uuid4().hex}"

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
        "activation_link": f"/activate?token={activation_token}",
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
'''.lstrip(), encoding="utf-8")

ROUTES.write_text(r'''
from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, Header

from backend.app.core.admin_deployment_control_runtime import (
    admin_deployment_control_summary,
    cancel_client_system,
    deploy_manual_client_system,
    list_admin_deployments,
    reactivate_client_system,
    suspend_client_system,
)

router = APIRouter()


def owner_admin(role: Optional[str]) -> bool:
    return role in {"owner", "admin", "system"}


@router.get("/admin/deployment-control/summary")
async def admin_deployment_control_summary_route(
    x_actor_role: Optional[str] = Header(default=None),
) -> Dict[str, Any]:
    if not owner_admin(x_actor_role):
        return {"success": False, "error": "owner_admin_required"}

    return admin_deployment_control_summary()


@router.get("/admin/deployment-control/list")
async def admin_deployment_control_list_route(
    x_actor_role: Optional[str] = Header(default=None),
    limit: int = 50,
) -> Dict[str, Any]:
    if not owner_admin(x_actor_role):
        return {"success": False, "error": "owner_admin_required"}

    return list_admin_deployments(limit=limit)


@router.post("/admin/deployment-control/manual-deploy")
async def admin_manual_deploy_route(
    payload: Dict[str, Any],
    x_actor_role: Optional[str] = Header(default=None),
) -> Dict[str, Any]:
    if not owner_admin(x_actor_role):
        return {"success": False, "error": "owner_admin_required"}

    return deploy_manual_client_system(payload)


@router.post("/admin/deployment-control/suspend")
async def admin_suspend_route(
    payload: Dict[str, Any],
    x_actor_role: Optional[str] = Header(default=None),
) -> Dict[str, Any]:
    if not owner_admin(x_actor_role):
        return {"success": False, "error": "owner_admin_required"}

    return suspend_client_system(payload)


@router.post("/admin/deployment-control/cancel")
async def admin_cancel_route(
    payload: Dict[str, Any],
    x_actor_role: Optional[str] = Header(default=None),
) -> Dict[str, Any]:
    if not owner_admin(x_actor_role):
        return {"success": False, "error": "owner_admin_required"}

    return cancel_client_system(payload)


@router.post("/admin/deployment-control/reactivate")
async def admin_reactivate_route(
    payload: Dict[str, Any],
    x_actor_role: Optional[str] = Header(default=None),
) -> Dict[str, Any]:
    if not owner_admin(x_actor_role):
        return {"success": False, "error": "owner_admin_required"}

    return reactivate_client_system(payload)
'''.lstrip(), encoding="utf-8")

main = MAIN.read_text(encoding="utf-8")

import_block = '''from backend.app.api.admin_deployment_control_routes import (
    router as admin_deployment_control_router,
)
'''

if "admin_deployment_control_router" not in main:
    anchor = "from backend.app.api.subscription_policy_routes import router as subscription_policy_router\n"
    if anchor not in main:
        raise RuntimeError("subscription_policy_router import anchor not found.")
    main = main.replace(anchor, anchor + import_block + "\n")

include_line = "app.include_router(admin_deployment_control_router)\n"

if include_line not in main:
    app_anchor = '''app = FastAPI(
    title="Ecommerce AI Agent Platform",
    version="1.1.0",
)
'''
    if app_anchor not in main:
        raise RuntimeError("FastAPI app anchor not found.")
    main = main.replace(app_anchor, app_anchor + "\n" + include_line)

MAIN.write_text(main, encoding="utf-8")

TEST.write_text(r'''
import json
import urllib.request
import urllib.error

BASE = "http://127.0.0.1:8000"


def request_json(path, method="GET", payload=None):
    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(
        BASE + path,
        data=data,
        headers={
            "Content-Type": "application/json",
            "x-actor-role": "owner",
            "x-tenant-id": "owner",
        },
        method=method,
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as res:
            return res.status, json.loads(res.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8")
        try:
            parsed = json.loads(body)
        except Exception:
            parsed = {"raw": body}
        return exc.code, parsed


tenant_id = "client_step250_manual_deploy"

summary_status, summary = request_json("/admin/deployment-control/summary")

deploy_status, deploy = request_json(
    "/admin/deployment-control/manual-deploy",
    method="POST",
    payload={
        "tenant_id": tenant_id,
        "company_name": "Step 250 Manual Deploy Client",
        "contact_email": "step250-client@example.com",
        "package": "Manual Unlimited",
        "active_agents": [
            "product_copywriting_agent",
            "ugc_creative_agent",
            "analytics_optimisation_agent",
        ],
        "unlimited_credits": True,
    },
)

suspend_status, suspend = request_json(
    "/admin/deployment-control/suspend",
    method="POST",
    payload={
        "tenant_id": tenant_id,
        "reason": "Step 250 suspend smoke test.",
    },
)

reactivate_status, reactivate = request_json(
    "/admin/deployment-control/reactivate",
    method="POST",
    payload={
        "tenant_id": tenant_id,
        "reason": "Step 250 reactivate smoke test.",
    },
)

cancel_status, cancel = request_json(
    "/admin/deployment-control/cancel",
    method="POST",
    payload={
        "tenant_id": tenant_id,
        "reason": "Step 250 cancel smoke test.",
    },
)

list_status, listed = request_json("/admin/deployment-control/list?limit=10")

combined = json.dumps({
    "summary": summary,
    "deploy": deploy,
    "suspend": suspend,
    "reactivate": reactivate,
    "cancel": cancel,
    "listed": listed,
}).lower()

tenant = deploy.get("tenant") or {}

checks = {
    "summary_route_ok": summary_status == 200 and summary.get("success") is True,
    "manual_deploy_ok": deploy_status == 200 and deploy.get("success") is True,
    "tenant_created": tenant.get("tenant_id") == tenant_id,
    "unlimited_credits_enabled": tenant.get("unlimited_credits") is True,
    "activation_link_created": bool(tenant.get("activation_link")),
    "active_agents_assigned": len(tenant.get("active_agents") or []) == 3,
    "suspend_ok": suspend_status == 200 and suspend.get("success") is True,
    "suspend_blocks_execution": suspend.get("execution_blocked") is True,
    "reactivate_ok": reactivate_status == 200 and reactivate.get("success") is True,
    "reactivate_allows_execution": reactivate.get("execution_allowed") is True,
    "cancel_ok": cancel_status == 200 and cancel.get("success") is True,
    "cancel_blocks_execution": cancel.get("execution_blocked") is True,
    "list_route_ok": list_status == 200 and listed.get("success") is True,
    "no_secret_values_exposed": all(secret not in combined for secret in [
        "sk_live_",
        "sk_test_",
        "whsec_",
        "postgresql://",
        "ecomagentsecure",
    ]),
}

print("STEP_250_ADMIN_DEPLOYMENT_CONTROL_LAYER_RESULTS")
for name, passed in checks.items():
    print(name, passed)

failed = [name for name, passed in checks.items() if not passed]

if failed:
    print("FAILED", failed)
    print(json.dumps({
        "summary": summary,
        "deploy": deploy,
        "suspend": suspend,
        "reactivate": reactivate,
        "cancel": cancel,
        "listed": listed,
    }, indent=2))
    raise SystemExit(1)

print("STEP_250_ADMIN_DEPLOYMENT_CONTROL_LAYER_OK")
'''.lstrip(), encoding="utf-8")

for file in [RUNTIME, ROUTES, MAIN, TEST]:
    py_compile.compile(str(file), doraise=True)

print("STEP_250_ADMIN_DEPLOYMENT_CONTROL_LAYER_INSTALLED")
print(f"Created/updated: {RUNTIME}")
print(f"Created/updated: {ROUTES}")
print(f"Updated: {MAIN}")
print(f"Created/updated: {TEST}")
print("STEP_250_OK")