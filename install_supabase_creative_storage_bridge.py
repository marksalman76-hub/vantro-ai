from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")

SUPABASE_FILE = ROOT / "backend" / "app" / "runtime" / "supabase_creative_storage.py"
PRODUCT_LIBRARY = ROOT / "backend" / "app" / "runtime" / "creative_product_asset_library.py"
MEDIA_BRIDGE = ROOT / "backend" / "app" / "runtime" / "creative_asset_persistence_bridge.py"

backup_dir = ROOT / "backups" / f"supabase_creative_storage_bridge_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)

for path in [SUPABASE_FILE, PRODUCT_LIBRARY, MEDIA_BRIDGE]:
    if path.exists():
        (backup_dir / path.name).write_text(path.read_text(encoding="utf-8"), encoding="utf-8")

SUPABASE_FILE.write_text(r'''from __future__ import annotations

import json
import mimetypes
import os
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, Optional


def _env(name: str, fallback: str = "") -> str:
    return str(os.getenv(name, fallback) or "").strip()


def supabase_enabled() -> bool:
    return bool(_env("SUPABASE_URL") and _env("SUPABASE_SERVICE_ROLE_KEY"))


def _project_url() -> str:
    return _env("SUPABASE_URL").rstrip("/")


def _service_key() -> str:
    return _env("SUPABASE_SERVICE_ROLE_KEY")


def product_asset_bucket() -> str:
    return _env("CREATIVE_PRODUCT_ASSET_BUCKET", _env("MEDIA_STORAGE_BUCKET", "creative-product-assets"))


def media_output_bucket() -> str:
    return _env("CREATIVE_MEDIA_OUTPUT_BUCKET", _env("MEDIA_STORAGE_BUCKET", "creative-media-outputs"))


def storage_status() -> Dict[str, Any]:
    return {
        "success": True,
        "layer": "supabase_creative_storage",
        "storage_provider": "supabase" if supabase_enabled() else "local_runtime_fallback",
        "durable_storage_ready": supabase_enabled(),
        "supabase_url_configured": bool(_env("SUPABASE_URL")),
        "service_role_key_configured": bool(_env("SUPABASE_SERVICE_ROLE_KEY")),
        "product_asset_bucket": product_asset_bucket(),
        "media_output_bucket": media_output_bucket(),
        "credential_values_exposed": False,
    }


def _headers(content_type: Optional[str] = None, upsert: bool = True) -> Dict[str, str]:
    headers = {
        "Authorization": f"Bearer {_service_key()}",
        "apikey": _service_key(),
    }
    if content_type:
        headers["Content-Type"] = content_type
    if upsert:
        headers["x-upsert"] = "true"
    return headers


def _object_url(bucket: str, object_key: str) -> str:
    return f"{_project_url()}/storage/v1/object/{bucket}/{urllib.parse.quote(object_key, safe='/')}"


def _public_url(bucket: str, object_key: str) -> str:
    return f"{_project_url()}/storage/v1/object/public/{bucket}/{urllib.parse.quote(object_key, safe='/')}"


def upload_bytes_to_supabase(
    *,
    bucket: str,
    object_key: str,
    content: bytes,
    content_type: Optional[str] = None,
) -> Dict[str, Any]:
    if not supabase_enabled():
        return {
            "success": False,
            "status": "supabase_not_configured",
            "credential_values_exposed": False,
        }

    content_type = content_type or mimetypes.guess_type(object_key)[0] or "application/octet-stream"
    request = urllib.request.Request(
        _object_url(bucket, object_key),
        data=content,
        method="POST",
        headers=_headers(content_type=content_type, upsert=True),
    )

    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            response_body = response.read().decode("utf-8", errors="ignore")

        return {
            "success": True,
            "status": "uploaded",
            "bucket": bucket,
            "object_key": object_key,
            "public_url": _public_url(bucket, object_key),
            "content_type": content_type,
            "response": response_body,
            "credential_values_exposed": False,
        }
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="ignore")
        return {
            "success": False,
            "status": "upload_failed",
            "bucket": bucket,
            "object_key": object_key,
            "http_status": exc.code,
            "error": error_body[-1000:],
            "credential_values_exposed": False,
        }
    except Exception as exc:
        return {
            "success": False,
            "status": "upload_exception",
            "bucket": bucket,
            "object_key": object_key,
            "error": str(exc),
            "credential_values_exposed": False,
        }


def upload_file_to_supabase(
    *,
    bucket: str,
    object_key: str,
    file_path: str,
    content_type: Optional[str] = None,
) -> Dict[str, Any]:
    path = Path(str(file_path or ""))
    if not path.exists() or not path.is_file():
        return {
            "success": False,
            "status": "local_file_not_found",
            "file_path": str(file_path),
            "credential_values_exposed": False,
        }

    return upload_bytes_to_supabase(
        bucket=bucket,
        object_key=object_key,
        content=path.read_bytes(),
        content_type=content_type or mimetypes.guess_type(str(path))[0],
    )


def download_text_from_supabase(
    *,
    bucket: str,
    object_key: str,
    fallback: str = "",
) -> Dict[str, Any]:
    if not supabase_enabled():
        return {
            "success": False,
            "status": "supabase_not_configured",
            "text": fallback,
            "credential_values_exposed": False,
        }

    request = urllib.request.Request(
        _object_url(bucket, object_key),
        method="GET",
        headers=_headers(upsert=False),
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            text = response.read().decode("utf-8", errors="ignore")
        return {
            "success": True,
            "status": "downloaded",
            "bucket": bucket,
            "object_key": object_key,
            "text": text,
            "credential_values_exposed": False,
        }
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return {
                "success": False,
                "status": "not_found",
                "bucket": bucket,
                "object_key": object_key,
                "text": fallback,
                "credential_values_exposed": False,
            }
        error_body = exc.read().decode("utf-8", errors="ignore")
        return {
            "success": False,
            "status": "download_failed",
            "bucket": bucket,
            "object_key": object_key,
            "http_status": exc.code,
            "error": error_body[-1000:],
            "text": fallback,
            "credential_values_exposed": False,
        }
    except Exception as exc:
        return {
            "success": False,
            "status": "download_exception",
            "bucket": bucket,
            "object_key": object_key,
            "error": str(exc),
            "text": fallback,
            "credential_values_exposed": False,
        }


def upload_json_to_supabase(
    *,
    bucket: str,
    object_key: str,
    payload: Any,
) -> Dict[str, Any]:
    content = json.dumps(payload, indent=2, ensure_ascii=False).encode("utf-8")
    return upload_bytes_to_supabase(
        bucket=bucket,
        object_key=object_key,
        content=content,
        content_type="application/json",
    )


def download_json_from_supabase(
    *,
    bucket: str,
    object_key: str,
    fallback: Any,
) -> Dict[str, Any]:
    result = download_text_from_supabase(bucket=bucket, object_key=object_key, fallback="")
    if not result.get("success"):
        return {
            **result,
            "json": fallback,
        }

    try:
        return {
            **result,
            "json": json.loads(result.get("text") or ""),
        }
    except Exception as exc:
        return {
            **result,
            "success": False,
            "status": "invalid_json",
            "error": str(exc),
            "json": fallback,
        }
''', encoding="utf-8")

