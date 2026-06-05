from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
FILE = ROOT / "backend" / "app" / "runtime" / "supabase_creative_storage.py"

backup = ROOT / "backups" / f"supabase_storage_upload_endpoint_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup.mkdir(parents=True, exist_ok=True)
(backup / FILE.name).write_text(FILE.read_text(encoding="utf-8"), encoding="utf-8")

FILE.write_text(r'''from __future__ import annotations

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
    url = _env("SUPABASE_URL").rstrip("/")
    for suffix in ["/rest/v1", "/storage/v1", "/auth/v1"]:
        if url.endswith(suffix):
            url = url[: -len(suffix)]
    return url.rstrip("/")


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


def _clean_object_key(object_key: str) -> str:
    parts = [p for p in str(object_key or "").replace("\\", "/").split("/") if p and p not in [".", ".."]]
    return "/".join(parts)


def _object_url(bucket: str, object_key: str) -> str:
    clean_key = _clean_object_key(object_key)
    encoded_bucket = urllib.parse.quote(str(bucket).strip(), safe="")
    encoded_key = "/".join(urllib.parse.quote(part, safe="") for part in clean_key.split("/"))
    return f"{_project_url()}/storage/v1/object/{encoded_bucket}/{encoded_key}"


def _public_url(bucket: str, object_key: str) -> str:
    clean_key = _clean_object_key(object_key)
    encoded_bucket = urllib.parse.quote(str(bucket).strip(), safe="")
    encoded_key = "/".join(urllib.parse.quote(part, safe="") for part in clean_key.split("/"))
    return f"{_project_url()}/storage/v1/object/public/{encoded_bucket}/{encoded_key}"


def _request_upload(method: str, bucket: str, object_key: str, content: bytes, content_type: str) -> Dict[str, Any]:
    url = _object_url(bucket, object_key)
    request = urllib.request.Request(
        url,
        data=content,
        method=method,
        headers=_headers(content_type=content_type, upsert=True),
    )

    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            response_body = response.read().decode("utf-8", errors="ignore")

        return {
            "success": True,
            "status": "uploaded",
            "method": method,
            "bucket": bucket,
            "object_key": _clean_object_key(object_key),
            "upload_url_checked": url,
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
            "method": method,
            "bucket": bucket,
            "object_key": _clean_object_key(object_key),
            "upload_url_checked": url,
            "http_status": exc.code,
            "error": error_body[-1500:],
            "credential_values_exposed": False,
        }
    except Exception as exc:
        return {
            "success": False,
            "status": "upload_exception",
            "method": method,
            "bucket": bucket,
            "object_key": _clean_object_key(object_key),
            "upload_url_checked": url,
            "error": str(exc),
            "credential_values_exposed": False,
        }


def upload_bytes_to_supabase(
    *,
    bucket: str,
    object_key: str,
    content: bytes,
    content_type: Optional[str] = None,
) -> Dict[str, Any]:
    if not supabase_enabled():
        return {"success": False, "status": "supabase_not_configured", "credential_values_exposed": False}

    content_type = content_type or mimetypes.guess_type(object_key)[0] or "application/octet-stream"

    first = _request_upload("POST", bucket, object_key, content, content_type)
    if first.get("success"):
        return first

    second = _request_upload("PUT", bucket, object_key, content, content_type)
    if second.get("success"):
        return second

    return {
        **second,
        "first_attempt": first,
        "second_attempt": second,
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
        return {"success": False, "status": "local_file_not_found", "file_path": str(file_path), "credential_values_exposed": False}

    return upload_bytes_to_supabase(
        bucket=bucket,
        object_key=object_key,
        content=path.read_bytes(),
        content_type=content_type or mimetypes.guess_type(str(path))[0],
    )


def download_text_from_supabase(*, bucket: str, object_key: str, fallback: str = "") -> Dict[str, Any]:
    if not supabase_enabled():
        return {"success": False, "status": "supabase_not_configured", "text": fallback, "credential_values_exposed": False}

    request = urllib.request.Request(
        _object_url(bucket, object_key),
        method="GET",
        headers=_headers(upsert=False),
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            text = response.read().decode("utf-8", errors="ignore")
        return {"success": True, "status": "downloaded", "bucket": bucket, "object_key": _clean_object_key(object_key), "text": text, "credential_values_exposed": False}
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return {"success": False, "status": "not_found", "bucket": bucket, "object_key": _clean_object_key(object_key), "text": fallback, "credential_values_exposed": False}
        error_body = exc.read().decode("utf-8", errors="ignore")
        return {"success": False, "status": "download_failed", "bucket": bucket, "object_key": _clean_object_key(object_key), "http_status": exc.code, "error": error_body[-1500:], "text": fallback, "credential_values_exposed": False}
    except Exception as exc:
        return {"success": False, "status": "download_exception", "bucket": bucket, "object_key": _clean_object_key(object_key), "error": str(exc), "text": fallback, "credential_values_exposed": False}


def upload_json_to_supabase(*, bucket: str, object_key: str, payload: Any) -> Dict[str, Any]:
    return upload_bytes_to_supabase(
        bucket=bucket,
        object_key=object_key,
        content=json.dumps(payload, indent=2, ensure_ascii=False).encode("utf-8"),
        content_type="application/json",
    )


def download_json_from_supabase(*, bucket: str, object_key: str, fallback: Any) -> Dict[str, Any]:
    result = download_text_from_supabase(bucket=bucket, object_key=object_key, fallback="")
    if not result.get("success"):
        return {**result, "json": fallback}

    try:
        return {**result, "json": json.loads(result.get("text") or "")}
    except Exception as exc:
        return {**result, "success": False, "status": "invalid_json", "error": str(exc), "json": fallback}
''', encoding="utf-8")

print("SUPABASE_STORAGE_UPLOAD_ENDPOINT_FIXED")
print("Updated:", FILE)
print("Backup:", backup)