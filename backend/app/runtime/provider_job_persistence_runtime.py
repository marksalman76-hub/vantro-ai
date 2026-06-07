from __future__ import annotations

from typing import Any, Dict, List

from backend.app.runtime.durable_provider_execution_ledger import (
    create_provider_job as durable_create_provider_job,
    get_provider_job as durable_get_provider_job,
    list_provider_job_events as durable_list_provider_job_events,
    list_provider_jobs as durable_list_provider_jobs,
    update_provider_job_status as durable_update_provider_job_status,
)


VALID_JOB_STATUSES = {
    "queued",
    "running",
    "polling",
    "completed",
    "failed",
    "retry_scheduled",
    "timed_out",
    "cancelled",
    "manual_review_required",
    "dead_letter",
}


def _safe_job(job: Dict[str, Any]) -> Dict[str, Any]:
    safe = dict(job or {})
    safe.pop("provider_secret", None)
    safe.pop("api_key", None)
    safe.pop("secret", None)
    safe["job_id"] = safe.get("job_id") or safe.get("provider_job_id")
    safe["provider_job_reference"] = safe.get("provider_job_reference") or safe.get("provider_external_job_id")
    safe["credential_values_exposed"] = False
    safe["customer_safe"] = True
    return safe


def create_provider_job(payload: Dict[str, Any]) -> Dict[str, Any]:
    result = durable_create_provider_job(payload)
    if not result.get("success"):
        return result
    return {
        "success": True,
        "status": result.get("status", "queued"),
        "job": _safe_job(result.get("job", {})),
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def update_provider_job_status(
    job_id: str,
    status: str,
    *,
    result_payload: Dict[str, Any] | None = None,
    error: str | None = None,
    provider_job_reference: str | None = None,
    asset_records: List[Dict[str, Any]] | None = None,
    next_retry_at: str | None = None,
) -> Dict[str, Any]:
    clean_status = str(status or "").strip().lower()
    if clean_status not in VALID_JOB_STATUSES:
        return {
            "success": False,
            "status": "invalid_status",
            "error": "invalid_provider_job_status",
            "job_id": job_id,
            "allowed_statuses": sorted(VALID_JOB_STATUSES),
            "credential_values_exposed": False,
            "customer_safe": True,
        }
    result = durable_update_provider_job_status(
        job_id,
        clean_status,
        result_payload=result_payload,
        error=error,
        provider_job_reference=provider_job_reference,
        asset_records=asset_records,
        next_retry_at=next_retry_at,
        polling_status="polling" if clean_status == "polling" else None,
    )
    if not result.get("success"):
        return result
    return {
        "success": True,
        "status": clean_status,
        "job": _safe_job(result.get("job", {})),
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def get_provider_job(job_id: str) -> Dict[str, Any]:
    result = durable_get_provider_job(job_id)
    if not result.get("success"):
        return result
    return {
        "success": True,
        "status": "found",
        "job": _safe_job(result.get("job", {})),
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def list_provider_jobs(status: str = "", tenant_id: str = "", provider: str = "", execution_id: str = "") -> Dict[str, Any]:
    result = durable_list_provider_jobs(status=status, tenant_id=tenant_id, provider=provider, execution_id=execution_id)
    jobs = [_safe_job(job) for job in result.get("jobs", [])]
    return {
        "success": bool(result.get("success", True)),
        "status": "listed",
        "job_count": len(jobs),
        "jobs": jobs,
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def list_provider_job_events(job_id: str = "") -> Dict[str, Any]:
    result = durable_list_provider_job_events(job_id=job_id)
    return {
        "success": bool(result.get("success", True)),
        "status": "listed",
        "event_count": result.get("event_count", 0),
        "events": result.get("events", []),
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def get_provider_job_persistence_status() -> Dict[str, Any]:
    listed = list_provider_jobs()
    return {
        "success": True,
        "provider_job_persistence_ready": True,
        "queued_job_persistence_enabled": True,
        "status_update_enabled": True,
        "asset_record_linking_enabled": True,
        "provider_job_event_log_enabled": True,
        "canonical_durable_provider_ledger": True,
        "job_count": listed.get("job_count", 0),
        "credential_values_exposed": False,
        "customer_safe": True,
    }
