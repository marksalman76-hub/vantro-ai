from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP_DIR = ROOT / "backups" / f"async_provider_worker_routes_before_{STAMP}"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

main_path = ROOT / "backend" / "app" / "main.py"
test_path = ROOT / "test_async_provider_worker_routes.py"

backup = BACKUP_DIR / "backend" / "app" / "main.py"
backup.parent.mkdir(parents=True, exist_ok=True)
backup.write_text(main_path.read_text(encoding="utf-8"), encoding="utf-8")

text = main_path.read_text(encoding="utf-8")

import_block = """
from backend.app.runtime.async_provider_worker_runtime import (
    enqueue_async_provider_job,
    get_async_provider_worker_status,
    process_next_queued_provider_job,
    process_provider_job,
    process_provider_job_batch,
)
"""

route_block = r'''

@app.get("/async-provider-worker/status")
async def async_provider_worker_status():
    return get_async_provider_worker_status()


@app.post("/async-provider-worker/enqueue")
async def async_provider_worker_enqueue(request: Request):
    body = await request.json()
    return enqueue_async_provider_job(body)


@app.post("/async-provider-worker/process")
async def async_provider_worker_process(request: Request):
    body = await request.json()

    return process_provider_job(
        body.get("job_id"),
        simulate_success=bool(body.get("simulate_success", True)),
    )


@app.post("/async-provider-worker/process-next")
async def async_provider_worker_process_next(request: Request):
    body = await request.json()

    return process_next_queued_provider_job(
        simulate_success=bool(body.get("simulate_success", True)),
    )


@app.post("/async-provider-worker/process-batch")
async def async_provider_worker_process_batch_route(request: Request):
    body = await request.json()

    return process_provider_job_batch(
        limit=int(body.get("limit", 5)),
        simulate_success=bool(body.get("simulate_success", True)),
    )
'''

if "from backend.app.runtime.async_provider_worker_runtime import" not in text:
    text = import_block + "\n" + text

if "/async-provider-worker/status" not in text:
    text = text.rstrip() + "\n\n" + route_block + "\n"

main_path.write_text(text, encoding="utf-8")

test_path.write_text(r'''
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

status = client.get("/async-provider-worker/status")
assert status.status_code == 200
status_json = status.json()
assert status_json["async_provider_worker_ready"] is True

queued = client.post(
    "/async-provider-worker/enqueue",
    json={
        "tenant_id": "worker-route-tenant",
        "execution_id": "worker_route_execution",
        "provider": "openai",
        "job_type": "image_generation",
        "requested_asset_type": "image",
    },
)
assert queued.status_code == 200
queued_json = queued.json()
assert queued_json["success"] is True

job_id = queued_json["job"]["job_id"]

processed = client.post(
    "/async-provider-worker/process",
    json={
        "job_id": job_id,
        "simulate_success": True,
    },
)
assert processed.status_code == 200
processed_json = processed.json()
assert processed_json["status"] == "completed"

next_job = client.post(
    "/async-provider-worker/enqueue",
    json={
        "tenant_id": "worker-route-tenant",
        "execution_id": "worker_route_execution_next",
        "provider": "openai",
        "job_type": "video_generation",
        "requested_asset_type": "video",
    },
)
assert next_job.status_code == 200

process_next = client.post(
    "/async-provider-worker/process-next",
    json={"simulate_success": True},
)
assert process_next.status_code == 200
process_next_json = process_next.json()
assert process_next_json["status"] == "completed"

batch_seed = client.post(
    "/async-provider-worker/enqueue",
    json={
        "tenant_id": "worker-route-tenant",
        "execution_id": "worker_route_execution_batch",
        "provider": "openai",
        "job_type": "image_generation",
        "requested_asset_type": "image",
    },
)
assert batch_seed.status_code == 200

batch = client.post(
    "/async-provider-worker/process-batch",
    json={
        "limit": 3,
        "simulate_success": True,
    },
)
assert batch.status_code == 200
batch_json = batch.json()
assert batch_json["status"] == "batch_processed"

print("ASYNC_PROVIDER_WORKER_ROUTES_TESTS_PASSED")
print("status_ready", status_json["async_provider_worker_ready"])
print("queued_success", queued_json["success"])
print("processed_status", processed_json["status"])
print("process_next_status", process_next_json["status"])
print("batch_status", batch_json["status"])
''', encoding="utf-8")

print("ASYNC_PROVIDER_WORKER_ROUTES_WIRED")
print(f"Backup folder: {BACKUP_DIR}")
print(f"Updated: {main_path}")
print(f"Created/updated: {test_path}")