PRODUCT_LIBRARY.write_text(r'''from __future__ import annotations

import base64
import hashlib
import json
import mimetypes
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

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

    asset_id = f"product_asset_{uuid.uuid4().hex[:18]}"
    mime_type = mimetypes.guess_type(safe_filename)[0] or "application/octet-stream"

    asset_dir = _tenant_dir(tenant_id, asset_type)
    stored_filename = f"{asset_id}_{safe_filename}"
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

    record = {
        "asset_id": asset_id,
        "tenant_id": tenant_id,
        "asset_type": asset_type,
        "filename": original_filename,
        "stored_filename": stored_filename,
        "stored_path": str(stored_path),
        "storage_provider": "supabase" if storage_url else "local_runtime_fallback",
        "storage_bucket": product_asset_bucket() if storage_url else None,
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
        "preview_ready": bool(storage_url) or mime_type.startswith(("image/", "video/")) or mime_type == "application/pdf",
        "download_ready": bool(storage_url) or True,
        "customer_safe": True,
        "credential_values_exposed": False,
        "created_at": _now(),
        "updated_at": _now(),
    }

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
        "storage_provider": record["storage_provider"],
        "durable_storage_ready": record["storage_provider"] == "supabase",
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
    registry = _load_registry()
    records = [r for r in registry.get("assets", []) if isinstance(r, dict)]

    if tenant_id:
        records = [r for r in records if r.get("tenant_id") == tenant_id]

    if asset_type:
        normalised = _normalise_asset_type(asset_type)
        records = [r for r in records if r.get("asset_type") == normalised]

    if campaign_id:
        records = [r for r in records if r.get("campaign_id") == campaign_id]

    records = records[: max(int(limit or 100), 1)]
    storage = supabase_storage_status()

    return {
        "success": True,
        "layer": "creative_product_asset_library",
        "status": "ready",
        "asset_count": len(records),
        "total_asset_count": len(registry.get("assets", [])),
        "assets": records,
        "supported_asset_types": sorted(set(ASSET_TYPE_ALIASES.values())),
        "allowed_extensions": sorted(ALLOWED_EXTENSIONS),
        "storage_provider": storage.get("storage_provider"),
        "durable_storage_ready": storage.get("durable_storage_ready"),
        "storage_bucket": product_asset_bucket(),
        "credential_values_exposed": False,
        "customer_safe": True,
        "verified_at": _now(),
    }


def get_creative_product_asset(asset_id: str) -> Dict[str, Any]:
    registry = _load_registry()
    for record in registry.get("assets", []):
        if isinstance(record, dict) and record.get("asset_id") == asset_id:
            return {
                "success": True,
                "status": "found",
                "asset": record,
                "credential_values_exposed": False,
                "customer_safe": True,
            }

    return {
        "success": False,
        "status": "not_found",
        "asset_id": asset_id,
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def delete_creative_product_asset(
    *,
    asset_id: str,
    tenant_id: Optional[str] = None,
) -> Dict[str, Any]:
    registry = _load_registry()
    kept: List[Dict[str, Any]] = []
    deleted: Optional[Dict[str, Any]] = None

    for record in registry.get("assets", []):
        if not isinstance(record, dict):
            continue
        if record.get("asset_id") != asset_id:
            kept.append(record)
            continue
        if tenant_id and record.get("tenant_id") != tenant_id:
            kept.append(record)
            continue
        deleted = record

    if not deleted:
        return {
            "success": False,
            "status": "not_found",
            "asset_id": asset_id,
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    stored_path = Path(str(deleted.get("stored_path") or ""))
    if stored_path.exists() and stored_path.is_file():
        try:
            stored_path.unlink()
        except Exception:
            pass

    registry["assets"] = kept
    _save_registry(registry)

    return {
        "success": True,
        "status": "deleted",
        "asset_id": asset_id,
        "credential_values_exposed": False,
        "customer_safe": True,
    }


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
    listed = list_creative_product_assets(limit=1)
    storage = supabase_storage_status()
    return {
        "success": True,
        "layer": "creative_product_asset_library",
        "status": "ready",
        "upload_ready": True,
        "list_ready": True,
        "delete_ready": True,
        "execution_context_ready": True,
        "total_asset_count": listed.get("total_asset_count", 0),
        "allowed_extensions": sorted(ALLOWED_EXTENSIONS),
        "storage_provider": storage.get("storage_provider"),
        "durable_storage_ready": storage.get("durable_storage_ready"),
        "storage_bucket": product_asset_bucket(),
        "credential_values_exposed": False,
        "customer_safe": True,
        "verified_at": _now(),
    }
''', encoding="utf-8")

