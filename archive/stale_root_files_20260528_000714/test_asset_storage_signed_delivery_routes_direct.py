from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

reset = client.post("/asset-storage/reset-for-tests").json()
assert reset["reset"] is True

status = client.get("/asset-storage/status").json()
assert status["asset_storage_runtime_ready"] is True

asset = client.post(
    "/asset-storage/create",
    json={
        "tenant_id": "tenant-test",
        "request_id": "request-test",
        "provider_key": "openai",
        "asset_type": "image",
        "asset_status": "prepared",
        "source_url": "https://example.com/internal-source.png",
        "metadata": {"safe": True, "api_key": "must-not-store"},
    },
).json()
assert asset["source_url_present"] is True
assert "api_key" not in asset["metadata"]

updated = client.post(
    f"/asset-storage/update-status/{asset['asset_id']}",
    json={"asset_status": "ready", "metadata": {"quality_score": 95}},
).json()
assert updated["asset_status"] == "ready"

packet = client.post(
    "/asset-delivery/signed-packet",
    json={
        "tenant_id": "tenant-test",
        "asset_id": asset["asset_id"],
        "delivery_type": "preview",
    },
).json()
assert packet["status"] == "ready"

verified = client.post(
    "/asset-delivery/verify",
    json={
        "tenant_id": "tenant-test",
        "asset_id": asset["asset_id"],
        "delivery_type": "preview",
        "expires_at_ms": packet["expires_at_ms"],
        "nonce": packet["nonce"],
        "signature": packet["signature"],
    },
).json()
assert verified["valid"] is True

preview = client.post(
    "/asset-delivery/customer-preview",
    json={"tenant_id": "tenant-test", "asset_id": asset["asset_id"]},
).json()
assert preview["status"] == "ready"
assert preview["internal_storage_key_exposed"] is False

events = client.get("/asset-delivery/events?tenant_id=tenant-test").json()
assert events["count"] >= 2

print("ASSET_STORAGE_SIGNED_DELIVERY_ROUTES_DIRECT_TESTS_PASSED")
print("asset_id", asset["asset_id"])
print("asset_status", updated["asset_status"])
print("packet_status", packet["status"])
print("verified", verified["valid"])
print("preview", preview["status"])
print("events", events["count"])
