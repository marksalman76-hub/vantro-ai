from __future__ import annotations

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
