from __future__ import annotations

import hashlib
import hmac
import mimetypes
import os
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from backend.app.runtime.canonical_media_asset_metadata_runtime import (
    get_media_asset as canonical_get_media_asset,
    list_asset_delivery_packets as canonical_list_asset_delivery_packets,
    record_asset_access_event,
    record_asset_delivery_packet,
    record_media_asset,
)
from backend.app.runtime.creative_asset_persistence_bridge import is_valid_playable_media_source


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
    return is_valid_playable_media_source(value)


def _is_local_runtime_path(value: Any) -> bool:
    return False


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
    valid_source_url = source_url if _is_browser_url(source_url) else ""
    local_file_path = source_url if _is_local_runtime_path(source_url) else ""
    playable = bool(valid_source_url or local_file_path)

    record = {
        "asset_id": asset_id,
        "tenant_id": tenant_id,
        "request_id": request_id,
        "provider_key": provider_key,
        "asset_type": asset_type,
        "asset_status": asset_status,
        "source_url_present": bool(valid_source_url),
        "source_url": valid_source_url,
        "local_file_path": local_file_path,
        "preview_ready": playable,
        "download_ready": playable,
        "playable": playable,
        "metadata_only": not playable,
        "storage_key": storage_key or f"{tenant_id}/{request_id}/{asset_id}",
        "metadata": _safe_metadata(metadata),
        "created_at_ms": now,
        "updated_at_ms": now,
        "credential_values_exposed": False,
        "customer_safe": True,
    }

    _ASSET_RECORDS[asset_id] = record
    canonical = record_media_asset(
        asset_id=asset_id,
        tenant_id=tenant_id,
        execution_id=request_id,
        provider_job_id=request_id,
        agent_id=str((metadata or {}).get("agent_id") or ""),
        asset_type=asset_type,
        media_type=asset_type,
        status=asset_status,
        storage_provider="provider_url" if valid_source_url else "local_runtime_file" if local_file_path else "metadata_only",
        object_key=record["storage_key"],
        local_path=record["local_file_path"],
        provider_url=record["source_url"],
        preview_url=record["source_url"] or record["local_file_path"],
        download_url=record["source_url"] or record["local_file_path"],
        preview_ready=playable,
        download_ready=playable,
        playable=playable,
        metadata_only=not playable,
        source_runtime="asset_storage_signed_delivery_runtime",
        payload=record,
    )
    record["authority"] = "backend_canonical"
    record["canonical_storage_mode"] = canonical.get("storage_mode")
    record["fallback_used"] = bool(canonical.get("dev_only"))
    record["dev_only"] = bool(canonical.get("dev_only"))
    record["production_fail_closed"] = bool(canonical.get("production_fail_closed"))
    return record


