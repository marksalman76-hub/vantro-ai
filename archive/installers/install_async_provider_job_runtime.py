from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
RUNTIME_DIR = ROOT / "backend" / "app" / "runtime"
BACKUP_DIR = ROOT / "backups"
RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
BACKUP_DIR.mkdir(exist_ok=True)

target = RUNTIME_DIR / "async_provider_job_runtime.py"

if target.exists():
    backup = BACKUP_DIR / f"async_provider_job_runtime_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
    shutil.copy2(target, backup)
else:
    backup = None

content = r'''"""
Async Provider Job Runtime

Runtime-safe async generation job layer for real provider execution.

This module does not call external providers yet. It creates the governed job
state model required before live provider adapters are activated.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4


JOB_STORE: Dict[str, Dict[str, Any]] = {}


VALID_JOB_STATUSES = {
    "queued",
    "running",
    "polling",
    "completed",
    "failed",
    "cancelled",
    "manual_review_required",
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_async_provider_job(
    *,
    tenant_id: str,
    actor_role: str,
    provider_key: str,
    capability: str,
    request_payload: Optional[Dict[str, Any]] = None,
    owner_approval_required: bool = True,
) -> Dict[str, Any]:
    job_id = f"job_{uuid4().hex}"

    job = {
        "job_id": job_id,
        "tenant_id": tenant_id,
        "actor_role": actor_role,
        "provider_key": provider_key,
        "capability": capability,
        "status": "queued",
        "request_payload": request_payload or {},
        "provider_job_id": None,
        "provider_status": None,
        "asset_delivery_packet": None,
        "retry_count": 0,
        "max_retries": 2,
        "failure_reason": None,
        "owner_approval_required": owner_approval_required,
        "credential_values_exposed": False,
        "customer_safe": True,
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
        "events": [
            {
                "event": "job_created",
                "status": "queued",
                "created_at": _now_iso(),
                "credential_values_exposed": False,
            }
        ],
    }

    JOB_STORE[job_id] = job
    return job


def get_async_provider_job(job_id: str) -> Dict[str, Any]:
    job = JOB_STORE.get(job_id)
    if not job:
        return {
            "found": False,
            "job_id": job_id,
            "error": "job_not_found",
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    return {
        "found": True,
        **job,
    }


def list_async_provider_jobs(
    *,
    tenant_id: Optional[str] = None,
    status: Optional[str] = None,
) -> Dict[str, Any]:
    jobs = list(JOB_STORE.values())

    if tenant_id:
        jobs = [job for job in jobs if job.get("tenant_id") == tenant_id]

    if status:
        jobs = [job for job in jobs if job.get("status") == status]

    return {
        "status": "ok",
        "job_runtime": "async_provider_job_runtime_v1",
        "job_count": len(jobs),
        "jobs": jobs,
        "credential_values_exposed": False,
        "customer_safe": True,
        "checked_at": _now_iso(),
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

    job = JOB_STORE.get(job_id)
    if not job:
        return {
            "updated": False,
            "job_id": job_id,
            "error": "job_not_found",
            "credential_values_exposed": False,
        }

    job["status"] = status
    job["updated_at"] = _now_iso()

    if provider_job_id is not None:
        job["provider_job_id"] = provider_job_id

    if provider_status is not None:
        job["provider_status"] = provider_status

    if failure_reason is not None:
        job["failure_reason"] = failure_reason

    if asset_delivery_packet is not None:
        job["asset_delivery_packet"] = {
            **asset_delivery_packet,
            "signed_delivery": bool(asset_delivery_packet.get("signed_delivery", False)),
            "customer_safe": True,
            "credential_values_exposed": False,
        }

    job["events"].append(
        {
            "event": "job_status_updated",
            "status": status,
            "provider_status": provider_status,
            "updated_at": _now_iso(),
            "credential_values_exposed": False,
        }
    )

    return {
        "updated": True,
        **job,
    }


def mark_async_provider_job_retry(job_id: str, reason: str) -> Dict[str, Any]:
    job = JOB_STORE.get(job_id)
    if not job:
        return {
            "updated": False,
            "job_id": job_id,
            "error": "job_not_found",
            "credential_values_exposed": False,
        }

    if job["retry_count"] >= job["max_retries"]:
        return update_async_provider_job_status(
            job_id=job_id,
            status="manual_review_required",
            failure_reason=f"retry_limit_reached: {reason}",
        )

    job["retry_count"] += 1
    job["status"] = "queued"
    job["failure_reason"] = reason
    job["updated_at"] = _now_iso()
    job["events"].append(
        {
            "event": "job_retry_queued",
            "retry_count": job["retry_count"],
            "reason": reason,
            "updated_at": _now_iso(),
            "credential_values_exposed": False,
        }
    )

    return {
        "updated": True,
        **job,
    }
'''

target.write_text(content, encoding="utf-8")

test = ROOT / "test_async_provider_job_runtime.py"
test.write_text(r'''from backend.app.runtime.async_provider_job_runtime import (
    create_async_provider_job,
    get_async_provider_job,
    list_async_provider_jobs,
    update_async_provider_job_status,
    mark_async_provider_job_retry,
)

job = create_async_provider_job(
    tenant_id="test-tenant",
    actor_role="owner",
    provider_key="openai",
    capability="image_generation",
    request_payload={"prompt": "test"},
)

assert job["status"] == "queued"
assert job["credential_values_exposed"] is False
assert job["customer_safe"] is True
assert job["owner_approval_required"] is True

fetched = get_async_provider_job(job["job_id"])
assert fetched["found"] is True
assert fetched["job_id"] == job["job_id"]

updated = update_async_provider_job_status(
    job_id=job["job_id"],
    status="running",
    provider_job_id="provider-test-001",
    provider_status="submitted",
)
assert updated["updated"] is True
assert updated["status"] == "running"
assert updated["provider_job_id"] == "provider-test-001"

retry = mark_async_provider_job_retry(job["job_id"], "temporary_provider_error")
assert retry["updated"] is True
assert retry["retry_count"] == 1
assert retry["status"] == "queued"

listed = list_async_provider_jobs(tenant_id="test-tenant")
assert listed["job_runtime"] == "async_provider_job_runtime_v1"
assert listed["job_count"] >= 1
assert listed["credential_values_exposed"] is False

print("ASYNC_PROVIDER_JOB_RUNTIME_TEST_PASSED")
print("job_id =", job["job_id"])
print("job_count =", listed["job_count"])
''', encoding="utf-8")

print("ASYNC_PROVIDER_JOB_RUNTIME_INSTALLED")
print(f"Created/updated: {target}")
print(f"Created/updated: {test}")
if backup:
    print(f"Backup: {backup}")
else:
    print("Backup: none needed")