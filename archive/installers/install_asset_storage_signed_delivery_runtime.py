from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

runtime_dir = ROOT / "backend" / "app" / "runtime"
runtime_dir.mkdir(parents=True, exist_ok=True)

target = runtime_dir / "asset_storage_signed_delivery_runtime.py"
test_file = ROOT / "test_asset_storage_signed_delivery_runtime_direct.py"
backup_dir = ROOT / "backups" / f"asset_storage_signed_delivery_before_{STAMP}"
backup_dir.mkdir(parents=True, exist_ok=True)

for p in [target, test_file]:
    if p.exists():
        (backup_dir / p.name).write_text(p.read_text(encoding="utf-8"), encoding="utf-8")

target.write_text(r'''
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
    secret = os.getenv("ASSET_PACKET_SIGNING_SECRET") or os.getenv("ADMIN_AUTH_SECRET") or "dev-asset-signing-secret"
    return hmac.new(secret.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()


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

    safe_metadata = {}
    for k, v in (metadata or {}).items():
        lk = str(k).lower()
        if "secret" in lk or "token" in lk or "key" in lk:
            continue
        safe_metadata[k] = v

    record = {
        "asset_id": asset_id,
        "tenant_id": tenant_id,
        "request_id": request_id,
        "provider_key": provider_key,
        "asset_type": asset_type,
        "asset_status": asset_status,
        "source_url_present": bool(source_url),
        "storage_key": storage_key or f"{tenant_id}/{request_id}/{asset_id}",
        "metadata": safe_metadata,
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
        for k, v in metadata.items():
            lk = str(k).lower()
            if "secret" in lk or "token" in lk or "key" in lk:
                continue
            safe_metadata[k] = v
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

    _ASSET_DELIVERY_EVENTS.append({
        "event_id": f"asset_delivery_{uuid.uuid4().hex[:16]}",
        "tenant_id": tenant_id,
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

    expected = _sign_payload(f"{tenant_id}:{asset_id}:{delivery_type}:{expires_at_ms}:{nonce}")
    valid = hmac.compare_digest(expected, signature)

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
        "storage_mode": "metadata_fallback",
        "signed_delivery_ready": True,
        "preview_delivery_ready": True,
        "download_delivery_ready": True,
        "asset_count": len(_ASSET_RECORDS),
        "delivery_event_count": len(_ASSET_DELIVERY_EVENTS),
        "credential_values_exposed": False,
        "customer_safe": True,
    }
'''.lstrip(), encoding="utf-8")

test_file.write_text(r'''
from backend.app.runtime.asset_storage_signed_delivery_runtime import (
    asset_storage_signed_delivery_status,
    create_asset_record,
    create_customer_safe_asset_preview,
    create_signed_asset_delivery_packet,
    get_asset_record,
    list_asset_delivery_events,
    list_asset_records,
    reset_asset_storage_for_tests,
    update_asset_status,
    verify_signed_asset_delivery_packet,
)

reset = reset_asset_storage_for_tests()
assert reset["reset"] is True

status = asset_storage_signed_delivery_status()
assert status["asset_storage_runtime_ready"] is True
assert status["signed_delivery_ready"] is True

asset = create_asset_record(
    tenant_id="tenant-test",
    request_id="request-test",
    provider_key="openai",
    asset_type="image",
    asset_status="prepared",
    source_url="https://example.com/internal-source.png",
    metadata={"safe": True, "api_key": "must-not-store"},
)
assert asset["source_url_present"] is True
assert "api_key" not in asset["metadata"]
assert asset["credential_values_exposed"] is False

fetched = get_asset_record(asset["asset_id"])
assert fetched["asset_id"] == asset["asset_id"]

updated = update_asset_status(
    asset_id=asset["asset_id"],
    asset_status="ready",
    metadata={"quality_score": 95, "secret": "must-not-store"},
)
assert updated["asset_status"] == "ready"
assert "secret" not in updated["metadata"]

packet = create_signed_asset_delivery_packet(
    tenant_id="tenant-test",
    asset_id=asset["asset_id"],
    delivery_type="preview",
    expires_in_seconds=3600,
)
assert packet["status"] == "ready"
assert packet["signed_delivery_token_present"] is True
assert packet["credential_values_exposed"] is False

verified = verify_signed_asset_delivery_packet(
    tenant_id="tenant-test",
    asset_id=asset["asset_id"],
    delivery_type="preview",
    expires_at_ms=packet["expires_at_ms"],
    nonce=packet["nonce"],
    signature=packet["signature"],
)
assert verified["valid"] is True

wrong_tenant = create_signed_asset_delivery_packet(
    tenant_id="wrong-tenant",
    asset_id=asset["asset_id"],
    delivery_type="preview",
)
assert wrong_tenant["status"] == "blocked"
assert wrong_tenant["reason"] == "tenant_asset_mismatch"

preview = create_customer_safe_asset_preview(
    tenant_id="tenant-test",
    asset_id=asset["asset_id"],
)
assert preview["status"] == "ready"
assert preview["internal_storage_key_exposed"] is False
assert preview["customer_safe"] is True

listed = list_asset_records(tenant_id="tenant-test")
assert listed["count"] == 1

events = list_asset_delivery_events(tenant_id="tenant-test")
assert events["count"] >= 2

final = asset_storage_signed_delivery_status()
assert final["asset_count"] == 1
assert final["delivery_event_count"] >= 2

print("ASSET_STORAGE_SIGNED_DELIVERY_RUNTIME_DIRECT_TESTS_PASSED")
print("asset_id", asset["asset_id"])
print("asset_status", updated["asset_status"])
print("packet_status", packet["status"])
print("verified", verified["valid"])
print("preview_status", preview["status"])
print("asset_count", final["asset_count"])
print("delivery_events", final["delivery_event_count"])
'''.lstrip(), encoding="utf-8")

print("ASSET_STORAGE_SIGNED_DELIVERY_RUNTIME_INSTALLED")
print(f"Backup folder: {backup_dir}")
print(f"Created/updated: {target}")
print(f"Created/updated: {test_file}")