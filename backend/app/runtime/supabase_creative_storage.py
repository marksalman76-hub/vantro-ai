from __future__ import annotations

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
