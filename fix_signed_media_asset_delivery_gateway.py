from pathlib import Path
from datetime import datetime
import re

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")

DELIVERY_RUNTIME = ROOT / "backend" / "app" / "runtime" / "asset_storage_signed_delivery_runtime.py"
VIEWER_RUNTIME = ROOT / "backend" / "app" / "runtime" / "admin_creative_media_asset_viewer.py"
MAIN_FILE = ROOT / "backend" / "app" / "main.py"

backup_dir = ROOT / "backups" / f"signed_media_asset_delivery_gateway_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)

for file_path in [DELIVERY_RUNTIME, VIEWER_RUNTIME, MAIN_FILE]:
    if file_path.exists():
        (backup_dir / file_path.name).write_text(file_path.read_text(encoding="utf-8"), encoding="utf-8")


DELIVERY_RUNTIME.write_text(
r'''from __future__ import annotations

import hashlib
import hmac
import mimetypes
import os
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional


_ASSET_RECORDS: Dict[str, Dict[str, Any]] = {}
_ASSET_DELIVERY_EVENTS: List[Dict[str, Any]] = []


def _now_ms() -> int:
    return int(time.time() * 1000)


def _sign_payload(payload: str) -> str:
    secret = os.getenv("ASSET_PACKET_SIGNING_SECRET") or os.getenv("ADMIN_AUTH_SECRET") or "dev-asset-signing-secret"
    return hmac.new(secret.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()


def _safe_metadata(metadata: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    safe = {}
    for key, value in (metadata or {}).items():
        lowered = str(key).lower()
        if "secret" in lowered or "token" in lowered or "key" in lowered:
            continue
        safe[key] = value
    return safe


def _is_browser_url(value: Any) -> bool:
    text = str(value or "").strip()
    return text.startswith(("http://", "https://", "data:"))


def _is_local_runtime_path(value: Any) -> bool:
    text = str(value or "").strip()
    return bool(text) and (
        text.startswith("/opt/render/project/src/runtime_outputs/")
        or text.startswith(str(Path.cwd() / "runtime_outputs"))
        or "\\runtime_outputs\\" in text
        or "/runtime_outputs/" in text
    )


def _content_type_for_path(path: str, asset_type: str = "") -> str:
    guessed, _ = mimetypes.guess_type(path)
    if guessed:
        return guessed

    lowered = f"{path} {asset_type}".lower()
    if ".mp4" in lowered or "video" in lowered:
        return "video/mp4"
    if ".mp3" in lowered or "audio" in lowered or "voice" in lowered:
        return "audio/mpeg"
    if ".png" in lowered:
        return "image/png"
    if ".jpg" in lowered or ".jpeg" in lowered:
        return "image/jpeg"
    return "application/octet-stream"


def _filename_for_path(path: str, asset_id: str, asset_type: str) -> str:
    name = Path(path).name if path else ""
    if name:
        return name
    extension = ".mp4" if "video" in str(asset_type).lower() else ".mp3" if "audio" in str(asset_type).lower() else ".bin"
    return f"{asset_id}{extension}"


def reset_asset_storage_for_tests() -> Dict[str, Any]:
    _ASSET_RECORDS.clear()
    _ASSET_DELIVERY_EVENTS.clear()
    return {
        "reset": True,
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def create_asset_record(
    *,
    tenant_id: str,
    request_id: str,
    provider_key: str,
    asset_type: str,
    asset_status: str = "prepared",
    source_url: Optional[str] = None,
    storage_key: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    asset_id = f"asset_{uuid.uuid4().hex[:16]}"
    now = _now_ms()

    record = {
        "asset_id": asset_id,
        "tenant_id": tenant_id,
        "request_id": request_id,
        "provider_key": provider_key,
        "asset_type": asset_type,
        "asset_status": asset_status,
        "source_url_present": bool(source_url),
        "source_url": source_url if _is_browser_url(source_url) else "",
        "local_file_path": source_url if _is_local_runtime_path(source_url) else "",
        "storage_key": storage_key or f"{tenant_id}/{request_id}/{asset_id}",
        "metadata": _safe_metadata(metadata),
        "created_at_ms": now,
        "updated_at_ms": now,
        "credential_values_exposed": False,
        "customer_safe": True,
    }

    _ASSET_RECORDS[asset_id] = record
    return record


def _registry_asset_to_record(asset_id: str) -> Dict[str, Any]:
    try:
        from backend.app.runtime.creative_asset_persistence_bridge import get_persisted_creative_assets

        registry = get_persisted_creative_assets(limit=500)
        assets = registry.get("assets", []) if isinstance(registry, dict) else []

        for asset in assets:
            if not isinstance(asset, dict):
                continue
            if asset.get("asset_id") != asset_id:
                continue

            preview_url = asset.get("preview_url") or ""
            download_url = asset.get("download_url") or ""
            provider_asset_url = asset.get("provider_asset_url") or ""

            local_file_path = ""
            source_url = ""

            for candidate in [download_url, preview_url, provider_asset_url]:
                if _is_local_runtime_path(candidate):
                    local_file_path = str(candidate)
                    break

            for candidate in [preview_url, provider_asset_url, download_url]:
                if _is_browser_url(candidate):
                    source_url = str(candidate)
                    break

            record = {
                "asset_id": asset_id,
                "tenant_id": asset.get("tenant_id") or "owner_admin",
                "request_id": asset.get("test_label") or asset.get("pack_id") or "creative_asset_registry",
                "provider_key": asset.get("provider") or "internal",
                "asset_type": asset.get("asset_type") or "creative_asset",
                "asset_status": asset.get("status") or "persisted",
                "source_url_present": bool(source_url),
                "source_url": source_url,
                "local_file_path": local_file_path,
                "storage_key": f"creative_registry/{asset_id}",
                "metadata": {
                    "registry_fallback": True,
                    "title": asset.get("title"),
                    "provider_asset_id": asset.get("provider_asset_id"),
                    "content_present": bool(asset.get("content")),
                    "summary_present": bool(asset.get("summary")),
                    "content": asset.get("content"),
                    "summary": asset.get("summary"),
                },
                "created_at_ms": _now_ms(),
                "updated_at_ms": _now_ms(),
                "credential_values_exposed": False,
                "customer_safe": True,
            }

            _ASSET_RECORDS[asset_id] = record
            return record

    except Exception as exc:
        return {
            "status": "not_found",
            "asset_id": asset_id,
            "reason": "registry_lookup_failed",
            "error": str(exc)[:500],
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    return {
        "status": "not_found",
        "asset_id": asset_id,
        "reason": "asset_not_found_in_registry",
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def get_asset_record(asset_id: str) -> Dict[str, Any]:
    record = _ASSET_RECORDS.get(asset_id)
    if record:
        return record
    return _registry_asset_to_record(asset_id)


def list_asset_records(
    *,
    tenant_id: Optional[str] = None,
    request_id: Optional[str] = None,
    provider_key: Optional[str] = None,
    limit: int = 100,
) -> Dict[str, Any]:
    records = list(_ASSET_RECORDS.values())

    if tenant_id:
        records = [r for r in records if r.get("tenant_id") == tenant_id]
    if request_id:
        records = [r for r in records if r.get("request_id") == request_id]
    if provider_key:
        records = [r for r in records if r.get("provider_key") == provider_key]

    records = sorted(records, key=lambda r: r.get("created_at_ms", 0), reverse=True)[:limit]

    return {
        "records": records,
        "count": len(records),
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def update_asset_status(
    *,
    asset_id: str,
    asset_status: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    record = get_asset_record(asset_id)
    if record.get("status") == "not_found":
        return record

    record["asset_status"] = asset_status
    record["updated_at_ms"] = _now_ms()

    if metadata:
        merged = dict(record.get("metadata") or {})
        merged.update(_safe_metadata(metadata))
        record["metadata"] = merged

    record["credential_values_exposed"] = False
    record["customer_safe"] = True
    _ASSET_RECORDS[asset_id] = record
    return record


def create_signed_asset_delivery_packet(
    *,
    tenant_id: str,
    asset_id: str,
    delivery_type: str = "preview",
    expires_in_seconds: int = 86400,
) -> Dict[str, Any]:
    record = get_asset_record(asset_id)
    if record.get("status") == "not_found":
        return {
            "status": "not_found",
            "asset_id": asset_id,
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    record_tenant = record.get("tenant_id") or tenant_id or "owner_admin"
    if record_tenant != tenant_id and tenant_id not in {"owner_admin", "owner", "admin"}:
        return {
            "status": "blocked",
            "reason": "tenant_asset_mismatch",
            "asset_id": asset_id,
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    expires_at_ms = _now_ms() + int(expires_in_seconds * 1000)
    nonce = uuid.uuid4().hex
    payload = f"{record_tenant}:{asset_id}:{delivery_type}:{expires_at_ms}:{nonce}"
    signature = _sign_payload(payload)

    packet = {
        "status": "ready",
        "asset_id": asset_id,
        "tenant_id": record_tenant,
        "delivery_type": delivery_type,
        "expires_at_ms": expires_at_ms,
        "nonce": nonce,
        "signature": signature,
        "signed_delivery_token_present": True,
        "delivery_url": f"/asset-delivery/{delivery_type}/{asset_id}?expires={expires_at_ms}&nonce={nonce}&sig={signature}",
        "credential_values_exposed": False,
        "customer_safe": True,
    }

    _ASSET_DELIVERY_EVENTS.append({
        "event_id": f"asset_delivery_{uuid.uuid4().hex[:16]}",
        "tenant_id": record_tenant,
        "asset_id": asset_id,
        "delivery_type": delivery_type,
        "event_type": "signed_delivery_packet_created",
        "created_at_ms": _now_ms(),
        "credential_values_exposed": False,
        "customer_safe": True,
    })

    return packet


def verify_signed_asset_delivery_packet(
    *,
    tenant_id: str,
    asset_id: str,
    delivery_type: str,
    expires_at_ms: int,
    nonce: str,
    signature: str,
) -> Dict[str, Any]:
    if _now_ms() > int(expires_at_ms):
        return {
            "valid": False,
            "reason": "expired",
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    valid = False
    for candidate_tenant in [tenant_id, "owner_admin", "owner", "admin"]:
        expected = _sign_payload(f"{candidate_tenant}:{asset_id}:{delivery_type}:{expires_at_ms}:{nonce}")
        if hmac.compare_digest(expected, signature):
            valid = True
            break

    return {
        "valid": valid,
        "reason": "valid" if valid else "invalid_signature",
        "asset_id": asset_id,
        "tenant_id": tenant_id,
        "delivery_type": delivery_type,
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def create_customer_safe_asset_preview(
    *,
    tenant_id: str,
    asset_id: str,
) -> Dict[str, Any]:
    record = get_asset_record(asset_id)
    if record.get("status") == "not_found":
        return record

    packet = create_signed_asset_delivery_packet(
        tenant_id=tenant_id or record.get("tenant_id") or "owner_admin",
        asset_id=asset_id,
        delivery_type="preview",
        expires_in_seconds=1800,
    )

    return {
        "status": "ready",
        "asset": {
            "asset_id": record["asset_id"],
            "asset_type": record["asset_type"],
            "asset_status": record["asset_status"],
            "provider_key": record["provider_key"],
            "created_at_ms": record["created_at_ms"],
        },
        "preview_packet": packet,
        "internal_storage_key_exposed": False,
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def build_customer_safe_delivery_response(
    *,
    asset_id: str,
    delivery_type: str,
    expires_at_ms: int,
    nonce: str,
    signature: str,
) -> Dict[str, Any]:
    record = get_asset_record(asset_id)

    if record.get("status") == "not_found":
        return {
            "success": False,
            "status": "not_found",
            "reason": "asset_not_found_or_runtime_record_expired",
            "asset_id": asset_id,
            "http_status": 404,
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    tenant_id = record.get("tenant_id") or "owner_admin"
    verification = verify_signed_asset_delivery_packet(
        tenant_id=tenant_id,
        asset_id=asset_id,
        delivery_type=delivery_type,
        expires_at_ms=expires_at_ms,
        nonce=nonce,
        signature=signature,
    )

    if not verification.get("valid"):
        return {
            "success": False,
            "status": "blocked",
            "reason": verification.get("reason"),
            "asset_id": asset_id,
            "http_status": 403,
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    asset_type = record.get("asset_type") or "asset"
    local_file_path = record.get("local_file_path") or ""
    source_url = record.get("source_url") or ""

    if local_file_path and Path(local_file_path).exists():
        return {
            "success": True,
            "status": "ready",
            "delivery_type": delivery_type,
            "asset_id": asset_id,
            "serve_file_path": local_file_path,
            "filename": _filename_for_path(local_file_path, asset_id, asset_type),
            "content_type": _content_type_for_path(local_file_path, asset_type),
            "http_status": 200,
            "delivery": {
                "mode": "local_runtime_file",
                "preview_ready": True,
                "download_ready": True,
                "internal_storage_key_exposed": False,
            },
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    if source_url:
        return {
            "success": True,
            "status": "ready",
            "delivery_type": delivery_type,
            "asset_id": asset_id,
            "redirect_url": source_url,
            "http_status": 302,
            "delivery": {
                "mode": "provider_url_redirect",
                "preview_ready": True,
                "download_ready": True,
                "internal_storage_key_exposed": False,
            },
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    metadata = record.get("metadata") if isinstance(record.get("metadata"), dict) else {}

    return {
        "success": True,
        "status": "ready",
        "delivery_type": delivery_type,
        "asset_id": asset_id,
        "content": metadata.get("content"),
        "summary": metadata.get("summary"),
        "http_status": 200,
        "delivery": {
            "mode": "metadata_fallback",
            "preview_ready": bool(metadata.get("content") or metadata.get("summary")),
            "download_ready": False,
            "internal_storage_key_exposed": False,
        },
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def list_asset_delivery_events(
    *,
    tenant_id: Optional[str] = None,
    asset_id: Optional[str] = None,
    limit: int = 100,
) -> Dict[str, Any]:
    events = list(_ASSET_DELIVERY_EVENTS)

    if tenant_id:
        events = [e for e in events if e.get("tenant_id") == tenant_id]
    if asset_id:
        events = [e for e in events if e.get("asset_id") == asset_id]

    events = sorted(events, key=lambda e: e.get("created_at_ms", 0), reverse=True)[:limit]

    return {
        "events": events,
        "count": len(events),
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def asset_storage_signed_delivery_status() -> Dict[str, Any]:
    return {
        "asset_storage_runtime_ready": True,
        "storage_mode": "signed_gateway_local_file_plus_provider_redirect",
        "signed_delivery_ready": True,
        "preview_delivery_ready": True,
        "download_delivery_ready": True,
        "asset_count": len(_ASSET_RECORDS),
        "delivery_event_count": len(_ASSET_DELIVERY_EVENTS),
        "credential_values_exposed": False,
        "customer_safe": True,
    }
''',
encoding="utf-8",
)


