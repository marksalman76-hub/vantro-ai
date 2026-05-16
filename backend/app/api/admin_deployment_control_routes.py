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
