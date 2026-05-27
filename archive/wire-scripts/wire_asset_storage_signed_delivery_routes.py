from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

main_path = ROOT / "backend" / "app" / "main.py"
test_file = ROOT / "test_asset_storage_signed_delivery_routes_direct.py"

backup_dir = ROOT / "backups" / f"asset_storage_signed_delivery_routes_before_{STAMP}"
backup_dir.mkdir(parents=True, exist_ok=True)

main_text = main_path.read_text(encoding="utf-8")
(backup_dir / "main.py").write_text(main_text, encoding="utf-8")

route_block = r'''

# ---------------------------------------------------------------------------
# Asset storage + signed delivery routes
# Added by wire_asset_storage_signed_delivery_routes.py
# Purpose:
# - expose customer-safe generated asset records, signed previews/downloads,
#   and delivery event records
# - do not expose internal storage keys or credentials
# ---------------------------------------------------------------------------

try:
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
except Exception:  # pragma: no cover
    asset_storage_signed_delivery_status = None
    create_asset_record = None
    create_customer_safe_asset_preview = None
    create_signed_asset_delivery_packet = None
    get_asset_record = None
    list_asset_delivery_events = None
    list_asset_records = None
    reset_asset_storage_for_tests = None
    update_asset_status = None
    verify_signed_asset_delivery_packet = None


@app.get("/asset-storage/status")
def asset_storage_status_route():
    if asset_storage_signed_delivery_status is None:
        return {"status": "unavailable", "credential_values_exposed": False}
    return asset_storage_signed_delivery_status()


@app.post("/asset-storage/create")
async def asset_storage_create_route(payload: dict):
    safe_payload = dict(payload or {})
    return create_asset_record(
        tenant_id=safe_payload.get("tenant_id") or "unknown-tenant",
        request_id=safe_payload.get("request_id") or "unknown-request",
        provider_key=safe_payload.get("provider_key") or "unknown-provider",
        asset_type=safe_payload.get("asset_type") or "generated_asset",
        asset_status=safe_payload.get("asset_status") or "prepared",
        source_url=safe_payload.get("source_url"),
        storage_key=safe_payload.get("storage_key"),
        metadata=safe_payload.get("metadata") or {},
    )


@app.get("/asset-storage/record/{asset_id}")
def asset_storage_get_route(asset_id: str):
    return get_asset_record(asset_id)


@app.get("/asset-storage/list")
def asset_storage_list_route(
    tenant_id: str = "",
    request_id: str = "",
    provider_key: str = "",
    limit: int = 100,
):
    return list_asset_records(
        tenant_id=tenant_id or None,
        request_id=request_id or None,
        provider_key=provider_key or None,
        limit=limit,
    )


@app.post("/asset-storage/update-status/{asset_id}")
async def asset_storage_update_status_route(asset_id: str, payload: dict):
    safe_payload = dict(payload or {})
    return update_asset_status(
        asset_id=asset_id,
        asset_status=safe_payload.get("asset_status") or "prepared",
        metadata=safe_payload.get("metadata") or {},
    )


@app.post("/asset-delivery/signed-packet")
async def asset_delivery_signed_packet_route(payload: dict):
    safe_payload = dict(payload or {})
    return create_signed_asset_delivery_packet(
        tenant_id=safe_payload.get("tenant_id") or "unknown-tenant",
        asset_id=safe_payload.get("asset_id") or "unknown-asset",
        delivery_type=safe_payload.get("delivery_type") or "preview",
        expires_in_seconds=int(safe_payload.get("expires_in_seconds", 3600) or 3600),
    )


@app.post("/asset-delivery/verify")
async def asset_delivery_verify_route(payload: dict):
    safe_payload = dict(payload or {})
    return verify_signed_asset_delivery_packet(
        tenant_id=safe_payload.get("tenant_id") or "unknown-tenant",
        asset_id=safe_payload.get("asset_id") or "unknown-asset",
        delivery_type=safe_payload.get("delivery_type") or "preview",
        expires_at_ms=int(safe_payload.get("expires_at_ms", 0) or 0),
        nonce=safe_payload.get("nonce") or "",
        signature=safe_payload.get("signature") or "",
    )


@app.post("/asset-delivery/customer-preview")
async def asset_delivery_customer_preview_route(payload: dict):
    safe_payload = dict(payload or {})
    return create_customer_safe_asset_preview(
        tenant_id=safe_payload.get("tenant_id") or "unknown-tenant",
        asset_id=safe_payload.get("asset_id") or "unknown-asset",
    )


@app.get("/asset-delivery/events")
def asset_delivery_events_route(
    tenant_id: str = "",
    asset_id: str = "",
    limit: int = 100,
):
    return list_asset_delivery_events(
        tenant_id=tenant_id or None,
        asset_id=asset_id or None,
        limit=limit,
    )


@app.post("/asset-storage/reset-for-tests")
async def asset_storage_reset_for_tests_route():
    return reset_asset_storage_for_tests()
'''

marker = "# Asset storage + signed delivery routes"
if marker in main_text:
    print("ASSET_STORAGE_SIGNED_DELIVERY_ROUTES_ALREADY_PRESENT")
else:
    main_path.write_text(main_text.rstrip() + "\n" + route_block + "\n", encoding="utf-8")
    print("ASSET_STORAGE_SIGNED_DELIVERY_ROUTES_WIRED")

test_file.write_text(r'''
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
'''.lstrip(), encoding="utf-8")

print("ASSET_STORAGE_SIGNED_DELIVERY_ROUTES_INSTALLED")
print(f"Backup folder: {backup_dir}")
print(f"Updated: {main_path}")
print(f"Created/updated: {test_file}")