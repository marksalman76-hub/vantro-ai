from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Header
from pydantic import BaseModel

from backend.app.media.production_storage_adapter import (
    prepare_upload_reference,
    storage_status,
)

router = APIRouter(prefix="/storage", tags=["storage"])


class PrepareUploadRequest(BaseModel):
    filename: str
    content_type: str = "application/octet-stream"


@router.get("/status")
def status():
    return storage_status()


@router.post("/prepare-upload")
def prepare_upload(payload: PrepareUploadRequest, x_tenant_id: Optional[str] = Header(default=None)):
    tenant_id = x_tenant_id or "client_demo_001"
    return prepare_upload_reference(
        tenant_id=tenant_id,
        filename=payload.filename,
        content_type=payload.content_type,
    )
