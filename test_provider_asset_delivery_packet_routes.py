
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