MEDIA_BRIDGE.write_text(r'''from pathlib import Path
from datetime import datetime, timezone
import json
import os
import hashlib
import mimetypes

try:
    from backend.app.runtime.supabase_creative_storage import (
        supabase_enabled,
        storage_status as supabase_storage_status,
        media_output_bucket,
        upload_file_to_supabase,
        upload_json_to_supabase,
        download_json_from_supabase,
    )
except Exception:
    supabase_enabled = lambda: False
    supabase_storage_status = lambda: {"durable_storage_ready": False}
    media_output_bucket = lambda: "creative-media-outputs"
    upload_file_to_supabase = None
    upload_json_to_supabase = None
    download_json_from_supabase = None

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_REGISTRY_DIR = ROOT / "runtime_outputs" / "creative_asset_registry"
REGISTRY_DIR = Path(os.getenv("CREATIVE_MEDIA_PERSISTENCE_DIR", str(DEFAULT_REGISTRY_DIR)))
REGISTRY_DIR.mkdir(parents=True, exist_ok=True)
REGISTRY_FILE = REGISTRY_DIR / "creative_assets.json"
SUPABASE_REGISTRY_OBJECT_KEY = "registries/creative_media_asset_registry.json"

CREATIVE_AGENT_IDS = {
    "ugc_creative_agent",
    "social_media_manager_content_creator_agent",
    "paid_ads_agent",
    "creative_rotation_agent",
    "product_image_agent",
    "marketing_specialist_agent",
    "influencer_collaboration_agent",
    "influencer_outreach_agent",
}

CREATIVE_TEXT_ASSET_TYPES = {
    "ugc_script",
    "creator_brief",
    "campaign_brief",
    "ad_brief",
    "social_content_plan",
    "influencer_outreach_packet",
    "usage_rights_record",
    "affiliate_discount_plan",
    "performance_tracking_plan",
    "creative_strategy",
}

MEDIA_ASSET_TYPES = {
    "video",
    "audio",
    "image",
    "voiceover",
    "lipsync_video",
    "dubbing_audio",
    "ugc_video",
    "ad_video",
    "product_image",
    "combined_video",
}

def _now():
    return datetime.now(timezone.utc).isoformat()

def _blank_registry():
    return []

def _load_registry():
    if supabase_enabled() and download_json_from_supabase is not None:
        result = download_json_from_supabase(
            bucket=media_output_bucket(),
            object_key=SUPABASE_REGISTRY_OBJECT_KEY,
            fallback=[],
        )
        data = result.get("json")
        if isinstance(data, list):
            return data

    if not REGISTRY_FILE.exists():
        return []
    try:
        data = json.loads(REGISTRY_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        return []

def _save_registry(data):
    if supabase_enabled() and upload_json_to_supabase is not None:
        upload_json_to_supabase(
            bucket=media_output_bucket(),
            object_key=SUPABASE_REGISTRY_OBJECT_KEY,
            payload=data,
        )

    REGISTRY_DIR.mkdir(parents=True, exist_ok=True)
    REGISTRY_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")

def _safe_string(value, fallback=""):
    if value is None:
        return fallback
    return str(value)

def _safe_slug(value, fallback="asset"):
    raw = _safe_string(value, fallback).strip() or fallback
    return "".join(ch if ch.isalnum() or ch in ("-", "_", ".") else "_" for ch in raw)[:160] or fallback

def _asset_id(packet):
    raw = "|".join([
        _safe_string(packet.get("agent_id")),
        _safe_string(packet.get("provider")),
        _safe_string(packet.get("asset_type")),
        _safe_string(packet.get("test_label")),
        _safe_string(packet.get("provider_asset_id")),
        _safe_string(packet.get("provider_asset_url") or packet.get("preview_url") or packet.get("download_url")),
        _safe_string(packet.get("title")),
    ])
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]

def is_creative_agent(agent_id):
    return str(agent_id or "").strip() in CREATIVE_AGENT_IDS

def classify_creative_asset(packet):
    explicit = str(packet.get("asset_type") or "").strip().lower()
    if explicit:
        return explicit

    provider = str(packet.get("provider") or "").lower()
    title = str(packet.get("title") or packet.get("test_label") or "").lower()
    content = str(packet.get("content") or packet.get("summary") or "").lower()

    if "elevenlabs" in provider or "voice" in title:
        return "voiceover"
    if "runway" in provider or "kling" in provider or "video" in title:
        return "video"
    if "image" in title or "product image" in content:
        return "image"
    if "influencer" in title or "creator shortlist" in content or "usage rights" in content:
        return "influencer_outreach_packet"
    if "ugc" in title or "script" in content:
        return "ugc_script"
    if "ad" in title or "campaign" in content:
        return "campaign_brief"

    return "creative_strategy"

def _maybe_upload_media_file(packet, asset_id, asset_type):
    if not supabase_enabled() or upload_file_to_supabase is None:
        return None

    candidate = (
        packet.get("download_url")
        or packet.get("preview_url")
        or packet.get("provider_asset_url")
    )

    if not candidate:
        return None

    candidate_text = str(candidate)
    if candidate_text.startswith("http://") or candidate_text.startswith("https://"):
        return None

    path = Path(candidate_text)
    if not path.exists() or not path.is_file():
        return None

    filename = path.name
    test_label = _safe_slug(packet.get("test_label") or packet.get("title") or asset_id)
    object_key = f"tenants/{_safe_slug(packet.get('tenant_id') or 'owner_admin')}/{asset_type}/{asset_id}_{test_label}_{filename}"
    content_type = mimetypes.guess_type(str(path))[0] or "application/octet-stream"

    upload = upload_file_to_supabase(
        bucket=media_output_bucket(),
        object_key=object_key,
        file_path=str(path),
        content_type=content_type,
    )

    if upload.get("success"):
        return upload

    return upload

def persist_creative_asset(asset_packet: dict):
    registry = _load_registry()
    packet = dict(asset_packet or {})

    agent_id = packet.get("agent_id") or packet.get("agent_key") or packet.get("requested_agent")
    asset_type = classify_creative_asset(packet)
    created_at = _now()
    asset_id = packet.get("asset_id") or _asset_id(packet)

    storage_upload = _maybe_upload_media_file(packet, asset_id, asset_type)
    storage_url = storage_upload.get("public_url") if isinstance(storage_upload, dict) and storage_upload.get("success") else None

    stored = {
        "asset_id": asset_id,
        "agent_id": agent_id,
        "agent_label": packet.get("agent_label"),
        "provider": packet.get("provider") or "internal",
        "asset_type": asset_type,
        "title": packet.get("title") or packet.get("test_label") or asset_type.replace("_", " ").title(),
        "test_label": packet.get("test_label"),
        "provider_asset_url": storage_url or packet.get("provider_asset_url"),
        "provider_asset_id": packet.get("provider_asset_id"),
        "preview_url": storage_url or packet.get("preview_url") or packet.get("provider_asset_url"),
        "download_url": storage_url or packet.get("download_url") or packet.get("provider_asset_url"),
        "original_preview_url": packet.get("preview_url") or packet.get("provider_asset_url"),
        "original_download_url": packet.get("download_url") or packet.get("provider_asset_url"),
        "storage_provider": "supabase" if storage_url else "external_or_local_runtime_fallback",
        "storage_bucket": media_output_bucket() if storage_url else None,
        "storage_object_key": storage_upload.get("object_key") if isinstance(storage_upload, dict) else None,
        "storage_upload": storage_upload,
        "content": packet.get("content"),
        "summary": packet.get("summary"),
        "status": packet.get("status") or "persisted",
        "quality_score": packet.get("quality_score"),
        "campaign_context": packet.get("campaign_context"),
        "target_audience": packet.get("target_audience"),
        "usage_rights": packet.get("usage_rights"),
        "owner_approval_required": bool(packet.get("owner_approval_required", False)),
        "governed": True,
        "customer_safe": True,
        "credential_values_exposed": False,
        "created_at": created_at,
    }

    existing_ids = {item.get("asset_id") for item in registry if isinstance(item, dict)}
    if stored["asset_id"] not in existing_ids:
        registry.insert(0, stored)

    registry = registry[:500]
    _save_registry(registry)

    return {
        "success": True,
        "asset_id": stored["asset_id"],
        "asset_type": stored["asset_type"],
        "registry_count": len(registry),
        "storage_provider": stored["storage_provider"],
        "durable_storage_ready": stored["storage_provider"] == "supabase",
        "credential_values_exposed": False,
    }

def persist_creative_agent_output(agent_id: str, output_packet: dict):
    if not is_creative_agent(agent_id):
        return {
            "success": True,
            "persisted": False,
            "reason": "not_creative_agent",
            "credential_values_exposed": False,
        }

    packet = output_packet or {}
    records = []

    media_assets = packet.get("media_assets")
    if isinstance(media_assets, list):
        for asset in media_assets:
            if isinstance(asset, dict):
                asset["agent_id"] = agent_id
                records.append(persist_creative_asset(asset))

    persisted_asset_records = packet.get("persisted_asset_records")
    if isinstance(persisted_asset_records, list):
        for asset in persisted_asset_records:
            if isinstance(asset, dict):
                asset["agent_id"] = agent_id
                records.append(persist_creative_asset(asset))

    if not records:
        text_content = (
            packet.get("live_output")
            or packet.get("output")
            or packet.get("result")
            or packet.get("summary")
            or packet.get("message")
        )

        title = packet.get("title") or packet.get("test_label") or f"{agent_id} creative output"

        records.append(
            persist_creative_asset(
                {
                    "agent_id": agent_id,
                    "provider": packet.get("provider") or packet.get("selected_provider") or "internal",
                    "asset_type": classify_creative_asset(
                        {
                            "asset_type": packet.get("asset_type"),
                            "provider": packet.get("provider"),
                            "title": title,
                            "content": text_content,
                        }
                    ),
                    "title": title,
                    "test_label": packet.get("test_label"),
                    "content": text_content,
                    "summary": packet.get("summary"),
                    "status": packet.get("status") or "creative_output_persisted",
                    "quality_score": packet.get("quality_score"),
                    "campaign_context": packet.get("campaign_context"),
                    "target_audience": packet.get("target_audience"),
                    "owner_approval_required": packet.get("owner_approval_required", False),
                }
            )
        )

    return {
        "success": True,
        "persisted": True,
        "agent_id": agent_id,
        "persisted_asset_count": len(records),
        "persisted_asset_records": records,
        "credential_values_exposed": False,
    }

def get_persisted_creative_assets(limit=100):
    registry = _load_registry()
    safe_assets = []

    for item in registry[: int(limit or 100)]:
        if not isinstance(item, dict):
            continue
        clean = dict(item)
        clean["credential_values_exposed"] = False
        safe_assets.append(clean)

    storage = supabase_storage_status()

    return {
        "success": True,
        "asset_count": len(safe_assets),
        "total_asset_count": len(registry),
        "assets": safe_assets,
        "providers_checked": ["elevenlabs", "runway", "heygen", "kling", "sync", "internal"],
        "storage_provider": storage.get("storage_provider"),
        "durable_storage_ready": storage.get("durable_storage_ready"),
        "storage_bucket": media_output_bucket(),
        "credential_values_exposed": False,
    }
''', encoding="utf-8")

print("SUPABASE_CREATIVE_STORAGE_BRIDGE_INSTALLED")
print("Created:", SUPABASE_FILE)
print("Updated:", PRODUCT_LIBRARY)
print("Updated:", MEDIA_BRIDGE)
print("Backup:", backup_dir)