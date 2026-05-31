from backend.app.runtime.asset_storage_signed_delivery_runtime import (
    asset_storage_signed_delivery_status,
    create_asset_record,
    create_customer_safe_asset_preview,
    create_signed_asset_delivery_packet,
    get_asset_record,
    list_asset_delivery_events,
    list_asset_records,
    reset_asset_storage_for_tests,
    update_asset_status,
    verify_signed_asset_delivery_packet,
)

reset = reset_asset_storage_for_tests()
assert reset["reset"] is True

status = asset_storage_signed_delivery_status()
assert status["asset_storage_runtime_ready"] is True
assert status["signed_delivery_ready"] is True

asset = create_asset_record(
    tenant_id="tenant-test",
    request_id="request-test",
    provider_key="openai",
    asset_type="image",
    asset_status="prepared",
    source_url="https://example.com/internal-source.png",
    metadata={"safe": True, "api_key": "must-not-store"},
)
assert asset["source_url_present"] is True
assert "api_key" not in asset["metadata"]
assert asset["credential_values_exposed"] is False

fetched = get_asset_record(asset["asset_id"])
assert fetched["asset_id"] == asset["asset_id"]

updated = update_asset_status(
    asset_id=asset["asset_id"],
    asset_status="ready",
    metadata={"quality_score": 95, "secret": "must-not-store"},
)
assert updated["asset_status"] == "ready"
assert "secret" not in updated["metadata"]

packet = create_signed_asset_delivery_packet(
    tenant_id="tenant-test",
    asset_id=asset["asset_id"],
    delivery_type="preview",
    expires_in_seconds=3600,
)
assert packet["status"] == "ready"
assert packet["signed_delivery_token_present"] is True
assert packet["credential_values_exposed"] is False

verified = verify_signed_asset_delivery_packet(
    tenant_id="tenant-test",
    asset_id=asset["asset_id"],
    delivery_type="preview",
    expires_at_ms=packet["expires_at_ms"],
    nonce=packet["nonce"],
    signature=packet["signature"],
)
assert verified["valid"] is True

wrong_tenant = create_signed_asset_delivery_packet(
    tenant_id="wrong-tenant",
    asset_id=asset["asset_id"],
    delivery_type="preview",
)
assert wrong_tenant["status"] == "blocked"
assert wrong_tenant["reason"] == "tenant_asset_mismatch"

preview = create_customer_safe_asset_preview(
    tenant_id="tenant-test",
    asset_id=asset["asset_id"],
)
assert preview["status"] == "ready"
assert preview["internal_storage_key_exposed"] is False
assert preview["customer_safe"] is True

listed = list_asset_records(tenant_id="tenant-test")
assert listed["count"] == 1

events = list_asset_delivery_events(tenant_id="tenant-test")
assert events["count"] >= 2

final = asset_storage_signed_delivery_status()
assert final["asset_count"] == 1
assert final["delivery_event_count"] >= 2

print("ASSET_STORAGE_SIGNED_DELIVERY_RUNTIME_DIRECT_TESTS_PASSED")
print("asset_id", asset["asset_id"])
print("asset_status", updated["asset_status"])
print("packet_status", packet["status"])
print("verified", verified["valid"])
print("preview_status", preview["status"])
print("asset_count", final["asset_count"])
print("delivery_events", final["delivery_event_count"])