VIEWER_RUNTIME.write_text(
r'''from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Dict, List

from backend.app.runtime.asset_storage_signed_delivery_runtime import create_signed_asset_delivery_packet


PROVIDERS_CHECKED = ["elevenlabs", "runway", "heygen", "kling", "sync", "openai_image", "internal"]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _backend_base_url() -> str:
    return (
        os.getenv("API_BASE_URL")
        or os.getenv("BACKEND_BASE_URL")
        or os.getenv("PUBLIC_BACKEND_BASE_URL")
        or "https://api.trance-formation.com.au"
    ).rstrip("/")


def _signed_gateway_url(asset_id: str, delivery_type: str = "preview") -> str:
    packet = create_signed_asset_delivery_packet(
        tenant_id="owner_admin",
        asset_id=asset_id,
        delivery_type=delivery_type,
        expires_in_seconds=86400,
    )

    if packet.get("status") != "ready" or not packet.get("delivery_url"):
        return ""

    return f"{_backend_base_url()}{packet.get('delivery_url')}"


def _safe_asset(asset: Dict[str, Any]) -> Dict[str, Any]:
    asset_id = str(asset.get("asset_id") or "").strip()
    provider = asset.get("provider") or asset.get("provider_key") or "internal"
    asset_type = asset.get("asset_type") or asset.get("media_type") or "creative_asset"

    gateway_preview_url = _signed_gateway_url(asset_id, "preview") if asset_id else ""
    gateway_download_url = _signed_gateway_url(asset_id, "download") if asset_id else ""

    original_preview_url = asset.get("preview_url") or asset.get("provider_asset_url") or asset.get("asset_url") or asset.get("media_url") or ""
    original_download_url = asset.get("download_url") or asset.get("provider_asset_url") or asset.get("asset_url") or asset.get("media_url") or original_preview_url or ""

    preview_url = gateway_preview_url or original_preview_url
    download_url = gateway_download_url or original_download_url

    return {
        "asset_id": asset_id or asset.get("asset_id"),
        "agent_id": asset.get("agent_id") or asset.get("agent_key") or asset.get("requested_agent"),
        "agent_label": asset.get("agent_label") or asset.get("agent_id") or asset.get("agent_key"),
        "provider": provider,
        "provider_key": provider,
        "asset_type": asset_type,
        "media_type": asset_type,
        "title": asset.get("title") or asset.get("test_label") or str(asset_type).replace("_", " ").title(),
        "status": asset.get("status") or asset.get("asset_status") or "persisted",
        "test_label": asset.get("test_label"),
        "provider_asset_id": asset.get("provider_asset_id"),
        "provider_asset_url": asset.get("provider_asset_url"),
        "preview_url": preview_url,
        "download_url": download_url,
        "original_preview_url": original_preview_url,
        "original_download_url": original_download_url,
        "preview_ready": bool(preview_url or asset.get("content") or asset.get("summary")),
        "download_ready": bool(download_url),
        "content": asset.get("content"),
        "summary": asset.get("summary"),
        "quality_score": asset.get("quality_score"),
        "campaign_context": asset.get("campaign_context"),
        "target_audience": asset.get("target_audience"),
        "usage_rights": asset.get("usage_rights"),
        "owner_approval_required": bool(asset.get("owner_approval_required", False)),
        "governed": True,
        "customer_safe": True,
        "credential_values_exposed": False,
        "created_at": asset.get("created_at"),
    }


def get_admin_creative_media_asset_viewer_status() -> Dict[str, Any]:
    return {
        "success": True,
        "layer": "admin_creative_media_asset_viewer",
        "status": "ready",
        "source": "creative_asset_persistence_bridge",
        "delivery_mode": "signed_backend_asset_gateway",
        "providers_checked": PROVIDERS_CHECKED,
        "credential_values_exposed": False,
        "external_actions_performed": False,
        "live_provider_calls_triggered": False,
        "customer_safe_visibility": True,
        "verified_at": _now(),
    }


def get_admin_creative_media_assets(limit: int = 50) -> Dict[str, Any]:
    try:
        from backend.app.runtime.creative_asset_persistence_bridge import get_persisted_creative_assets

        registry = get_persisted_creative_assets(limit=max(int(limit or 50), 1))
        raw_assets = registry.get("assets", []) if isinstance(registry, dict) else []

        assets: List[Dict[str, Any]] = []
        for asset in raw_assets:
            if isinstance(asset, dict):
                assets.append(_safe_asset(asset))

        return {
            "success": True,
            "layer": "admin_creative_media_asset_viewer",
            "status": "ready",
            "source": "creative_asset_persistence_bridge",
            "delivery_mode": "signed_backend_asset_gateway",
            "asset_count": len(assets),
            "total_asset_count": registry.get("total_asset_count", len(assets)) if isinstance(registry, dict) else len(assets),
            "assets": assets,
            "providers_checked": registry.get("providers_checked", PROVIDERS_CHECKED) if isinstance(registry, dict) else PROVIDERS_CHECKED,
            "credential_values_exposed": False,
            "external_actions_performed": False,
            "live_provider_calls_triggered": False,
            "customer_safe_visibility": True,
            "verified_at": _now(),
        }

    except Exception as exc:
        return {
            "success": False,
            "layer": "admin_creative_media_asset_viewer",
            "status": "unavailable",
            "source": "creative_asset_persistence_bridge",
            "delivery_mode": "signed_backend_asset_gateway",
            "asset_count": 0,
            "total_asset_count": 0,
            "assets": [],
            "providers_checked": PROVIDERS_CHECKED,
            "error": str(exc)[:1000],
            "credential_values_exposed": False,
            "external_actions_performed": False,
            "live_provider_calls_triggered": False,
            "customer_safe_visibility": True,
            "verified_at": _now(),
        }
''',
encoding="utf-8",
)


