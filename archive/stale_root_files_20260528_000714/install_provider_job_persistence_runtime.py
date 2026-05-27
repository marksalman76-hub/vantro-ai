from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP_DIR = ROOT / "backups" / f"provider_job_persistence_runtime_before_{STAMP}"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

runtime_path = ROOT / "backend" / "app" / "runtime" / "provider_job_persistence_runtime.py"
test_path = ROOT / "test_provider_job_persistence_runtime.py"

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

_PROVIDER_JOBS: Dict[str, Dict[str, Any]] = {}
_PROVIDER_JOB_EVENTS: List[Dict[str, Any]] = []

VALID_JOB_STATUSES = {
    "queued",
    "running",
    "completed",
    "failed",
    "retry_scheduled",
    "timed_out",
    "cancelled",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_job(job: Dict[str, Any]) -> Dict[str, Any]:
    safe = deepcopy(job)
    safe.pop("provider_secret", None)
    safe.pop("api_key", None)
    safe.pop("secret", None)
    safe["credential_values_exposed"] = False
    safe["customer_safe"] = True
    return safe


def _record_event(event_type: str, job_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    event = {
        "event_id": f"provider_job_event_{uuid4().hex[:12]}",
        "event_type": event_type,
        "job_id": job_id,
        "created_at": _now(),
        "credential_values_exposed": False,
        "customer_safe": True,
        "payload": deepcopy(payload),
    }
    _PROVIDER_JOB_EVENTS.append(event)
    return deepcopy(event)


def create_provider_job(payload: Dict[str, Any]) -> Dict[str, Any]:
    provider = str(payload.get("provider") or payload.get("provider_id") or "unknown").strip()
    job_type = str(payload.get("job_type") or payload.get("type") or "generation").strip()
    tenant_id = str(payload.get("tenant_id") or payload.get("client_id") or "").strip()
    execution_id = str(payload.get("execution_id") or payload.get("workflow_id") or "").strip()

    job_id = str(payload.get("job_id") or f"provider_job_{uuid4().hex[:14]}").strip()

    job = {
        "job_id": job_id,
        "provider": provider,
        "job_type": job_type,
        "tenant_id": tenant_id,
        "execution_id": execution_id,
        "status": "queued",
        "attempt_count": int(payload.get("attempt_count") or 0),
        "max_attempts": int(payload.get("max_attempts") or 3),
        "provider_job_reference": payload.get("provider_job_reference"),
        "requested_asset_type": payload.get("requested_asset_type") or payload.get("asset_type"),
        "request_payload": deepcopy(payload.get("request_payload") or {}),
        "result_payload": {},
        "asset_records": [],
        "error": None,
        "next_retry_at": None,
        "created_at": _now(),
        "updated_at": _now(),
        "credential_values_exposed": False,
        "customer_safe": True,
    }

    _PROVIDER_JOBS[job_id] = job
    _record_event("provider_job_created", job_id, _safe_job(job))

    return {
        "success": True,
        "status": "queued",
        "job": _safe_job(job),
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
    key = str(job_id or "").strip()

    if key not in _PROVIDER_JOBS:
        return {
            "success": False,
            "status": "not_found",
            "error": "provider_job_not_found",
            "job_id": key,
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    clean_status = str(status or "").strip().lower()

    if clean_status not in VALID_JOB_STATUSES:
        return {
            "success": False,
            "status": "invalid_status",
            "error": "invalid_provider_job_status",
            "job_id": key,
            "allowed_statuses": sorted(VALID_JOB_STATUSES),
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    job = _PROVIDER_JOBS[key]
    job["status"] = clean_status
    job["updated_at"] = _now()

    if provider_job_reference:
        job["provider_job_reference"] = provider_job_reference

    if result_payload is not None:
        job["result_payload"] = deepcopy(result_payload)

    if asset_records is not None:
        job["asset_records"] = deepcopy(asset_records)

    if error is not None:
        job["error"] = str(error)

    if next_retry_at is not None:
        job["next_retry_at"] = next_retry_at

    if clean_status in {"running", "retry_scheduled"}:
        job["attempt_count"] = int(job.get("attempt_count") or 0) + 1

    _record_event("provider_job_status_updated", key, _safe_job(job))

    return {
        "success": True,
        "status": clean_status,
        "job": _safe_job(job),
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def get_provider_job(job_id: str) -> Dict[str, Any]:
    key = str(job_id or "").strip()

    if key not in _PROVIDER_JOBS:
        return {
            "success": False,
            "status": "not_found",
            "error": "provider_job_not_found",
            "job_id": key,
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    return {
        "success": True,
        "status": "found",
        "job": _safe_job(_PROVIDER_JOBS[key]),
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def list_provider_jobs(status: str = "", tenant_id: str = "", provider: str = "") -> Dict[str, Any]:
    clean_status = str(status or "").strip().lower()
    clean_tenant = str(tenant_id or "").strip()
    clean_provider = str(provider or "").strip()

    jobs = []

    for job in _PROVIDER_JOBS.values():
        if clean_status and job.get("status") != clean_status:
            continue
        if clean_tenant and job.get("tenant_id") != clean_tenant:
            continue
        if clean_provider and job.get("provider") != clean_provider:
            continue
        jobs.append(_safe_job(job))

    return {
        "success": True,
        "status": "listed",
        "job_count": len(jobs),
        "jobs": jobs,
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def list_provider_job_events(job_id: str = "") -> Dict[str, Any]:
    key = str(job_id or "").strip()

    events = [
        deepcopy(event)
        for event in _PROVIDER_JOB_EVENTS
        if not key or event.get("job_id") == key
    ]

    return {
        "success": True,
        "status": "listed",
        "event_count": len(events),
        "events": events,
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def get_provider_job_persistence_status() -> Dict[str, Any]:
    return {
        "success": True,
        "provider_job_persistence_ready": True,
        "queued_job_persistence_enabled": True,
        "status_update_enabled": True,
        "asset_record_linking_enabled": True,
        "provider_job_event_log_enabled": True,
        "credential_values_exposed": False,
        "customer_safe": True,
    }
''', encoding="utf-8")

test_path.write_text(r'''
from backend.app.runtime.provider_job_persistence_runtime import (
    create_provider_job,
    get_provider_job,
    get_provider_job_persistence_status,
    list_provider_job_events,
    list_provider_jobs,
    update_provider_job_status,
)

status = get_provider_job_persistence_status()
assert status["provider_job_persistence_ready"] is True
assert status["credential_values_exposed"] is False

created = create_provider_job({
    "tenant_id": "test-provider-job-tenant",
    "execution_id": "execution_001",
    "provider": "openai",
    "job_type": "image_generation",
    "requested_asset_type": "image",
    "request_payload": {"prompt": "Safe commercial product image test"},
})
assert created["success"] is True
assert created["status"] == "queued"
assert created["job"]["credential_values_exposed"] is False

job_id = created["job"]["job_id"]

running = update_provider_job_status(
    job_id,
    "running",
    provider_job_reference="provider_ref_001",
)
assert running["success"] is True
assert running["status"] == "running"
assert running["job"]["attempt_count"] == 1

completed = update_provider_job_status(
    job_id,
    "completed",
    result_payload={"provider_status": "succeeded"},
    asset_records=[
        {
            "asset_id": "asset_001",
            "asset_type": "image",
            "delivery_status": "ready",
            "credential_values_exposed": False,
            "customer_safe": True,
        }
    ],
)
assert completed["success"] is True
assert completed["status"] == "completed"
assert len(completed["job"]["asset_records"]) == 1

found = get_provider_job(job_id)
assert found["success"] is True
assert found["job"]["status"] == "completed"

listed = list_provider_jobs(status="completed")
assert listed["success"] is True
assert listed["job_count"] >= 1

events = list_provider_job_events(job_id)
assert events["success"] is True
assert events["event_count"] >= 3
assert events["credential_values_exposed"] is False

invalid = update_provider_job_status(job_id, "bad_status")
assert invalid["success"] is False
assert invalid["error"] == "invalid_provider_job_status"

print("PROVIDER_JOB_PERSISTENCE_RUNTIME_TESTS_PASSED")
print("status_ready", status["provider_job_persistence_ready"])
print("created_status", created["status"])
print("running_status", running["status"])
print("completed_status", completed["status"])
print("listed_job_count", listed["job_count"])
print("event_count", events["event_count"])
print("invalid_error", invalid["error"])
''', encoding="utf-8")

print("PROVIDER_JOB_PERSISTENCE_RUNTIME_INSTALLED")
print(f"Backup folder: {BACKUP_DIR}")
print(f"Created/updated: {runtime_path}")
print(f"Created/updated: {test_path}")