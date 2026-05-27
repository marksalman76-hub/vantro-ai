from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP_DIR = ROOT / "backups" / f"provider_execution_admin_visibility_before_{STAMP}"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

runtime_path = ROOT / "backend" / "app" / "runtime" / "provider_execution_admin_visibility.py"
test_path = ROOT / "test_provider_execution_admin_visibility.py"

for path in [runtime_path, test_path]:
    if path.exists():
        backup = BACKUP_DIR / path.relative_to(ROOT)
        backup.parent.mkdir(parents=True, exist_ok=True)
        backup.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")

runtime_path.parent.mkdir(parents=True, exist_ok=True)

runtime_path.write_text(r'''
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
''', encoding="utf-8")

test_path.write_text(r'''
from backend.app.runtime.async_provider_worker_runtime import enqueue_async_provider_job, process_provider_job
from backend.app.runtime.provider_asset_delivery_packet_runtime import create_delivery_packet_from_provider_job
from backend.app.runtime.provider_execution_admin_visibility import (
    get_provider_execution_admin_visibility,
    get_provider_execution_admin_visibility_status,
)
from backend.app.runtime.provider_job_persistence_runtime import create_provider_job, update_provider_job_status
from backend.app.runtime.provider_retry_timeout_orchestration import schedule_provider_job_retry

tenant_id = "provider-execution-admin-visibility-test-tenant"

status = get_provider_execution_admin_visibility_status()
assert status["provider_execution_admin_visibility_ready"] is True
assert status["credential_values_exposed"] is False

queued = create_provider_job({
    "tenant_id": tenant_id,
    "provider": "openai",
    "job_type": "image_generation",
    "requested_asset_type": "image",
})
assert queued["success"] is True

running_job = create_provider_job({
    "tenant_id": tenant_id,
    "provider": "openai",
    "job_type": "video_generation",
    "requested_asset_type": "video",
})
update_provider_job_status(running_job["job"]["job_id"], "running")

failed_job = create_provider_job({
    "tenant_id": tenant_id,
    "provider": "openai",
    "job_type": "image_generation",
    "requested_asset_type": "image",
})
update_provider_job_status(failed_job["job"]["job_id"], "failed", error="provider_failed")

retry_job = create_provider_job({
    "tenant_id": tenant_id,
    "provider": "openai",
    "job_type": "image_generation",
    "requested_asset_type": "image",
})
schedule_provider_job_retry(retry_job["job"]["job_id"], reason="provider_rate_limited", delay_seconds=60)

worker_job = enqueue_async_provider_job({
    "tenant_id": tenant_id,
    "execution_id": "visibility_execution_001",
    "provider": "openai",
    "job_type": "image_generation",
    "requested_asset_type": "image",
})
completed = process_provider_job(worker_job["job"]["job_id"])
assert completed["status"] == "completed"

packet = create_delivery_packet_from_provider_job(worker_job["job"]["job_id"])
assert packet["success"] is True

visibility = get_provider_execution_admin_visibility(tenant_id=tenant_id)
assert visibility["success"] is True
assert visibility["provider_execution_admin_visibility_ready"] is True
assert visibility["summary"]["queued_job_count"] >= 1
assert visibility["summary"]["running_job_count"] >= 1
assert visibility["summary"]["completed_job_count"] >= 1
assert visibility["summary"]["failed_job_count"] >= 1
assert visibility["summary"]["retry_scheduled_job_count"] >= 1
assert visibility["summary"]["delivery_packet_count"] >= 1
assert visibility["credential_values_exposed"] is False

print("PROVIDER_EXECUTION_ADMIN_VISIBILITY_TESTS_PASSED")
print("status_ready", status["provider_execution_admin_visibility_ready"])
print("queued_jobs", visibility["summary"]["queued_job_count"])
print("running_jobs", visibility["summary"]["running_job_count"])
print("completed_jobs", visibility["summary"]["completed_job_count"])
print("failed_jobs", visibility["summary"]["failed_job_count"])
print("retry_scheduled", visibility["summary"]["retry_scheduled_job_count"])
print("delivery_packets", visibility["summary"]["delivery_packet_count"])
''', encoding="utf-8")

print("PROVIDER_EXECUTION_ADMIN_VISIBILITY_INSTALLED")
print(f"Backup folder: {BACKUP_DIR}")
print(f"Created/updated: {runtime_path}")
print(f"Created/updated: {test_path}")