def _canonical_asset_to_record(asset: Dict[str, Any]) -> Dict[str, Any]:
    payload = asset.get("payload") if isinstance(asset.get("payload"), dict) else {}
    source_url = asset.get("provider_url") or asset.get("preview_url") or asset.get("download_url") or ""
    source_url = source_url if _is_browser_url(source_url) else ""
    local_file_path = ""
    return {
        "asset_id": asset.get("asset_id"),
        "tenant_id": asset.get("tenant_id") or "owner_admin",
        "request_id": asset.get("provider_job_id") or asset.get("execution_id") or payload.get("request_id") or "canonical_media_asset_metadata",
        "provider_key": payload.get("provider_key") or payload.get("provider") or "internal",
        "asset_type": asset.get("asset_type") or asset.get("media_type") or "creative_asset",
        "asset_status": asset.get("status") or "persisted",
        "metadata_only": bool(asset.get("metadata_only") or not source_url),
        "playable": bool(asset.get("playable") and source_url),
        "source_url_present": bool(source_url),
        "source_url": source_url,
        "local_file_path": local_file_path,
        "storage_key": asset.get("object_key") or f"canonical_media/{asset.get('asset_id')}",
        "metadata": _safe_metadata(payload),
        "created_at_ms": _now_ms(),
        "updated_at_ms": _now_ms(),
        "authority": "backend_canonical",
        "canonical_storage_mode": asset.get("storage_mode"),
        "credential_values_exposed": False,
        "customer_safe": True,
    }


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
                "metadata_only": bool(asset.get("metadata_only") or not (asset.get("playable") and source_url)),
                "playable": bool(asset.get("playable") and source_url),
                "source_url_present": bool(source_url),
                "source_url": source_url,
                "local_file_path": "",
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
    canonical = canonical_get_media_asset(asset_id)
    if canonical.get("production_fail_closed"):
        return {
            "status": "canonical_media_metadata_unavailable",
            "asset_id": asset_id,
            "reason": canonical.get("reason"),
            "production_fail_closed": True,
            "credential_values_exposed": False,
            "customer_safe": True,
        }
    if canonical.get("success") and canonical.get("asset"):
        return _canonical_asset_to_record(canonical.get("asset") or {})

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
    if record.get("production_fail_closed"):
        return {
            "status": "canonical_media_metadata_unavailable",
            "asset_id": asset_id,
            "production_fail_closed": True,
            "credential_values_exposed": False,
            "customer_safe": True,
        }
    if record.get("status") == "not_found":
        return {
            "status": "not_found",
            "asset_id": asset_id,
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    source_valid = is_valid_playable_media_source(record.get("source_url"))
    if record.get("metadata_only") and not source_valid:
        return {
            "status": "metadata_only",
            "reason": "asset_has_no_playable_delivery_source",
            "asset_id": asset_id,
            "credential_values_exposed": False,
            "customer_safe": True,
        }
    if not source_valid:
        return {
            "status": "blocked_placeholder_source",
            "reason": "placeholder_or_invalid_media_source",
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
    record_asset_delivery_packet(
        tenant_id=record_tenant,
        asset_id=asset_id,
        delivery_packet_id=f"asset_delivery_packet_{nonce}",
        delivery_status="ready",
        preview_ready=delivery_type == "preview",
        download_ready=delivery_type == "download",
        signed_preview_url=packet["delivery_url"] if delivery_type == "preview" else "",
        signed_download_url=packet["delivery_url"] if delivery_type == "download" else "",
        expires_at=datetime.fromtimestamp(expires_at_ms / 1000, timezone.utc),
        payload=packet,
    )
    record_asset_access_event(
        tenant_id=record_tenant,
        asset_id=asset_id,
        event_type="signed_delivery_packet_created",
        actor_role="system",
        payload={"delivery_type": delivery_type, "expires_at_ms": expires_at_ms},
    )

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

    if record.get("production_fail_closed"):
        return {
            "success": False,
            "status": "canonical_media_metadata_unavailable",
            "reason": record.get("reason"),
            "asset_id": asset_id,
            "http_status": 503,
            "production_fail_closed": True,
            "credential_values_exposed": False,
            "customer_safe": True,
        }

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

    if record.get("metadata_only") and not local_file_path and not source_url:
        metadata = record.get("metadata") if isinstance(record.get("metadata"), dict) else {}
        return {
            "success": True,
            "status": "metadata_only",
            "reason": "asset_has_no_playable_delivery_source",
            "delivery_type": delivery_type,
            "asset_id": asset_id,
            "content": metadata.get("content"),
            "summary": metadata.get("summary"),
            "http_status": 200,
            "delivery": {
                "mode": "metadata_fallback",
                "preview_ready": False,
                "download_ready": False,
                "internal_storage_key_exposed": False,
            },
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    if local_file_path and Path(local_file_path).exists():
        record_asset_access_event(
            tenant_id=tenant_id,
            asset_id=asset_id,
            event_type=f"{delivery_type}_local_file_served",
            actor_role="client",
            payload={"delivery_type": delivery_type},
        )
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
        record_asset_access_event(
            tenant_id=tenant_id,
            asset_id=asset_id,
            event_type=f"{delivery_type}_provider_url_redirect",
            actor_role="client",
            payload={"delivery_type": delivery_type},
        )
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
        "status": "metadata_only",
        "reason": "asset_has_no_playable_delivery_source",
        "delivery_type": delivery_type,
        "asset_id": asset_id,
        "content": metadata.get("content"),
        "summary": metadata.get("summary"),
        "http_status": 200,
        "delivery": {
            "mode": "metadata_fallback",
            "preview_ready": False,
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
    canonical = canonical_list_asset_delivery_packets(tenant_id=tenant_id or "", asset_id=asset_id or "", limit=limit)
    if canonical.get("success") and canonical.get("delivery_packets"):
        return {
            "events": canonical.get("delivery_packets", []),
            "count": canonical.get("count", 0),
            "authority": "backend_canonical",
            "fallback_used": False,
            "dev_only": bool(canonical.get("dev_only")),
            "credential_values_exposed": False,
            "customer_safe": True,
        }
    if canonical.get("production_fail_closed"):
        return {
            "events": [],
            "count": 0,
            "authority": "backend_canonical",
            "production_fail_closed": True,
            "credential_values_exposed": False,
            "customer_safe": True,
        }

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
