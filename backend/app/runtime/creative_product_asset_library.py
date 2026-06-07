from __future__ import annotations

import base64
import hashlib
import json
import mimetypes
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from backend.app.runtime.canonical_product_asset_metadata_runtime import (
    delete_product_asset as canonical_delete_product_asset,
    ensure_product_asset_metadata_tables,
    get_product_asset as canonical_get_product_asset,
    get_product_asset_metadata_summary,
    list_product_assets as canonical_list_product_assets,
    record_product_asset,
    record_product_asset_event,
)

try:
    from backend.app.runtime.supabase_creative_storage import (
        supabase_enabled,
        storage_status as supabase_storage_status,
        product_asset_bucket,
        upload_bytes_to_supabase,
        download_json_from_supabase,
        upload_json_to_supabase,
    )
except Exception:
    supabase_enabled = lambda: False
    supabase_storage_status = lambda: {"durable_storage_ready": False}
    product_asset_bucket = lambda: "creative-product-assets"
    upload_bytes_to_supabase = None
    download_json_from_supabase = None
    upload_json_to_supabase = None


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_ASSET_ROOT = ROOT / "runtime_outputs" / "creative_product_assets"
ASSET_ROOT = Path(os.getenv("CREATIVE_ASSET_PERSISTENCE_DIR", str(DEFAULT_ASSET_ROOT)))
REGISTRY_PATH = ASSET_ROOT / "creative_product_asset_registry.json"
SUPABASE_REGISTRY_OBJECT_KEY = "registries/creative_product_asset_registry.json"

ALLOWED_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".webp", ".gif",
    ".mp4", ".mov", ".webm",
    ".pdf", ".docx", ".pptx", ".txt", ".md",
}

