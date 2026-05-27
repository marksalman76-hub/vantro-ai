
from backend.app.runtime.async_provider_worker_runtime import enqueue_async_provider_job, process_provider_job
from backend.app.runtime.provider_asset_delivery_packet_runtime import (
    create_delivery_packet_from_provider_job,
    get_delivery_packet,
    get_provider_asset_delivery_packet_status,
    list_delivery_packets,
)
from backend.app.runtime.provider_job_persistence_runtime import create_provider_job

status = get_provider_asset_delivery_packet_status()
assert status["provider_asset_delivery_packet_ready"] is True
assert status["credential_values_exposed"] is False

queued = enqueue_async_provider_job({
    "tenant_id": "delivery-packet-test-tenant",
    "execution_id": "delivery_execution_001",
    "provider": "openai",
    "job_type": "image_generation",
    "requested_asset_type": "image",
})

job_id = queued["job"]["job_id"]
completed = process_provider_job(job_id)
assert completed["status"] == "completed"

packet = create_delivery_packet_from_provider_job(job_id)
assert packet["success"] is True
assert packet["status"] == "ready"
assert packet["delivery_packet"]["job_id"] == job_id
assert packet["delivery_packet"]["execution_id"] == "delivery_execution_001"
assert packet["delivery_packet"]["asset_count"] == 1
assert packet["credential_values_exposed"] is False

packet_id = packet["delivery_packet"]["packet_id"]

found = get_delivery_packet(packet_id)
assert found["success"] is True
assert found["delivery_packet"]["delivery_status"] == "ready"

listed = list_delivery_packets(tenant_id="delivery-packet-test-tenant")
assert listed["success"] is True
assert listed["packet_count"] >= 1

incomplete = create_provider_job({
    "tenant_id": "delivery-packet-test-tenant",
    "execution_id": "delivery_execution_002",
    "provider": "openai",
    "job_type": "image_generation",
    "requested_asset_type": "image",
})

blocked = create_delivery_packet_from_provider_job(incomplete["job"]["job_id"])
assert blocked["success"] is False
assert blocked["error"] == "provider_job_not_completed"

missing = create_delivery_packet_from_provider_job("missing_job")
assert missing["success"] is False
assert missing["error"] == "provider_job_not_found"

print("PROVIDER_ASSET_DELIVERY_PACKET_RUNTIME_TESTS_PASSED")
print("status_ready", status["provider_asset_delivery_packet_ready"])
print("packet_status", packet["status"])
print("found_status", found["status"])
print("listed_packet_count", listed["packet_count"])
print("blocked_error", blocked["error"])
print("missing_error", missing["error"])
