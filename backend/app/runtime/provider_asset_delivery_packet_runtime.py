from __future__ import annotations

from typing import Any, Dict

from backend.app.runtime.durable_provider_execution_ledger import (
    list_delivery_packets as durable_list_delivery_packets,
    record_provider_delivery_packet,
)
from backend.app.runtime.provider_job_persistence_runtime import get_provider_job


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

    assets = job.get("asset_records") or []
    asset_id = ""
    if assets and isinstance(assets[0], dict):
        asset_id = str(assets[0].get("asset_id") or "")

    packet = record_provider_delivery_packet(
        provider_job_id=job.get("provider_job_id") or job.get("job_id") or job_id,
        execution_id=job.get("execution_id") or "",
        asset_id=asset_id,
        delivery_status="ready",
    )

    return {
        "success": bool(packet.get("success")),
        "status": packet.get("status", "ready"),
        "delivery_packet": packet.get("delivery_packet"),
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def get_delivery_packet(packet_id: str) -> Dict[str, Any]:
    packets = durable_list_delivery_packets(limit=500).get("delivery_packets", [])
    for packet in packets:
        if packet.get("packet_id") == packet_id or packet.get("delivery_packet_id") == packet_id:
            return {
                "success": True,
                "status": "found",
                "delivery_packet": packet,
                "credential_values_exposed": False,
                "customer_safe": True,
            }
    return {
        "success": False,
        "status": "not_found",
        "error": "delivery_packet_not_found",
        "packet_id": packet_id,
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def list_delivery_packets(tenant_id: str = "", execution_id: str = "") -> Dict[str, Any]:
    return durable_list_delivery_packets(tenant_id=tenant_id, execution_id=execution_id)


def get_provider_asset_delivery_packet_status() -> Dict[str, Any]:
    return {
        "success": True,
        "provider_asset_delivery_packet_ready": True,
        "completed_job_packet_creation_enabled": True,
        "asset_execution_linking_enabled": True,
        "failed_job_delivery_blocking_enabled": True,
        "customer_safe_delivery_packets_enabled": True,
        "canonical_durable_provider_ledger": True,
        "credential_values_exposed": False,
        "customer_safe": True,
    }
