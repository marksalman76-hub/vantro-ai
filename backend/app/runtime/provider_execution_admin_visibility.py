
from __future__ import annotations

from typing import Any, Dict

from backend.app.runtime.provider_asset_delivery_packet_runtime import list_delivery_packets
from backend.app.runtime.provider_job_persistence_runtime import list_provider_job_events, list_provider_jobs
from backend.app.runtime.provider_retry_timeout_orchestration import list_retry_ready_provider_jobs


def get_provider_execution_admin_visibility(tenant_id: str = "", provider: str = "") -> Dict[str, Any]:
    queued = list_provider_jobs(status="queued", tenant_id=tenant_id, provider=provider)
    running = list_provider_jobs(status="running", tenant_id=tenant_id, provider=provider)
    completed = list_provider_jobs(status="completed", tenant_id=tenant_id, provider=provider)
    failed = list_provider_jobs(status="failed", tenant_id=tenant_id, provider=provider)
    timed_out = list_provider_jobs(status="timed_out", tenant_id=tenant_id, provider=provider)
    retry_scheduled = list_provider_jobs(status="retry_scheduled", tenant_id=tenant_id, provider=provider)
    retry_ready = list_retry_ready_provider_jobs()
    packets = list_delivery_packets(tenant_id=tenant_id)
    events = list_provider_job_events()

    summary = {
        "tenant_filter": tenant_id or "all",
        "provider_filter": provider or "all",
        "queued_job_count": queued.get("job_count", 0),
        "running_job_count": running.get("job_count", 0),
        "completed_job_count": completed.get("job_count", 0),
        "failed_job_count": failed.get("job_count", 0),
        "timed_out_job_count": timed_out.get("job_count", 0),
        "retry_scheduled_job_count": retry_scheduled.get("job_count", 0),
        "retry_ready_job_count": retry_ready.get("ready_count", 0),
        "delivery_packet_count": packets.get("packet_count", 0),
        "provider_job_event_count": events.get("event_count", 0),
    }

    recent_jobs = (
        queued.get("jobs", []) +
        running.get("jobs", []) +
        completed.get("jobs", []) +
        failed.get("jobs", []) +
        timed_out.get("jobs", []) +
        retry_scheduled.get("jobs", [])
    )[-20:]

    return {
        "success": True,
        "provider_execution_admin_visibility_ready": True,
        "summary": summary,
        "recent_jobs": recent_jobs,
        "recent_delivery_packets": packets.get("delivery_packets", [])[-10:],
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def get_provider_execution_admin_visibility_status() -> Dict[str, Any]:
    return {
        "success": True,
        "provider_execution_admin_visibility_ready": True,
        "queued_running_completed_failed_visible": True,
        "retry_timeout_visibility_enabled": True,
        "delivery_packet_visibility_enabled": True,
        "customer_safe_admin_summary_enabled": True,
        "credential_values_exposed": False,
        "customer_safe": True,
    }