ASSET_TYPE_ALIASES = {
    "product": "product_image",
    "product_image": "product_image",
    "product_video": "product_video",
    "logo": "logo",
    "brand": "brand_asset",
    "brand_asset": "brand_asset",
    "brand_guide": "brand_guideline",
    "brand_guideline": "brand_guideline",
    "reference": "reference_asset",
    "reference_video": "reference_video",
    "competitor": "competitor_reference",
    "brief": "creative_brief",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_text(value: Any, fallback: str = "") -> str:
    text = str(value or "").strip()
    return text or fallback


def _safe_slug(value: Any, fallback: str = "asset") -> str:
    raw = _safe_text(value, fallback)
    safe = "".join(ch if ch.isalnum() or ch in ("-", "_", ".") else "_" for ch in raw)
    return safe[:160] or fallback


def _normalise_asset_type(asset_type: str) -> str:
    key = _safe_text(asset_type, "reference_asset").lower().replace(" ", "_")
    return ASSET_TYPE_ALIASES.get(key, key or "reference_asset")


def _tenant_dir(tenant_id: str, asset_type: str) -> Path:
    safe_tenant = _safe_slug(tenant_id or "owner_admin", "owner_admin")
    safe_type = _safe_slug(asset_type or "reference_asset", "reference_asset")
    path = ASSET_ROOT / safe_tenant / safe_type
    path.mkdir(parents=True, exist_ok=True)
    return path


def _blank_registry() -> Dict[str, Any]:
    return {"assets": [], "updated_at": _now(), "credential_values_exposed": False}


def _load_registry() -> Dict[str, Any]:
    if supabase_enabled() and download_json_from_supabase is not None:
        result = download_json_from_supabase(
            bucket=product_asset_bucket(),
            object_key=SUPABASE_REGISTRY_OBJECT_KEY,
            fallback=_blank_registry(),
        )
        data = result.get("json")
        if isinstance(data, dict):
            data.setdefault("assets", [])
            return data

    ASSET_ROOT.mkdir(parents=True, exist_ok=True)
    if not REGISTRY_PATH.exists():
        return _blank_registry()
    try:
        data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return _blank_registry()
        data.setdefault("assets", [])
        return data
    except Exception:
        return _blank_registry()


def _save_registry(data: Dict[str, Any]) -> None:
    data["updated_at"] = _now()
    data["credential_values_exposed"] = False

    if supabase_enabled() and upload_json_to_supabase is not None:
        upload_json_to_supabase(
            bucket=product_asset_bucket(),
            object_key=SUPABASE_REGISTRY_OBJECT_KEY,
            payload=data,
        )

    ASSET_ROOT.mkdir(parents=True, exist_ok=True)
    REGISTRY_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _hash_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _safe_metadata(metadata: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    safe: Dict[str, Any] = {}
    for key, value in (metadata or {}).items():
        lowered = str(key).lower()
        if "secret" in lowered or "token" in lowered or "password" in lowered or "key" in lowered:
            continue
        safe[str(key)] = value
    return safe


def _is_production() -> bool:
    values = [
        os.getenv("ENVIRONMENT"),
        os.getenv("APP_ENV"),
        os.getenv("FASTAPI_ENV"),
        os.getenv("NODE_ENV"),
        os.getenv("RENDER"),
        os.getenv("VERCEL_ENV"),
        os.getenv("PRODUCTION"),
    ]
    return any(str(value or "").strip().lower() in {"1", "true", "prod", "production"} for value in values)


def _canonical_unavailable_response(readiness: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "success": False,
        "layer": "creative_product_asset_library",
        "status": readiness.get("status") or "canonical_product_asset_metadata_unavailable",
        "authority": "backend_canonical",
        "production_fail_closed": bool(readiness.get("production_fail_closed")),
        "credential_values_exposed": False,
        "customer_safe": True,
        "error": readiness.get("reason") or readiness.get("error") or "canonical_product_asset_metadata_unavailable",
    }


def _merge_authority(payload: Dict[str, Any], canonical: Dict[str, Any]) -> Dict[str, Any]:
    merged = dict(payload)
    merged["authority"] = "backend_canonical"
    merged["fallback_used"] = bool(canonical.get("dev_only"))
    merged["dev_only"] = bool(canonical.get("dev_only"))
    merged["production_fail_closed"] = False
    merged["canonical_storage_mode"] = canonical.get("storage_mode")
    merged["credential_values_exposed"] = False
    merged["customer_safe"] = True
    return merged


def upload_creative_product_asset(
    *,
    tenant_id: str,
    filename: str,
    content_base64: str,
    asset_type: str = "reference_asset",
    uploaded_by: str = "owner_admin",
    campaign_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    tenant_id = _safe_text(tenant_id, "owner_admin")
    asset_type = _normalise_asset_type(asset_type)
    original_filename = _safe_text(filename, "uploaded_asset")
    safe_filename = _safe_slug(original_filename, "uploaded_asset")

    extension = Path(safe_filename).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        return {
            "success": False,
            "status": "blocked_unsupported_file_type",
            "filename": original_filename,
            "extension": extension,
            "allowed_extensions": sorted(ALLOWED_EXTENSIONS),
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    try:
        content = base64.b64decode(content_base64, validate=True)
    except Exception as exc:
        return {
            "success": False,
            "status": "invalid_base64_upload",
            "error": str(exc),
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    if len(content) == 0:
        return {
            "success": False,
            "status": "empty_file_blocked",
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    max_bytes = int(os.getenv("CREATIVE_PRODUCT_ASSET_MAX_BYTES", str(50 * 1024 * 1024)))
    if len(content) > max_bytes:
        return {
            "success": False,
            "status": "file_too_large",
            "size_bytes": len(content),
            "max_bytes": max_bytes,
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    readiness = ensure_product_asset_metadata_tables()
    if not readiness.get("success"):
        return _canonical_unavailable_response(readiness)

    production = _is_production()
    if production and not supabase_enabled():
        return {
            "success": False,
            "layer": "creative_product_asset_library",
            "status": "object_storage_unavailable",
            "authority": "backend_canonical",
            "production_fail_closed": True,
            "credential_values_exposed": False,
            "customer_safe": True,
            "error": "Product asset uploads require durable object storage in production.",
        }

    asset_id = f"product_asset_{uuid.uuid4().hex[:18]}"
    mime_type = mimetypes.guess_type(safe_filename)[0] or "application/octet-stream"

    stored_filename = f"{asset_id}_{safe_filename}"
    stored_path: Optional[Path] = None
    if not production:
        asset_dir = _tenant_dir(tenant_id, asset_type)
        stored_path = asset_dir / stored_filename
        stored_path.write_bytes(content)

    object_key = f"tenants/{_safe_slug(tenant_id)}/{asset_type}/{stored_filename}"
    storage_upload = None
    storage_url = None

    if supabase_enabled() and upload_bytes_to_supabase is not None:
        storage_upload = upload_bytes_to_supabase(
            bucket=product_asset_bucket(),
            object_key=object_key,
            content=content,
            content_type=mime_type,
        )
        if storage_upload.get("success"):
            storage_url = storage_upload.get("public_url")

    if production and not storage_url:
        return {
            "success": False,
            "layer": "creative_product_asset_library",
            "status": "object_storage_upload_failed",
            "authority": "backend_canonical",
            "production_fail_closed": True,
            "storage_upload": storage_upload,
            "credential_values_exposed": False,
            "customer_safe": True,
            "error": "Product asset upload did not receive a durable customer-safe storage URL.",
        }

    provider = "supabase" if storage_url else "local_runtime_fallback"
    bucket = product_asset_bucket() if storage_url else None
    safe_ready = bool(storage_url)
    record = {
        "asset_id": asset_id,
        "tenant_id": tenant_id,
        "asset_type": asset_type,
        "filename": original_filename,
        "original_filename": original_filename,
        "stored_filename": stored_filename,
        "stored_path": str(stored_path) if stored_path else None,
        "storage_provider": provider,
        "storage_bucket": bucket,
        "storage_object_key": object_key if storage_url else None,
        "public_url": storage_url,
        "preview_url": storage_url,
        "download_url": storage_url,
        "mime_type": mime_type,
        "size_bytes": len(content),
        "sha256": _hash_bytes(content),
        "uploaded_by": _safe_text(uploaded_by, "owner_admin"),
        "campaign_id": campaign_id,
        "metadata": _safe_metadata(metadata),
        "preview_ready": safe_ready,
        "download_ready": safe_ready,
        "customer_safe": True,
        "credential_values_exposed": False,
        "created_at": _now(),
        "updated_at": _now(),
    }

    canonical = record_product_asset(
        asset_id=asset_id,
        tenant_id=tenant_id,
        project_id=campaign_id or "default_project",
        uploaded_by=_safe_text(uploaded_by, "owner_admin"),
        asset_type=asset_type,
        filename=original_filename,
        original_filename=original_filename,
        mime_type=mime_type,
        byte_size=len(content),
        checksum=record["sha256"],
        storage_provider=provider,
        bucket=bucket or "",
        object_key=object_key if storage_url else "",
        local_path=str(stored_path) if stored_path else "",
        preview_url=storage_url or "",
        download_url=storage_url or "",
        preview_ready=safe_ready,
        download_ready=safe_ready,
        status="uploaded",
        approval_status="pending_review",
        source_runtime="creative_product_asset_library",
        payload={
            **_safe_metadata(metadata),
            "stored_filename": stored_filename,
            "storage_upload_success": bool(storage_url),
        },
    )
    if not canonical.get("success"):
        return _canonical_unavailable_response(canonical)

    record = canonical.get("asset") if isinstance(canonical.get("asset"), dict) else record

    registry = _load_registry()
    assets = registry.get("assets", [])
    assets.insert(0, record)
    registry["assets"] = assets[:1000]
    _save_registry(registry)

    return {
        "success": True,
        "status": "creative_product_asset_uploaded",
        "asset": record,
        "asset_id": asset_id,
        "storage_upload": storage_upload,
        "storage_provider": record.get("storage_provider"),
        "durable_storage_ready": record.get("storage_provider") == "supabase",
        "authority": "backend_canonical",
        "fallback_used": False,
        "dev_only": False,
        "production_fail_closed": False,
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def list_creative_product_assets(
    *,
    tenant_id: Optional[str] = None,
    asset_type: Optional[str] = None,
    campaign_id: Optional[str] = None,
    limit: int = 100,
) -> Dict[str, Any]:
    canonical = canonical_list_product_assets(
        tenant_id=tenant_id or "",
        project_id=campaign_id or "",
        asset_type=_normalise_asset_type(asset_type) if asset_type else "",
        limit=limit,
    )
    if not canonical.get("success"):
        return _canonical_unavailable_response(canonical)

    records = [r for r in canonical.get("assets", []) if isinstance(r, dict)]
    storage = supabase_storage_status()

    return _merge_authority({
        "success": True,
        "layer": "creative_product_asset_library",
        "status": "ready",
        "asset_count": len(records),
        "total_asset_count": canonical.get("total_asset_count", len(records)),
        "assets": records,
        "supported_asset_types": sorted(set(ASSET_TYPE_ALIASES.values())),
        "allowed_extensions": sorted(ALLOWED_EXTENSIONS),
        "storage_provider": storage.get("storage_provider"),
        "durable_storage_ready": storage.get("durable_storage_ready"),
        "storage_bucket": product_asset_bucket(),
        "credential_values_exposed": False,
        "customer_safe": True,
        "verified_at": _now(),
    }, canonical)


def get_creative_product_asset(asset_id: str) -> Dict[str, Any]:
    canonical = canonical_get_product_asset(asset_id)
    if not canonical.get("success"):
        if canonical.get("production_fail_closed"):
            return _canonical_unavailable_response(canonical)
        return {
            "success": False,
            "status": "not_found",
            "asset_id": asset_id,
            "authority": "backend_canonical",
            "fallback_used": bool(canonical.get("dev_only")),
            "dev_only": bool(canonical.get("dev_only")),
            "production_fail_closed": False,
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    record = canonical.get("asset") or canonical.get("record")
    if isinstance(record, dict):
        return _merge_authority({
                "success": True,
                "status": "found",
                "asset": record,
                "credential_values_exposed": False,
                "customer_safe": True,
            }, canonical)

    return {
        "success": False,
        "status": "not_found",
        "asset_id": asset_id,
        "authority": "backend_canonical",
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def delete_creative_product_asset(
    *,
    asset_id: str,
    tenant_id: Optional[str] = None,
) -> Dict[str, Any]:
    existing = canonical_get_product_asset(asset_id, tenant_id=tenant_id or "")
    if not existing.get("success"):
        if existing.get("production_fail_closed"):
            return _canonical_unavailable_response(existing)
        return {
            "success": False,
            "status": "not_found",
            "asset_id": asset_id,
            "authority": "backend_canonical",
            "fallback_used": bool(existing.get("dev_only")),
            "dev_only": bool(existing.get("dev_only")),
            "production_fail_closed": False,
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    deleted_asset = existing.get("asset") or {}
    deleted = canonical_delete_product_asset(asset_id=asset_id, tenant_id=tenant_id or "", actor_role="owner_admin")
    if not deleted.get("success"):
        return _canonical_unavailable_response(deleted)

    stored_path = Path(str(deleted_asset.get("stored_path") or deleted_asset.get("local_path") or ""))
    if stored_path.exists() and stored_path.is_file():
        try:
            stored_path.unlink()
        except Exception:
            pass

    try:
        registry = _load_registry()
        registry["assets"] = [
            record
            for record in registry.get("assets", [])
            if not (isinstance(record, dict) and record.get("asset_id") == asset_id and (not tenant_id or record.get("tenant_id") == tenant_id))
        ]
        _save_registry(registry)
    except Exception:
        pass

    return _merge_authority({
        "success": True,
        "status": "deleted",
        "asset_id": asset_id,
        "credential_values_exposed": False,
        "customer_safe": True,
    }, deleted)


def build_creative_execution_asset_context(
    *,
    tenant_id: str = "owner_admin",
    campaign_id: Optional[str] = None,
    limit: int = 25,
) -> Dict[str, Any]:
    listed = list_creative_product_assets(tenant_id=tenant_id, campaign_id=campaign_id, limit=limit)
    assets = listed.get("assets", [])

    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for asset in assets:
        asset_type = str(asset.get("asset_type") or "reference_asset")
        grouped.setdefault(asset_type, []).append({
            "asset_id": asset.get("asset_id"),
            "filename": asset.get("filename"),
            "mime_type": asset.get("mime_type"),
            "stored_path": asset.get("stored_path"),
            "storage_provider": asset.get("storage_provider"),
            "storage_bucket": asset.get("storage_bucket"),
            "storage_object_key": asset.get("storage_object_key"),
            "public_url": asset.get("public_url"),
            "preview_url": asset.get("preview_url"),
            "download_url": asset.get("download_url"),
            "size_bytes": asset.get("size_bytes"),
        })

    return {
        "success": True,
        "layer": "creative_execution_asset_context",
        "authority": "backend_canonical",
        "fallback_used": bool(listed.get("dev_only")),
        "dev_only": bool(listed.get("dev_only")),
        "production_fail_closed": False,
        "tenant_id": tenant_id,
        "campaign_id": campaign_id,
        "asset_count": len(assets),
        "assets_by_type": grouped,
        "product_images": grouped.get("product_image", []),
        "product_videos": grouped.get("product_video", []),
        "logos": grouped.get("logo", []),
        "brand_assets": grouped.get("brand_asset", []) + grouped.get("brand_guideline", []),
        "reference_assets": grouped.get("reference_asset", []) + grouped.get("reference_video", []),
        "storage_provider": listed.get("storage_provider"),
        "durable_storage_ready": listed.get("durable_storage_ready"),
        "credential_values_exposed": False,
        "customer_safe": True,
        "created_at": _now(),
    }


def creative_product_asset_library_status() -> Dict[str, Any]:
    summary = get_product_asset_metadata_summary()
    if not summary.get("success"):
        return _canonical_unavailable_response(summary)
    listed = list_creative_product_assets(limit=1)
    storage = supabase_storage_status()
    return _merge_authority({
        "success": True,
        "layer": "creative_product_asset_library",
        "status": "ready",
        "product_asset_metadata_ready": bool(summary.get("product_asset_metadata_ready", True)),
        "upload_ready": True,
        "list_ready": True,
        "delete_ready": True,
        "execution_context_ready": True,
        "total_asset_count": summary.get("total_asset_count", listed.get("total_asset_count", 0)),
        "event_count": summary.get("event_count", 0),
        "allowed_extensions": sorted(ALLOWED_EXTENSIONS),
        "storage_provider": storage.get("storage_provider"),
        "durable_storage_ready": storage.get("durable_storage_ready"),
        "storage_bucket": product_asset_bucket(),
        "canonical_storage_mode": summary.get("storage_mode"),
        "credential_values_exposed": False,
        "customer_safe": True,
        "verified_at": _now(),
    }, summary)
