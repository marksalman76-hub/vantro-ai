from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
APP = ROOT / "backend" / "app"
MEDIA = APP / "media"
API = APP / "api"
BACKUPS = ROOT / "backups"

for p in [MEDIA, API, BACKUPS]:
    p.mkdir(parents=True, exist_ok=True)

storage_adapter = r'''from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class StorageConfig:
    provider: str
    bucket: str
    public_base_url: str
    configured: bool
    mode: str


def get_storage_config() -> StorageConfig:
    provider = os.getenv("MEDIA_STORAGE_PROVIDER", "local_registry").strip().lower()
    bucket = os.getenv("MEDIA_STORAGE_BUCKET", "").strip()
    public_base_url = os.getenv("MEDIA_STORAGE_PUBLIC_BASE_URL", "").strip()

    configured = provider in {"supabase", "r2", "s3"} and bool(bucket)

    return StorageConfig(
        provider=provider,
        bucket=bucket,
        public_base_url=public_base_url,
        configured=configured,
        mode="production_object_storage_ready" if configured else "local_registry_fallback",
    )


def storage_status() -> Dict[str, Any]:
    config = get_storage_config()
    return {
        "success": True,
        "provider": config.provider,
        "bucket_configured": bool(config.bucket),
        "public_base_url_configured": bool(config.public_base_url),
        "configured": config.configured,
        "mode": config.mode,
        "supported_providers": ["supabase", "r2", "s3"],
        "fallback": "durable_media_registry",
        "required_env": [
            "MEDIA_STORAGE_PROVIDER",
            "MEDIA_STORAGE_BUCKET",
            "MEDIA_STORAGE_PUBLIC_BASE_URL",
        ],
        "optional_env": [
            "MEDIA_STORAGE_ACCESS_KEY",
            "MEDIA_STORAGE_SECRET_KEY",
            "MEDIA_STORAGE_REGION",
            "SUPABASE_URL",
            "SUPABASE_SERVICE_ROLE_KEY",
        ],
    }


def build_public_asset_url(object_key: str) -> str:
    config = get_storage_config()
    clean_key = object_key.lstrip("/")

    if config.public_base_url:
        return f"{config.public_base_url.rstrip('/')}/{clean_key}"

    return f"local://media/{clean_key}"


def prepare_upload_reference(*, tenant_id: str, filename: str, content_type: str = "application/octet-stream") -> Dict[str, Any]:
    config = get_storage_config()
    clean_filename = filename.replace("\\", "/").split("/")[-1]
    object_key = f"tenants/{tenant_id}/media/{clean_filename}"

    return {
        "success": True,
        "storage_mode": config.mode,
        "provider": config.provider,
        "tenant_id": tenant_id,
        "filename": clean_filename,
        "content_type": content_type,
        "object_key": object_key,
        "public_url": build_public_asset_url(object_key),
        "upload_ready": config.configured,
        "fallback_registry_ready": True,
        "note": "Object storage credentials are not stored in code. Configure environment variables for Supabase/R2/S3.",
    }
'''

storage_routes = r'''from __future__ import annotations

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
'''

test_script = r'''import json

from backend.app.media.production_storage_adapter import (
    build_public_asset_url,
    prepare_upload_reference,
    storage_status,
)

status = storage_status()
upload = prepare_upload_reference(
    tenant_id="client_batch_g_storage_test",
    filename="campaign-preview.png",
    content_type="image/png",
)
public_url = build_public_asset_url("tenants/client_batch_g_storage_test/media/campaign-preview.png")

results = {
    "status_success": status.get("success") is True,
    "fallback_ready": status.get("fallback") == "durable_media_registry",
    "supported_supabase": "supabase" in status.get("supported_providers", []),
    "supported_r2": "r2" in status.get("supported_providers", []),
    "supported_s3": "s3" in status.get("supported_providers", []),
    "upload_reference_success": upload.get("success") is True,
    "object_key_created": upload.get("object_key") == "tenants/client_batch_g_storage_test/media/campaign-preview.png",
    "public_url_created": bool(public_url),
    "upload_ready_or_fallback": upload.get("upload_ready") is True or upload.get("fallback_registry_ready") is True,
    "status": status,
    "upload": upload,
    "public_url": public_url,
}

print("BATCH_G_PRODUCTION_STORAGE_RESULTS")
print(json.dumps(results, indent=2))

required = [
    "status_success",
    "fallback_ready",
    "supported_supabase",
    "supported_r2",
    "supported_s3",
    "upload_reference_success",
    "object_key_created",
    "public_url_created",
    "upload_ready_or_fallback",
]

if not all(results[k] for k in required):
    raise SystemExit("BATCH_G_PRODUCTION_STORAGE_FAILED")

print("BATCH_G_PRODUCTION_STORAGE_OK")
'''

(MEDIA / "production_storage_adapter.py").write_text(storage_adapter, encoding="utf-8")
(API / "storage_routes.py").write_text(storage_routes, encoding="utf-8")
(ROOT / "test_batch_g_production_storage_adapter.py").write_text(test_script, encoding="utf-8")

main = APP / "main.py"
if main.exists():
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    backup = BACKUPS / f"main_before_batch_g_storage_{stamp}.py"
    backup.write_text(main.read_text(encoding="utf-8"), encoding="utf-8")

    text = main.read_text(encoding="utf-8")

    if "backend.app.api.storage_routes import router as storage_router" not in text:
        text = "from backend.app.api.storage_routes import router as storage_router\n" + text

    if "app.include_router(storage_router)" not in text:
        text = text.rstrip() + "\n\n# Batch G production storage routes\napp.include_router(storage_router)\n"

    main.write_text(text, encoding="utf-8")
    print(f"Updated main.py")
    print(f"Backup: {backup}")

print("BATCH_G_PRODUCTION_STORAGE_ADAPTER_INSTALLED")
print("Created: backend\\app\\media\\production_storage_adapter.py")
print("Created: backend\\app\\api\\storage_routes.py")
print("Created: test_batch_g_production_storage_adapter.py")