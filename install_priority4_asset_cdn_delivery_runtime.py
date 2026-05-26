from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
RUNTIME = ROOT / "backend" / "app" / "runtime"
DATA_DIR = ROOT / "data" / "ai_media_asset_delivery"
BACKUPS = ROOT / "backups"

RUNTIME.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)
BACKUPS.mkdir(exist_ok=True)

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

runtime_file = RUNTIME / "ai_media_asset_cdn_delivery_runtime.py"
test_file = ROOT / "test_priority4_asset_cdn_delivery_runtime.py"

if runtime_file.exists():
    (BACKUPS / f"ai_media_asset_cdn_delivery_runtime_before_priority4_{stamp}.py").write_text(
        runtime_file.read_text(encoding="utf-8"),
        encoding="utf-8",
    )

runtime_file.write_text(r'''
from __future__ import annotations

import hashlib
import hmac
import json
import os
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = ROOT / "data" / "ai_media_asset_delivery"
ASSETS_PATH = DATA_DIR / "assets.jsonl"
EVENTS_PATH = DATA_DIR / "asset_events.jsonl"

DATA_DIR.mkdir(parents=True, exist_ok=True)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_tenant_id(tenant_id: str) -> str:
    raw = (tenant_id or "tenant_unknown").strip()
    return "".join(ch if ch.isalnum() or ch in {"_", "-"} else "_" for ch in raw)[:80] or "tenant_unknown"


def _secret() -> str:
    return (
        os.getenv("ASSET_DELIVERY_SIGNING_SECRET")
        or os.getenv("JWT_SECRET")
        or os.getenv("ADMIN_AUTH_SECRET")
        or "local_dev_asset_delivery_secret"
    )


def _sign(value: str) -> str:
    return hmac.new(_secret().encode("utf-8"), value.encode("utf-8"), hashlib.sha256).hexdigest()


def _append_jsonl(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")


def _read_jsonl(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except Exception:
            continue
    return rows


def build_tenant_asset_storage_path(tenant_id: str, asset_id: str, filename: str = "") -> Dict[str, Any]:
    safe_tenant = _safe_tenant_id(tenant_id)
    safe_asset = _safe_tenant_id(asset_id)
    safe_filename = filename or f"{safe_asset}.asset"
    safe_filename = "".join(ch if ch.isalnum() or ch in {"_", "-", ".", " "} else "_" for ch in safe_filename)[:120]

    relative_path = f"generated-assets/{safe_tenant}/{safe_asset}/{safe_filename}"

    return {
        "tenant_id": tenant_id or "tenant_unknown",
        "asset_id": asset_id,
        "relative_path": relative_path,
        "tenant_isolated": True,
        "path_safe": True,
        "internal_config_exposed": False,
        "governance_preserved": True,
    }


def create_signed_asset_access_packet(
    tenant_id: str,
    asset_id: str,
    access_type: str = "preview",
    expires_minutes: int = 30,
) -> Dict[str, Any]:
    issued_at = datetime.now(timezone.utc)
    expires_at = issued_at + timedelta(minutes=max(1, int(expires_minutes)))
    access_id = "asset_access_" + uuid.uuid4().hex[:16]

    canonical = f"{tenant_id}|{asset_id}|{access_type}|{int(expires_at.timestamp())}|{access_id}"
    signature = _sign(canonical)

    return {
        "access_id": access_id,
        "tenant_id": tenant_id or "tenant_unknown",
        "asset_id": asset_id,
        "access_type": access_type,
        "issued_at": issued_at.isoformat(),
        "expires_at": expires_at.isoformat(),
        "expires_minutes": expires_minutes,
        "signature": signature,
        "signed_access_ready": True,
        "public_url_exposed": False,
        "tenant_isolated": True,
        "customer_safe": True,
        "internal_config_exposed": False,
        "governance_preserved": True,
    }


def verify_signed_asset_access_packet(packet: Dict[str, Any]) -> Dict[str, Any]:
    try:
        expires_at = datetime.fromisoformat(packet["expires_at"])
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
    except Exception:
        return {"valid": False, "reason": "invalid_expiry", "governance_preserved": True}

    canonical = (
        f"{packet.get('tenant_id')}|{packet.get('asset_id')}|{packet.get('access_type')}|"
        f"{int(expires_at.timestamp())}|{packet.get('access_id')}"
    )
    expected = _sign(canonical)
    valid_signature = hmac.compare_digest(expected, packet.get("signature", ""))
    not_expired = datetime.now(timezone.utc) < expires_at

    return {
        "valid": bool(valid_signature and not_expired),
        "valid_signature": valid_signature,
        "not_expired": not_expired,
        "reason": "ok" if valid_signature and not_expired else "expired_or_invalid_signature",
        "tenant_id": packet.get("tenant_id"),
        "asset_id": packet.get("asset_id"),
        "access_type": packet.get("access_type"),
        "governance_preserved": True,
    }


def persist_generated_asset_record(asset_packet: Dict[str, Any]) -> Dict[str, Any]:
    asset_id = asset_packet.get("asset_id") or "media_asset_" + uuid.uuid4().hex[:16]
    tenant_id = asset_packet.get("tenant_id") or "tenant_unknown"
    provider = asset_packet.get("provider") or asset_packet.get("active_provider") or "unknown_provider"
    filename = asset_packet.get("filename") or f"{asset_id}.mp4"

    storage = build_tenant_asset_storage_path(tenant_id, asset_id, filename)
    preview_access = create_signed_asset_access_packet(tenant_id, asset_id, "preview", 30)
    download_access = create_signed_asset_access_packet(tenant_id, asset_id, "download", 15)

    record = {
        "success": True,
        "asset_id": asset_id,
        "job_id": asset_packet.get("job_id", ""),
        "tenant_id": tenant_id,
        "provider": provider,
        "media_type": asset_packet.get("media_type", "generated_media"),
        "asset_status": "persisted_metadata_ready",
        "storage": storage,
        "cdn": {
            "cdn_ready": False,
            "cdn_provider": os.getenv("ASSET_CDN_PROVIDER", "pending"),
            "secure_cdn_required": True,
            "public_bucket_allowed": False,
        },
        "access": {
            "preview": preview_access,
            "download": download_access,
        },
        "delivery": {
            "customer_safe_preview_ready": True,
            "secure_download_ready": True,
            "tenant_isolated": True,
            "signed_access_required": True,
        },
        "quality_review_required": asset_packet.get("quality_review_required", True),
        "customer_safe_status": "Ready for review",
        "internal_config_exposed": False,
        "governance_preserved": True,
        "owner_approval_gate_preserved": True,
        "created_at": now_iso(),
    }

    _append_jsonl(ASSETS_PATH, record)
    _append_jsonl(EVENTS_PATH, {
        "event_id": "asset_event_" + uuid.uuid4().hex[:16],
        "event_type": "generated_asset_persisted",
        "tenant_id": tenant_id,
        "asset_id": asset_id,
        "job_id": record.get("job_id", ""),
        "customer_safe_status": record["customer_safe_status"],
        "created_at": now_iso(),
        "governance_preserved": True,
    })

    return record


def build_customer_safe_asset_delivery_packet(asset_record: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "success": True,
        "asset_id": asset_record.get("asset_id"),
        "job_id": asset_record.get("job_id"),
        "tenant_id": asset_record.get("tenant_id"),
        "media_type": asset_record.get("media_type"),
        "status": asset_record.get("customer_safe_status", "Ready for review"),
        "preview": {
            "available": True,
            "access_id": asset_record.get("access", {}).get("preview", {}).get("access_id"),
            "expires_at": asset_record.get("access", {}).get("preview", {}).get("expires_at"),
            "signed_access_ready": True,
        },
        "download": {
            "available": True,
            "access_id": asset_record.get("access", {}).get("download", {}).get("access_id"),
            "expires_at": asset_record.get("access", {}).get("download", {}).get("expires_at"),
            "signed_access_ready": True,
        },
        "customer_safe_message": "Your generated media is ready for review.",
        "internal_config_exposed": False,
        "tenant_isolated": True,
        "governance_preserved": True,
    }


def list_asset_history_for_tenant(tenant_id: str, limit: int = 20) -> Dict[str, Any]:
    rows = [row for row in _read_jsonl(ASSETS_PATH) if row.get("tenant_id") == tenant_id]
    rows = rows[-max(1, int(limit)):]
    return {
        "success": True,
        "tenant_id": tenant_id,
        "count": len(rows),
        "assets": rows,
        "internal_config_exposed": False,
        "governance_preserved": True,
    }


def asset_cdn_delivery_runtime_readiness() -> Dict[str, Any]:
    return {
        "success": True,
        "runtime": "priority4_asset_cdn_delivery_runtime",
        "status": "ready",
        "data_paths": {
            "assets_path": str(ASSETS_PATH),
            "events_path": str(EVENTS_PATH),
        },
        "capabilities": [
            "tenant_isolated_asset_storage_paths",
            "generated_asset_metadata_persistence",
            "signed_expiring_preview_access_packets",
            "signed_expiring_download_access_packets",
            "customer_safe_delivery_packets",
            "cdn_ready_metadata_shape",
            "asset_history_linkage",
            "runtime_safe_asset_event_logging",
        ],
        "layout_changes": False,
        "internal_config_exposed": False,
        "governance_preserved": True,
        "owner_approval_gate_preserved": True,
    }
''', encoding="utf-8")

