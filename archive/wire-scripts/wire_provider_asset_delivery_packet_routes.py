from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP_DIR = ROOT / "backups" / f"provider_asset_delivery_packet_routes_before_{STAMP}"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

main_path = ROOT / "backend" / "app" / "main.py"
test_path = ROOT / "test_provider_asset_delivery_packet_routes.py"

backup = BACKUP_DIR / "backend" / "app" / "main.py"
backup.parent.mkdir(parents=True, exist_ok=True)
backup.write_text(main_path.read_text(encoding="utf-8"), encoding="utf-8")

text = main_path.read_text(encoding="utf-8")

import_block = """
from backend.app.runtime.provider_asset_delivery_packet_runtime import (
    create_delivery_packet_from_provider_job,
    get_delivery_packet,
    get_provider_asset_delivery_packet_status,
    list_delivery_packets,
)
"""

route_block = r'''

@app.get("/provider-asset-delivery/status")
async def provider_asset_delivery_status():
    return get_provider_asset_delivery_packet_status()


@app.post("/provider-asset-delivery/create")
async def provider_asset_delivery_create(request: Request):
    body = await request.json()
    return create_delivery_packet_from_provider_job(body.get("job_id"))


@app.get("/provider-asset-delivery/packet/{packet_id}")
async def provider_asset_delivery_get(packet_id: str):
    return get_delivery_packet(packet_id)


@app.get("/provider-asset-delivery/packets")
async def provider_asset_delivery_list(tenant_id: str = "", execution_id: str = ""):
    return list_delivery_packets(tenant_id, execution_id)
'''

if "from backend.app.runtime.provider_asset_delivery_packet_runtime import" not in text:
    text = import_block + "\n" + text

if "/provider-asset-delivery/status" not in text:
    text = text.rstrip() + "\n\n" + route_block + "\n"

main_path.write_text(text, encoding="utf-8")

test_path.write_text(r'''
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.runtime.async_provider_worker_runtime import enqueue_async_provider_job, process_provider_job

client = TestClient(app)

status = client.get("/provider-asset-delivery/status")
assert status.status_code == 200
status_json = status.json()
assert status_json["provider_asset_delivery_packet_ready"] is True
assert status_json["credential_values_exposed"] is False

queued = enqueue_async_provider_job({
    "tenant_id": "asset-delivery-route-tenant",
    "execution_id": "asset_delivery_route_execution",
    "provider": "openai",
    "job_type": "image_generation",
    "requested_asset_type": "image",
})

job_id = queued["job"]["job_id"]
completed = process_provider_job(job_id)
assert completed["status"] == "completed"

created = client.post(
    "/provider-asset-delivery/create",
    json={"job_id": job_id},
)
assert created.status_code == 200
created_json = created.json()
assert created_json["success"] is True
assert created_json["status"] == "ready"
assert created_json["credential_values_exposed"] is False

packet_id = created_json["delivery_packet"]["packet_id"]

fetched = client.get(f"/provider-asset-delivery/packet/{packet_id}")
assert fetched.status_code == 200
fetched_json = fetched.json()
assert fetched_json["success"] is True
assert fetched_json["delivery_packet"]["delivery_status"] == "ready"

listed = client.get("/provider-asset-delivery/packets?tenant_id=asset-delivery-route-tenant")
assert listed.status_code == 200
listed_json = listed.json()
assert listed_json["success"] is True
assert listed_json["packet_count"] >= 1

missing = client.post(
    "/provider-asset-delivery/create",
    json={"job_id": "missing_job"},
)
assert missing.status_code == 200
missing_json = missing.json()
assert missing_json["success"] is False
assert missing_json["error"] == "provider_job_not_found"

print("PROVIDER_ASSET_DELIVERY_PACKET_ROUTES_TESTS_PASSED")
print("status_ready", status_json["provider_asset_delivery_packet_ready"])
print("created_status", created_json["status"])
print("fetched_status", fetched_json["status"])
print("listed_packet_count", listed_json["packet_count"])
print("missing_error", missing_json["error"])
''', encoding="utf-8")

print("PROVIDER_ASSET_DELIVERY_PACKET_ROUTES_WIRED")
print(f"Backup folder: {BACKUP_DIR}")
print(f"Updated: {main_path}")
print(f"Created/updated: {test_path}")