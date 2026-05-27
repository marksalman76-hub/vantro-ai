
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
