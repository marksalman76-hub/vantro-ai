from __future__ import annotations

from typing import Any, Dict, Optional

from backend.app.runtime.provider_job_persistence_runtime import (
    create_provider_job,
    get_provider_job,
    list_provider_jobs,
    update_provider_job_status,
)


VALID_JOB_STATUSES = {
    "queued",
    "running",
    "polling",
    "completed",
    "failed",
    "cancelled",
    "manual_review_required",
}


def create_async_provider_job(
    *,
    tenant_id: str,
    actor_role: str,
    provider_key: str,
    capability: str,
    request_payload: Optional[Dict[str, Any]] = None,
    owner_approval_required: bool = True,
) -> Dict[str, Any]:
    created = create_provider_job(
        {
            "tenant_id": tenant_id,
            "provider": provider_key,
            "job_type": capability,
            "request_payload": request_payload or {},
            "owner_approval_required": owner_approval_required,
            "actor_role": actor_role,
        }
    )
    if not created.get("success"):
        return {
            "found": False,
            "success": False,
            "status": created.get("status"),
            "error": created.get("error") or created.get("reason"),
            "provider_ledger_response": created,
            "credential_values_exposed": False,
            "customer_safe": True,
        }
    job = created.get("job", {})
    return {
        "found": True,
        **job,
        "provider_key": job.get("provider") or provider_key,
        "capability": capability,
        "owner_approval_required": owner_approval_required,
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def get_async_provider_job(job_id: str) -> Dict[str, Any]:
    found = get_provider_job(job_id)
    if not found.get("success"):
        return {
            "found": False,
            "job_id": job_id,
            "error": "job_not_found",
            "credential_values_exposed": False,
            "customer_safe": True,
        }
    return {"found": True, **found.get("job", {})}


def list_async_provider_jobs(*, tenant_id: Optional[str] = None, status: Optional[str] = None) -> Dict[str, Any]:
    listed = list_provider_jobs(status=status or "", tenant_id=tenant_id or "")
    return {
        "status": "ok",
        "job_runtime": "async_provider_job_runtime_v2_durable_wrapper",
        "job_count": listed.get("job_count", 0),
        "jobs": listed.get("jobs", []),
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def update_async_provider_job_status(
    *,
    job_id: str,
    status: str,
    provider_job_id: Optional[str] = None,
    provider_status: Optional[str] = None,
    failure_reason: Optional[str] = None,
    asset_delivery_packet: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    if status not in VALID_JOB_STATUSES:
        return {
            "updated": False,
            "job_id": job_id,
            "error": "invalid_job_status",
            "allowed_statuses": sorted(VALID_JOB_STATUSES),
            "credential_values_exposed": False,
        }
    updated = update_provider_job_status(
        job_id,
        status,
        provider_job_reference=provider_job_id,
        error=failure_reason,
        result_payload={"provider_status": provider_status} if provider_status else None,
        asset_records=[asset_delivery_packet] if asset_delivery_packet else None,
    )
    if not updated.get("success"):
        return {"updated": False, **updated}
    return {"updated": True, **updated.get("job", {})}


def mark_async_provider_job_retry(job_id: str, reason: str) -> Dict[str, Any]:
    found = get_provider_job(job_id)
    if not found.get("success"):
        return {
            "updated": False,
            "job_id": job_id,
            "error": "job_not_found",
            "credential_values_exposed": False,
        }
    job = found["job"]
    if int(job.get("attempt_count") or 0) >= int(job.get("max_attempts") or 2):
        return update_async_provider_job_status(
            job_id=job_id,
            status="manual_review_required",
            failure_reason=f"retry_limit_reached: {reason}",
        )
    updated = update_provider_job_status(job_id, "retry_scheduled", error=reason)
    return {"updated": bool(updated.get("success")), **updated.get("job", {})}
