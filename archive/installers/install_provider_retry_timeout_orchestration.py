from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP_DIR = ROOT / "backups" / f"provider_retry_timeout_orchestration_before_{STAMP}"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

runtime_path = ROOT / "backend" / "app" / "runtime" / "provider_retry_timeout_orchestration.py"
test_path = ROOT / "test_provider_retry_timeout_orchestration.py"

for path in [runtime_path, test_path]:
    if path.exists():
        backup = BACKUP_DIR / path.relative_to(ROOT)
        backup.parent.mkdir(parents=True, exist_ok=True)
        backup.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")

runtime_path.parent.mkdir(parents=True, exist_ok=True)

runtime_path.write_text(r'''
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

from backend.app.runtime.provider_job_persistence_runtime import (
    get_provider_job,
    list_provider_jobs,
    update_provider_job_status,
)


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
            "failed",
            error="provider_retry_attempts_exhausted",
        )
        return {
            "success": False,
            "status": "retry_exhausted",
            "job": exhausted.get("job"),
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
''', encoding="utf-8")

test_path.write_text(r'''
from backend.app.runtime.provider_job_persistence_runtime import (
    create_provider_job,
    get_provider_job,
    update_provider_job_status,
)
from backend.app.runtime.provider_retry_timeout_orchestration import (
    get_provider_retry_timeout_status,
    list_retry_ready_provider_jobs,
    mark_provider_job_timed_out,
    requeue_retry_ready_provider_jobs,
    schedule_provider_job_retry,
)

status = get_provider_retry_timeout_status()
assert status["provider_retry_timeout_orchestration_ready"] is True
assert status["credential_values_exposed"] is False

created = create_provider_job({
    "tenant_id": "retry-timeout-test-tenant",
    "provider": "openai",
    "job_type": "image_generation",
    "requested_asset_type": "image",
    "max_attempts": 3,
})
job_id = created["job"]["job_id"]

running = update_provider_job_status(job_id, "running")
assert running["status"] == "running"

retry = schedule_provider_job_retry(job_id, reason="provider_rate_limited", delay_seconds=1)
assert retry["success"] is True
assert retry["status"] == "retry_scheduled"
assert retry["job"]["next_retry_at"]

ready = list_retry_ready_provider_jobs()
assert ready["success"] is True

requeued = requeue_retry_ready_provider_jobs(limit=5)
assert requeued["success"] is True
assert requeued["status"] == "requeued"

timed = mark_provider_job_timed_out(job_id)
assert timed["success"] is True
assert timed["status"] == "timed_out"

found = get_provider_job(job_id)
assert found["success"] is True
assert found["job"]["status"] == "timed_out"

exhausted_job = create_provider_job({
    "tenant_id": "retry-timeout-test-tenant",
    "provider": "openai",
    "job_type": "video_generation",
    "requested_asset_type": "video",
    "attempt_count": 3,
    "max_attempts": 3,
})
exhausted = schedule_provider_job_retry(exhausted_job["job"]["job_id"], reason="provider_failed")
assert exhausted["success"] is False
assert exhausted["status"] == "retry_exhausted"

print("PROVIDER_RETRY_TIMEOUT_ORCHESTRATION_TESTS_PASSED")
print("status_ready", status["provider_retry_timeout_orchestration_ready"])
print("retry_status", retry["status"])
print("ready_count", ready["ready_count"])
print("requeued_status", requeued["status"])
print("timed_status", timed["status"])
print("exhausted_status", exhausted["status"])
''', encoding="utf-8")

print("PROVIDER_RETRY_TIMEOUT_ORCHESTRATION_INSTALLED")
print(f"Backup folder: {BACKUP_DIR}")
print(f"Created/updated: {runtime_path}")
print(f"Created/updated: {test_path}")
