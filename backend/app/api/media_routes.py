from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel

from backend.app.media.durable_media_store import (
    latest_deliverable,
    list_media_assets,
    media_persistence_status,
    persist_deliverable,
    register_media_asset,
)

router = APIRouter(prefix="/media", tags=["media"])


class RegisterAssetRequest(BaseModel):
    url: str
    title: str = ""
    asset_type: str = "media"
    source: str = "runtime"
    mime_type: str = ""
    size: str = ""
    metadata: Dict[str, Any] = {}


class PersistDeliverableRequest(BaseModel):
    execution_id: str = ""
    deliverable: Dict[str, Any]
    assets: list[Dict[str, Any]] = []


def _tenant(x_tenant_id: Optional[str]) -> str:
    tenant_id = x_tenant_id or "client_demo_001"
    if not tenant_id:
        raise HTTPException(status_code=400, detail="tenant_id_required")
    return tenant_id


@router.get("/status")
def media_status():
    return media_persistence_status()


@router.post("/assets/register")
def register_asset(payload: RegisterAssetRequest, x_tenant_id: Optional[str] = Header(default=None)):
    asset = register_media_asset(
        tenant_id=_tenant(x_tenant_id),
        url=payload.url,
        title=payload.title,
        asset_type=payload.asset_type,
        source=payload.source,
        mime_type=payload.mime_type,
        size=payload.size,
        metadata=payload.metadata,
    )
    if asset.get("success") is False or asset.get("production_fail_closed"):
        raise HTTPException(status_code=503, detail=asset)
    return {"success": True, "asset": asset}


@router.get("/assets")
def list_assets(x_tenant_id: Optional[str] = Header(default=None)):
    status = media_persistence_status()
    if status.get("production_fail_closed"):
        raise HTTPException(status_code=503, detail=status)
    assets = list_media_assets(_tenant(x_tenant_id))
    return {
        "success": True,
        "authority": "backend_canonical",
        "fallback_used": bool(status.get("fallback_used")),
        "dev_only": bool(status.get("dev_only")),
        "production_fail_closed": False,
        "assets": assets,
        "credential_values_exposed": False,
    }


@router.post("/deliverables/persist")
def persist(payload: PersistDeliverableRequest, x_tenant_id: Optional[str] = Header(default=None)):
    record = persist_deliverable(
        tenant_id=_tenant(x_tenant_id),
        execution_id=payload.execution_id,
        deliverable=payload.deliverable,
        assets=payload.assets,
    )
    if record.get("success") is False or record.get("production_fail_closed"):
        raise HTTPException(status_code=503, detail=record)
    return {"success": True, "record": record, "deliverable": record["deliverable"]}


@router.get("/deliverables/latest")
def latest(x_tenant_id: Optional[str] = Header(default=None)):
    record = latest_deliverable(_tenant(x_tenant_id))
    if isinstance(record, dict) and record.get("production_fail_closed"):
        raise HTTPException(status_code=503, detail=record)
    return {
        "success": True,
        "authority": "backend_canonical" if record else "backend_canonical",
        "fallback_used": bool(record.get("fallback_used")) if isinstance(record, dict) else False,
        "dev_only": bool(record.get("dev_only")) if isinstance(record, dict) else False,
        "production_fail_closed": False,
        "record": record,
        "deliverable": record.get("deliverable") if record else None,
        "credential_values_exposed": False,
    }
