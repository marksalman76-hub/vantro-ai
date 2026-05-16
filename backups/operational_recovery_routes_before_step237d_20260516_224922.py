from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, Header

from backend.app.core.operational_recovery_runtime import (
    discover_operational_artifacts,
    get_artifact_preview,
    operational_recovery_summary,
    prepare_execution_replay,
    prepare_execution_retry,
)

router = APIRouter()


def _owner_admin(role: Optional[str]) -> bool:
    return role in {"owner", "admin", "system"}


@router.get("/admin/operations/recovery-summary")
async def admin_recovery_summary(
    x_actor_role: Optional[str] = Header(default=None),
) -> Dict[str, Any]:
    if not _owner_admin(x_actor_role):
        return {"success": False, "error": "owner_admin_required"}

    return operational_recovery_summary()


@router.get("/admin/operations/artifacts")
async def admin_artifacts(
    x_actor_role: Optional[str] = Header(default=None),
    limit: int = 50,
) -> Dict[str, Any]:
    if not _owner_admin(x_actor_role):
        return {"success": False, "error": "owner_admin_required"}

    return discover_operational_artifacts(limit=limit)


@router.get("/admin/operations/artifact-preview")
async def admin_artifact_preview(
    relative_path: str,
    x_actor_role: Optional[str] = Header(default=None),
) -> Dict[str, Any]:
    if not _owner_admin(x_actor_role):
        return {"success": False, "error": "owner_admin_required"}

    return get_artifact_preview(relative_path)


@router.post("/admin/operations/prepare-replay")
async def admin_prepare_replay(
    payload: Dict[str, Any],
    x_actor_role: Optional[str] = Header(default=None),
) -> Dict[str, Any]:
    if not _owner_admin(x_actor_role):
        return {"success": False, "error": "owner_admin_required"}

    return prepare_execution_replay(payload)


@router.post("/admin/operations/prepare-retry")
async def admin_prepare_retry(
    payload: Dict[str, Any],
    x_actor_role: Optional[str] = Header(default=None),
) -> Dict[str, Any]:
    if not _owner_admin(x_actor_role):
        return {"success": False, "error": "owner_admin_required"}

    return prepare_execution_retry(payload)