main_text = MAIN_FILE.read_text(encoding="utf-8")
start = main_text.find('@app.get("/asset-delivery/{delivery_type}/{asset_id}")')

if start == -1:
    raise SystemExit("asset-delivery route not found in backend/app/main.py")

next_route = main_text.find("\n@app.", start + 1)
if next_route == -1:
    next_route = len(main_text)

new_route = r'''@app.get("/asset-delivery/{delivery_type}/{asset_id}")
async def asset_delivery(delivery_type: str, asset_id: str, expires: int, nonce: str, sig: str):
    from fastapi.responses import FileResponse, JSONResponse, RedirectResponse

    try:
        result = build_customer_safe_delivery_response(
            asset_id=asset_id,
            delivery_type=delivery_type,
            expires_at_ms=expires,
            nonce=nonce,
            signature=sig,
        )

        status_code = int(result.get("http_status", 200) or 200)

        if status_code >= 400:
            return JSONResponse(status_code=status_code, content=result)

        serve_file_path = result.get("serve_file_path")
        if serve_file_path:
            filename = result.get("filename")
            content_type = result.get("content_type") or "application/octet-stream"
            if filename:
                return FileResponse(path=serve_file_path, media_type=content_type, filename=filename)
            return FileResponse(path=serve_file_path, media_type=content_type)

        redirect_url = result.get("redirect_url")
        if redirect_url:
            return RedirectResponse(url=redirect_url, status_code=302)

        return JSONResponse(status_code=status_code, content=result)

    except Exception as exc:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "status": "delivery_failed",
                "error": str(exc),
                "credential_values_exposed": False,
                "customer_safe": True,
            },
        )
'''

main_text = main_text[:start] + new_route + main_text[next_route:]
MAIN_FILE.write_text(main_text, encoding="utf-8")

print("SIGNED_MEDIA_ASSET_DELIVERY_GATEWAY_FIXED")
print("Updated:", DELIVERY_RUNTIME)
print("Updated:", VIEWER_RUNTIME)
print("Updated:", MAIN_FILE)
print("Backup:", backup_dir)