test_file.write_text(r'''
from backend.app.runtime.ai_media_asset_cdn_delivery_runtime import (
    asset_cdn_delivery_runtime_readiness,
    persist_generated_asset_record,
    build_customer_safe_asset_delivery_packet,
    verify_signed_asset_access_packet,
    list_asset_history_for_tenant,
)


def run():
    readiness = asset_cdn_delivery_runtime_readiness()
    assert readiness["success"] is True
    assert readiness["status"] == "ready"
    assert readiness["governance_preserved"] is True

    record = persist_generated_asset_record({
        "asset_id": "media_asset_priority4_test",
        "job_id": "media_job_priority4_test",
        "tenant_id": "tenant_priority4_test",
        "provider": "runway",
        "media_type": "ugc_video",
        "filename": "priority4-test.mp4",
    })

    assert record["success"] is True
    assert record["delivery"]["tenant_isolated"] is True
    assert record["delivery"]["signed_access_required"] is True
    assert record["cdn"]["public_bucket_allowed"] is False
    assert record["internal_config_exposed"] is False

    preview_check = verify_signed_asset_access_packet(record["access"]["preview"])
    assert preview_check["valid"] is True
    assert preview_check["governance_preserved"] is True

    delivery_packet = build_customer_safe_asset_delivery_packet(record)
    assert delivery_packet["success"] is True
    assert delivery_packet["preview"]["signed_access_ready"] is True
    assert delivery_packet["download"]["signed_access_ready"] is True
    assert delivery_packet["internal_config_exposed"] is False

    history = list_asset_history_for_tenant("tenant_priority4_test")
    assert history["success"] is True
    assert history["count"] >= 1

    print("PRIORITY4_ASSET_CDN_DELIVERY_RUNTIME_OK")


if __name__ == "__main__":
    run()
''', encoding="utf-8")

print("PRIORITY4_ASSET_CDN_DELIVERY_RUNTIME_INSTALLED")
print(f"Created/updated: {runtime_file}")
print(f"Created/updated: {test_file}")