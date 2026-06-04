from __future__ import annotations

import hashlib
import hmac
import os
import time
import uuid
from typing import Any, Dict, List, Optional


_ASSET_RECORDS: Dict[str, Dict[str, Any]] = {}
_ASSET_DELIVERY_EVENTS: List[Dict[str, Any]] = []


def _now_ms() -> int:
    return int(time.time() * 1000)


def _sign_payload(payload: str) -> str:
    secret = (
        os.getenv("ASSET_PACKET_SIGNING_SECRET")
        or os.getenv("ADMIN_AUTH_SECRET")
        or "dev-asset-signing-secret"
    )
    return hmac.new(secret.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()


def _safe_metadata(metadata: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    safe_metadata: Dict[str, Any] = {}
    for key, value in (metadata or {}).items():
        lower_key = str(key).lower()
        if "secret" in lower_key or "token" in lower_key or "key" in lower_key:
            continue
        safe_metadata[key] = value
    return safe_metadata


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
        "storage_key": storage_key or f"{tenant_id}/{request_id}/{asset_id}",
        "metadata": _safe_metadata(metadata),
        "created_at_ms": now,
        "updated_at_ms": now,
        "credential_values_exposed": False,
        "customer_safe": True,
    }

    _ASSET_RECORDS[asset_id] = record
    return record


def get_asset_record(asset_id: str) -> Dict[str, Any]:
    return _ASSET_RECORDS.get(asset_id) or {
        "status": "not_found",
        "asset_id": asset_id,
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def list_asset_records(
    *,
    tenant_id: Optional[str] = None,
    request_id: Optional[str] = None,
    provider_key: Optional[str] = None,
    limit: int = 100,
) -> Dict[str, Any]:
    records = list(_ASSET_RECORDS.values())

    if tenant_id:
        records = [record for record in records if record.get("tenant_id") == tenant_id]
    if request_id:
        records = [record for record in records if record.get("request_id") == request_id]
    if provider_key:
        records = [record for record in records if record.get("provider_key") == provider_key]

    records = sorted(records, key=lambda record: record.get("created_at_ms", 0), reverse=True)[:limit]

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
    record = _ASSET_RECORDS.get(asset_id)
    if not record:
        return {
            "status": "not_found",
            "asset_id": asset_id,
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    record["asset_status"] = asset_status
    record["updated_at_ms"] = _now_ms()

    if metadata:
        safe_metadata = dict(record.get("metadata") or {})
        safe_metadata.update(_safe_metadata(metadata))
        record["metadata"] = safe_metadata

    record["credential_values_exposed"] = False
    record["customer_safe"] = True
    return record


def create_signed_asset_delivery_packet(
    *,
    tenant_id: str,
    asset_id: str,
    delivery_type: str = "preview",
    expires_in_seconds: int = 3600,
) -> Dict[str, Any]:
    record = get_asset_record(asset_id)
    if record.get("status") == "not_found":
        return {
            "status": "not_found",
            "asset_id": asset_id,
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    if record.get("tenant_id") != tenant_id:
        return {
            "status": "blocked",
            "reason": "tenant_asset_mismatch",
            "asset_id": asset_id,
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    delivery_type = str(delivery_type or "preview").strip().lower()
    expires_at_ms = _now_ms() + int(expires_in_seconds * 1000)
    nonce = uuid.uuid4().hex
    payload = f"{tenant_id}:{asset_id}:{delivery_type}:{expires_at_ms}:{nonce}"
    signature = _sign_payload(payload)

    packet = {
        "status": "ready",
        "asset_id": asset_id,
        "tenant_id": tenant_id,
        "delivery_type": delivery_type,
        "expires_at_ms": expires_at_ms,
        "nonce": nonce,
        "signature": signature,
        "signed_delivery_token_present": True,
        "delivery_url": f"/asset-delivery/{delivery_type}/{asset_id}?expires={expires_at_ms}&nonce={nonce}&sig={signature}",
        "credential_values_exposed": False,
        "customer_safe": True,
    }

    _ASSET_DELIVERY_EVENTS.append(
        {
            "event_id": f"asset_delivery_{uuid.uuid4().hex[:16]}",
            "tenant_id": tenant_id,
            "asset_id": asset_id,
            "delivery_type": delivery_type,
            "event_type": "signed_delivery_packet_created",
            "created_at_ms": _now_ms(),
            "credential_values_exposed": False,
            "customer_safe": True,
        }
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

    delivery_type = str(delivery_type or "preview").strip().lower()
    expected = _sign_payload(f"{tenant_id}:{asset_id}:{delivery_type}:{expires_at_ms}:{nonce}")
    valid = hmac.compare_digest(expected, str(signature or ""))

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

    if record.get("tenant_id") != tenant_id:
        return {
            "status": "blocked",
            "reason": "tenant_asset_mismatch",
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    packet = create_signed_asset_delivery_packet(
        tenant_id=tenant_id,
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

    tenant_id = record.get("tenant_id")
    verification = verify_signed_asset_delivery_packet(
        tenant_id=tenant_id,
        asset_id=asset_id,
        delivery_type=delivery_type,
        expires_at_ms=int(expires_at_ms),
        nonce=nonce,
        signature=signature,
    )

    if not verification.get("valid"):
        return {
            "success": False,
            "status": "blocked",
            "reason": verification.get("reason") or "invalid_delivery_signature",
            "asset_id": asset_id,
            "http_status": 403,
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    _ASSET_DELIVERY_EVENTS.append(
        {
            "event_id": f"asset_delivery_{uuid.uuid4().hex[:16]}",
            "tenant_id": tenant_id,
            "asset_id": asset_id,
            "delivery_type": delivery_type,
            "event_type": "signed_delivery_packet_used",
            "created_at_ms": _now_ms(),
            "credential_values_exposed": False,
            "customer_safe": True,
        }
    )

    safe_asset = {
        "asset_id": record.get("asset_id"),
        "tenant_id": record.get("tenant_id"),
        "request_id": record.get("request_id"),
        "provider_key": record.get("provider_key"),
        "asset_type": record.get("asset_type"),
        "asset_status": record.get("asset_status"),
        "source_url_present": bool(record.get("source_url_present")),
        "metadata": record.get("metadata") or {},
        "created_at_ms": record.get("created_at_ms"),
        "updated_at_ms": record.get("updated_at_ms"),
        "credential_values_exposed": False,
        "customer_safe": True,
    }

    return {
        "success": True,
        "status": "ready",
        "delivery_type": delivery_type,
        "asset": safe_asset,
        "delivery": {
            "mode": "metadata_fallback",
            "content_type": "application/json",
            "download_ready": delivery_type == "download",
            "preview_ready": delivery_type == "preview",
            "internal_storage_key_exposed": False,
        },
        "credential_values_exposed": False,
        "customer_safe": True,
        "http_status": 200,
    }


def list_asset_delivery_events(
    *,
    tenant_id: Optional[str] = None,
    asset_id: Optional[str] = None,
    limit: int = 100,
) -> Dict[str, Any]:
    events = list(_ASSET_DELIVERY_EVENTS)

    if tenant_id:
        events = [event for event in events if event.get("tenant_id") == tenant_id]
    if asset_id:
        events = [event for event in events if event.get("asset_id") == asset_id]

    events = sorted(events, key=lambda event: event.get("created_at_ms", 0), reverse=True)[:limit]

    return {
        "events": events,
        "count": len(events),
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def asset_storage_signed_delivery_status() -> Dict[str, Any]:
    return {
        "asset_storage_runtime_ready": True,
        "storage_mode": "metadata_fallback",
        "signed_delivery_ready": True,
        "preview_delivery_ready": True,
        "download_delivery_ready": True,
        "asset_count": len(_ASSET_RECORDS),
        "delivery_event_count": len(_ASSET_DELIVERY_EVENTS),
        "credential_values_exposed": False,
        "customer_safe": True,
    }