from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP_DIR = ROOT / "backups" / f"provider_job_persistence_routes_before_{STAMP}"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

main_path = ROOT / "backend" / "app" / "main.py"
test_path = ROOT / "test_provider_job_persistence_routes.py"

backup = BACKUP_DIR / "backend" / "app" / "main.py"
backup.parent.mkdir(parents=True, exist_ok=True)
backup.write_text(main_path.read_text(encoding="utf-8"), encoding="utf-8")

text = main_path.read_text(encoding="utf-8")

import_block = """
from backend.app.runtime.provider_job_persistence_runtime import (
    create_provider_job,
    get_provider_job,
    get_provider_job_persistence_status,
    list_provider_job_events,
    list_provider_jobs,
    update_provider_job_status,
)
"""

route_block = r'''

@app.get("/provider-job-persistence/status")
async def provider_job_persistence_status():
    return get_provider_job_persistence_status()


@app.post("/provider-job-persistence/create")
async def provider_job_persistence_create(request: Request):
    body = await request.json()
    return create_provider_job(body)


@app.post("/provider-job-persistence/update")
async def provider_job_persistence_update(request: Request):
    body = await request.json()

    return update_provider_job_status(
        body.get("job_id"),
        body.get("status"),
        result_payload=body.get("result_payload"),
        error=body.get("error"),
        provider_job_reference=body.get("provider_job_reference"),
        asset_records=body.get("asset_records"),
        next_retry_at=body.get("next_retry_at"),
    )


@app.get("/provider-job-persistence/job/{job_id}")
async def provider_job_persistence_get(job_id: str):
    return get_provider_job(job_id)


@app.get("/provider-job-persistence/jobs")
async def provider_job_persistence_list(
    status: str = "",
    tenant_id: str = "",
    provider: str = "",
):
    return list_provider_jobs(status, tenant_id, provider)


@app.get("/provider-job-persistence/events")
async def provider_job_persistence_events(job_id: str = ""):
    return list_provider_job_events(job_id)
'''

if "from backend.app.runtime.provider_job_persistence_runtime import" not in text:
    text = import_block + "\n" + text

if "/provider-job-persistence/status" not in text:
    text = text.rstrip() + "\n\n" + route_block + "\n"

main_path.write_text(text, encoding="utf-8")

test_path.write_text(r'''
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

status = client.get("/provider-job-persistence/status")
assert status.status_code == 200
status_json = status.json()
assert status_json["provider_job_persistence_ready"] is True

created = client.post(
    "/provider-job-persistence/create",
    json={
        "tenant_id": "route-test-tenant",
        "provider": "openai",
        "job_type": "image_generation",
        "requested_asset_type": "image",
    },
)
assert created.status_code == 200
created_json = created.json()
assert created_json["success"] is True

job_id = created_json["job"]["job_id"]

updated = client.post(
    "/provider-job-persistence/update",
    json={
        "job_id": job_id,
        "status": "completed",
        "result_payload": {"provider_status": "done"},
    },
)
assert updated.status_code == 200
updated_json = updated.json()
assert updated_json["status"] == "completed"

fetched = client.get(f"/provider-job-persistence/job/{job_id}")
assert fetched.status_code == 200
fetched_json = fetched.json()
assert fetched_json["job"]["status"] == "completed"

listed = client.get("/provider-job-persistence/jobs?status=completed")
assert listed.status_code == 200
listed_json = listed.json()
assert listed_json["job_count"] >= 1

events = client.get(f"/provider-job-persistence/events?job_id={job_id}")
assert events.status_code == 200
events_json = events.json()
assert events_json["event_count"] >= 2

print("PROVIDER_JOB_PERSISTENCE_ROUTES_TESTS_PASSED")
print("status_ready", status_json["provider_job_persistence_ready"])
print("created_success", created_json["success"])
print("updated_status", updated_json["status"])
print("listed_job_count", listed_json["job_count"])
print("event_count", events_json["event_count"])
''', encoding="utf-8")

print("PROVIDER_JOB_PERSISTENCE_ROUTES_WIRED")
print(f"Backup folder: {BACKUP_DIR}")
print(f"Updated: {main_path}")
print(f"Created/updated: {test_path}")