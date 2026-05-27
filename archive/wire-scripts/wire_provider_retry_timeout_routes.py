from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP_DIR = ROOT / "backups" / f"provider_retry_timeout_routes_before_{STAMP}"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

main_path = ROOT / "backend" / "app" / "main.py"
test_path = ROOT / "test_provider_retry_timeout_routes.py"

backup = BACKUP_DIR / "backend" / "app" / "main.py"
backup.parent.mkdir(parents=True, exist_ok=True)
backup.write_text(main_path.read_text(encoding="utf-8"), encoding="utf-8")

text = main_path.read_text(encoding="utf-8")

import_block = """
from backend.app.runtime.provider_retry_timeout_orchestration import (
    get_provider_retry_timeout_status,
    list_retry_ready_provider_jobs,
    mark_provider_job_timed_out,
    mark_stale_running_jobs_timed_out,
    requeue_retry_ready_provider_jobs,
    schedule_provider_job_retry,
)
"""

route_block = r'''

@app.get("/provider-retry-timeout/status")
async def provider_retry_timeout_status():
    return get_provider_retry_timeout_status()


@app.post("/provider-retry-timeout/schedule-retry")
async def provider_retry_timeout_schedule_retry(request: Request):
    body = await request.json()

    return schedule_provider_job_retry(
        body.get("job_id"),
        reason=body.get("reason", "provider_job_failed"),
        delay_seconds=int(body.get("delay_seconds", 60)),
    )


@app.post("/provider-retry-timeout/mark-timeout")
async def provider_retry_timeout_mark_timeout(request: Request):
    body = await request.json()

    return mark_provider_job_timed_out(
        body.get("job_id"),
        reason=body.get("reason", "provider_job_timed_out"),
    )


@app.get("/provider-retry-timeout/retry-ready")
async def provider_retry_timeout_retry_ready():
    return list_retry_ready_provider_jobs()


@app.post("/provider-retry-timeout/requeue")
async def provider_retry_timeout_requeue(request: Request):
    body = await request.json()

    return requeue_retry_ready_provider_jobs(
        limit=int(body.get("limit", 5)),
    )


@app.post("/provider-retry-timeout/scan-timeouts")
async def provider_retry_timeout_scan_timeouts(request: Request):
    body = await request.json()

    return mark_stale_running_jobs_timed_out(
        timeout_seconds=int(body.get("timeout_seconds", 900)),
    )
'''

if "from backend.app.runtime.provider_retry_timeout_orchestration import" not in text:
    text = import_block + "\n" + text

if "/provider-retry-timeout/status" not in text:
    text = text.rstrip() + "\n\n" + route_block + "\n"

main_path.write_text(text, encoding="utf-8")

test_path.write_text(r'''
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.runtime.provider_job_persistence_runtime import create_provider_job

client = TestClient(app)

status = client.get("/provider-retry-timeout/status")
assert status.status_code == 200
status_json = status.json()
assert status_json["provider_retry_timeout_orchestration_ready"] is True

created = create_provider_job({
    "tenant_id": "retry-route-tenant",
    "provider": "openai",
    "job_type": "image_generation",
    "requested_asset_type": "image",
})

job_id = created["job"]["job_id"]

retry = client.post(
    "/provider-retry-timeout/schedule-retry",
    json={
        "job_id": job_id,
        "reason": "provider_rate_limit",
        "delay_seconds": 1,
    },
)
assert retry.status_code == 200
retry_json = retry.json()
assert retry_json["status"] == "retry_scheduled"

ready = client.get("/provider-retry-timeout/retry-ready")
assert ready.status_code == 200
ready_json = ready.json()
assert ready_json["success"] is True

requeue = client.post(
    "/provider-retry-timeout/requeue",
    json={"limit": 5},
)
assert requeue.status_code == 200
requeue_json = requeue.json()
assert requeue_json["status"] == "requeued"

timeout = client.post(
    "/provider-retry-timeout/mark-timeout",
    json={
        "job_id": job_id,
        "reason": "provider_timeout",
    },
)
assert timeout.status_code == 200
timeout_json = timeout.json()
assert timeout_json["status"] == "timed_out"

scan = client.post(
    "/provider-retry-timeout/scan-timeouts",
    json={"timeout_seconds": 1},
)
assert scan.status_code == 200
scan_json = scan.json()
assert scan_json["status"] == "timeout_scan_completed"

print("PROVIDER_RETRY_TIMEOUT_ROUTES_TESTS_PASSED")
print("status_ready", status_json["provider_retry_timeout_orchestration_ready"])
print("retry_status", retry_json["status"])
print("ready_success", ready_json["success"])
print("requeue_status", requeue_json["status"])
print("timeout_status", timeout_json["status"])
print("scan_status", scan_json["status"])
''', encoding="utf-8")

print("PROVIDER_RETRY_TIMEOUT_ROUTES_WIRED")
print(f"Backup folder: {BACKUP_DIR}")
print(f"Updated: {main_path}")
print(f"Created/updated: {test_path}")