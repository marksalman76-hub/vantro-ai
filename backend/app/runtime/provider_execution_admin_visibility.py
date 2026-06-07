from __future__ import annotations

from typing import Any, Dict

from backend.app.runtime.durable_provider_execution_ledger import get_provider_admin_summary
from backend.app.runtime.provider_retry_timeout_orchestration import list_retry_ready_provider_jobs


def get_provider_execution_admin_visibility(tenant_id: str = "", provider: str = "") -> Dict[str, Any]:
    summary = get_provider_admin_summary(tenant_id=tenant_id, provider=provider)
    if not summary.get("success"):
        return summary

    retry_ready = list_retry_ready_provider_jobs()
    summary_payload = dict(summary.get("summary") or {})
    summary_payload["retry_ready_job_count"] = retry_ready.get("ready_count", 0)

    return {
        "success": True,
        "ready": True,
        "provider_execution_admin_visibility_ready": True,
        "summary": summary_payload,
        "execution_records": summary.get("execution_records", []),
        "recent_execution_records": summary.get("recent_execution_records", []),
        "jobs": summary.get("jobs", []),
        "recent_jobs": summary.get("recent_jobs", []),
        "dispatch_attempts": summary.get("dispatch_attempts", []),
        "recent_dispatch_attempts": summary.get("recent_dispatch_attempts", []),
        "retry_history": summary.get("retry_history", []),
        "recent_retry_history": summary.get("recent_retry_history", []),
        "latency_metrics": summary.get("latency_metrics", []),
        "recent_latency_metrics": summary.get("recent_latency_metrics", []),
        "delivery_packets": summary.get("delivery_packets", []),
        "recent_delivery_packets": summary.get("recent_delivery_packets", []),
        "retry_timeout": summary.get("retry_timeout", {}),
        "storage_mode": summary.get("storage_mode"),
        "durable": summary.get("durable", False),
        "dev_only": summary.get("dev_only", False),
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def get_provider_execution_admin_visibility_status() -> Dict[str, Any]:
    summary = get_provider_admin_summary()
    return {
        "success": bool(summary.get("success", True)),
        "ready": bool(summary.get("success", True)),
        "provider_execution_admin_visibility_ready": True,
        "queued_running_completed_failed_visible": True,
        "retry_timeout_visibility_enabled": True,
        "delivery_packet_visibility_enabled": True,
        "customer_safe_admin_summary_enabled": True,
        "canonical_durable_provider_ledger": True,
        "storage_mode": summary.get("storage_mode"),
        "durable": summary.get("durable", False),
        "dev_only": summary.get("dev_only", False),
        "credential_values_exposed": False,
        "customer_safe": True,
    }
