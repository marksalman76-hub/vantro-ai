
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

from backend.app.runtime.provider_job_persistence_runtime import (
    get_provider_job,
    list_provider_jobs,
    update_provider_job_status,
)
from backend.app.runtime.durable_provider_execution_ledger import record_provider_retry
from backend.app.runtime.durable_manual_review_recovery_runtime import create_manual_review_item


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.isoformat()


def _parse_iso(value: str) -> datetime | None:
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except Exception:
        return None


def schedule_provider_job_retry(
    job_id: str,
    *,
    reason: str = "provider_job_failed",
    delay_seconds: int = 60,
) -> Dict[str, Any]:
    found = get_provider_job(job_id)

    if not found.get("success"):
        return found

    job = found["job"]
    attempt_count = int(job.get("attempt_count") or 0)
    max_attempts = int(job.get("max_attempts") or 3)

    if attempt_count >= max_attempts:
        exhausted = update_provider_job_status(
            job_id,
            "manual_review_required",
            error="provider_retry_attempts_exhausted",
        )
        record_provider_retry(
            provider_job_id=job_id,
            execution_id=str(job.get("execution_id") or ""),
            retry_reason="provider_retry_attempts_exhausted",
            attempt_number=attempt_count,
            scheduled_for=_now(),
            retry_allowed=False,
            next_action="manual_review_required",
        )
        review = create_manual_review_item(
            tenant_id=str(job.get("tenant_id") or "unknown"),
            project_id=str(job.get("project_id") or "default_project"),
            source_type="provider_job",
            source_id=job_id,
            provider_job_id=job_id,
            provider_execution_id=str(job.get("execution_id") or ""),
            execution_id=str(job.get("execution_id") or ""),
            review_type="provider_retry_exhausted",
            status="manual_review_required",
            priority="high",
            reason="provider_retry_attempts_exhausted",
            summary="Provider retry attempts are exhausted and require owner/admin review.",
            payload={
                "provider_job_id": job_id,
                "attempt_count": attempt_count,
                "max_attempts": max_attempts,
                "last_error": job.get("last_error"),
                "next_action": "manual_review_required",
            },
        )
        return {
            "success": False,
            "status": "manual_review_required",
            "job": exhausted.get("job"),
            "review_item": review.get("item"),
            "reason": "provider_retry_attempts_exhausted",
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    next_retry_at = _iso(_now() + timedelta(seconds=max(1, int(delay_seconds or 60))))

    scheduled = update_provider_job_status(
        job_id,
        "retry_scheduled",
        error=reason,
        next_retry_at=next_retry_at,
    )
    if scheduled.get("success"):
        job_after = scheduled.get("job") or job
        record_provider_retry(
            provider_job_id=job_id,
            execution_id=str(job_after.get("execution_id") or job.get("execution_id") or ""),
            retry_reason=reason,
            attempt_number=attempt_count + 1,
            scheduled_for=next_retry_at,
            retry_allowed=True,
            next_action="retry_scheduled",
        )

    return {
        "success": True,
        "status": "retry_scheduled",
        "job": scheduled.get("job"),
        "next_retry_at": next_retry_at,
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def mark_provider_job_timed_out(job_id: str, *, reason: str = "provider_job_timed_out") -> Dict[str, Any]:
    timed_out = update_provider_job_status(
        job_id,
        "timed_out",
        error=reason,
    )

    if not timed_out.get("success"):
        return timed_out

    return {
        "success": True,
        "status": "timed_out",
        "job": timed_out.get("job"),
        "reason": reason,
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def list_retry_ready_provider_jobs() -> Dict[str, Any]:
    scheduled = list_provider_jobs(status="retry_scheduled").get("jobs", [])
    ready: List[Dict[str, Any]] = []

    current = _now()

    for job in scheduled:
        retry_at = _parse_iso(job.get("next_retry_at"))
        if retry_at is None or retry_at <= current:
            ready.append(job)

    return {
        "success": True,
        "status": "listed",
        "ready_count": len(ready),
        "jobs": ready,
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def requeue_retry_ready_provider_jobs(limit: int = 5) -> Dict[str, Any]:
    ready = list_retry_ready_provider_jobs().get("jobs", [])
    safe_limit = max(1, min(int(limit or 5), 25))
    requeued = []

    for job in ready[:safe_limit]:
        result = update_provider_job_status(
            job["job_id"],
            "queued",
            error=None,
            next_retry_at=None,
        )
        requeued.append(result)

    return {
        "success": True,
        "status": "requeued",
        "requeued_count": len(requeued),
        "results": requeued,
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def mark_stale_running_jobs_timed_out(timeout_seconds: int = 900) -> Dict[str, Any]:
    running = list_provider_jobs(status="running").get("jobs", [])
    current = _now()
    timed_out = []

    for job in running:
        updated_at = _parse_iso(job.get("updated_at") or job.get("created_at"))
        if updated_at is None:
            continue

        age = (current - updated_at).total_seconds()

        if age >= max(1, int(timeout_seconds or 900)):
            timed_out.append(mark_provider_job_timed_out(job["job_id"]))

    return {
        "success": True,
        "status": "timeout_scan_completed",
        "timed_out_count": len(timed_out),
        "results": timed_out,
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def get_provider_retry_timeout_status() -> Dict[str, Any]:
    return {
        "success": True,
        "provider_retry_timeout_orchestration_ready": True,
        "retry_scheduling_enabled": True,
        "max_attempt_enforcement_enabled": True,
        "timeout_marking_enabled": True,
        "retry_ready_pickup_enabled": True,
        "customer_safe_failure_states_enabled": True,
        "credential_values_exposed": False,
        "customer_safe": True,
    }
