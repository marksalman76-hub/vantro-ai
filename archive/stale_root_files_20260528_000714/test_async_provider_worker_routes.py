
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
