from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP_DIR = ROOT / "backups" / f"provider_asset_delivery_packet_runtime_before_{STAMP}"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

runtime_path = ROOT / "backend" / "app" / "runtime" / "provider_asset_delivery_packet_runtime.py"
test_path = ROOT / "test_provider_asset_delivery_packet_runtime.py"

for path in [runtime_path, test_path]:
    if path.exists():
        backup = BACKUP_DIR / path.relative_to(ROOT)
        backup.parent.mkdir(parents=True, exist_ok=True)
        backup.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")

runtime_path.parent.mkdir(parents=True, exist_ok=True)

runtime_path.write_text(r'''
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, List
from uuid import uuid4

from backend.app.runtime.provider_job_persistence_runtime import get_provider_job

_DELIVERY_PACKETS: Dict[str, Dict[str, Any]] = {}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe(packet: Dict[str, Any]) -> Dict[str, Any]:
    safe = deepcopy(packet)
    safe.pop("provider_secret", None)
    safe.pop("api_key", None)
    safe.pop("secret", None)
    safe["credential_values_exposed"] = False
    safe["customer_safe"] = True
    return safe


def create_delivery_packet_from_provider_job(job_id: str) -> Dict[str, Any]:
    found = get_provider_job(job_id)

    if not found.get("success"):
        return {
            "success": False,
            "status": "not_found",
            "error": "provider_job_not_found",
            "job_id": job_id,
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    job = found["job"]

    if job.get("status") != "completed":
        return {
            "success": False,
            "status": "blocked",
            "error": "provider_job_not_completed",
            "job_id": job_id,
            "job_status": job.get("status"),
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    assets: List[Dict[str, Any]] = job.get("asset_records") or []

    if not assets:
        return {
            "success": False,
            "status": "blocked",
            "error": "provider_job_has_no_assets",
            "job_id": job_id,
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    packet_id = f"delivery_packet_{uuid4().hex[:14]}"

    packet = {
        "packet_id": packet_id,
        "job_id": job_id,
        "tenant_id": job.get("tenant_id"),
        "execution_id": job.get("execution_id"),
        "provider": job.get("provider"),
        "delivery_status": "ready",
        "asset_count": len(assets),
        "assets": deepcopy(assets),
        "created_at": _now(),
        "updated_at": _now(),
        "credential_values_exposed": False,
        "customer_safe": True,
    }

    _DELIVERY_PACKETS[packet_id] = packet

    return {
        "success": True,
        "status": "ready",
        "delivery_packet": _safe(packet),
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def get_delivery_packet(packet_id: str) -> Dict[str, Any]:
    key = str(packet_id or "").strip()

    if key not in _DELIVERY_PACKETS:
        return {
            "success": False,
            "status": "not_found",
            "error": "delivery_packet_not_found",
            "packet_id": key,
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    return {
        "success": True,
        "status": "found",
        "delivery_packet": _safe(_DELIVERY_PACKETS[key]),
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def list_delivery_packets(tenant_id: str = "", execution_id: str = "") -> Dict[str, Any]:
    clean_tenant = str(tenant_id or "").strip()
    clean_execution = str(execution_id or "").strip()

    packets = []
    for packet in _DELIVERY_PACKETS.values():
        if clean_tenant and packet.get("tenant_id") != clean_tenant:
            continue
        if clean_execution and packet.get("execution_id") != clean_execution:
            continue
        packets.append(_safe(packet))

    return {
        "success": True,
        "status": "listed",
        "packet_count": len(packets),
        "delivery_packets": packets,
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def get_provider_asset_delivery_packet_status() -> Dict[str, Any]:
    return {
        "success": True,
        "provider_asset_delivery_packet_ready": True,
        "completed_job_packet_creation_enabled": True,
        "asset_execution_linking_enabled": True,
        "failed_job_delivery_blocking_enabled": True,
        "customer_safe_delivery_packets_enabled": True,
        "credential_values_exposed": False,
        "customer_safe": True,
    }
''', encoding="utf-8")

test_path.write_text(r'''
from backend.app.runtime.async_provider_worker_runtime import enqueue_async_provider_job, process_provider_job
from backend.app.runtime.provider_asset_delivery_packet_runtime import (
    create_delivery_packet_from_provider_job,
    get_delivery_packet,
    get_provider_asset_delivery_packet_status,
    list_delivery_packets,
)
from backend.app.runtime.provider_job_persistence_runtime import create_provider_job

status = get_provider_asset_delivery_packet_status()
assert status["provider_asset_delivery_packet_ready"] is True
assert status["credential_values_exposed"] is False

queued = enqueue_async_provider_job({
    "tenant_id": "delivery-packet-test-tenant",
    "execution_id": "delivery_execution_001",
    "provider": "openai",
    "job_type": "image_generation",
    "requested_asset_type": "image",
})

job_id = queued["job"]["job_id"]
completed = process_provider_job(job_id)
assert completed["status"] == "completed"

packet = create_delivery_packet_from_provider_job(job_id)
assert packet["success"] is True
assert packet["status"] == "ready"
assert packet["delivery_packet"]["job_id"] == job_id
assert packet["delivery_packet"]["execution_id"] == "delivery_execution_001"
assert packet["delivery_packet"]["asset_count"] == 1
assert packet["credential_values_exposed"] is False

packet_id = packet["delivery_packet"]["packet_id"]

found = get_delivery_packet(packet_id)
assert found["success"] is True
assert found["delivery_packet"]["delivery_status"] == "ready"

listed = list_delivery_packets(tenant_id="delivery-packet-test-tenant")
assert listed["success"] is True
assert listed["packet_count"] >= 1

incomplete = create_provider_job({
    "tenant_id": "delivery-packet-test-tenant",
    "execution_id": "delivery_execution_002",
    "provider": "openai",
    "job_type": "image_generation",
    "requested_asset_type": "image",
})

blocked = create_delivery_packet_from_provider_job(incomplete["job"]["job_id"])
assert blocked["success"] is False
assert blocked["error"] == "provider_job_not_completed"

missing = create_delivery_packet_from_provider_job("missing_job")
assert missing["success"] is False
assert missing["error"] == "provider_job_not_found"

print("PROVIDER_ASSET_DELIVERY_PACKET_RUNTIME_TESTS_PASSED")
print("status_ready", status["provider_asset_delivery_packet_ready"])
print("packet_status", packet["status"])
print("found_status", found["status"])
print("listed_packet_count", listed["packet_count"])
print("blocked_error", blocked["error"])
print("missing_error", missing["error"])
''', encoding="utf-8")

print("PROVIDER_ASSET_DELIVERY_PACKET_RUNTIME_INSTALLED")
print(f"Backup folder: {BACKUP_DIR}")
print(f"Created/updated: {runtime_path}")
print(f"Created/updated: {test_path}")