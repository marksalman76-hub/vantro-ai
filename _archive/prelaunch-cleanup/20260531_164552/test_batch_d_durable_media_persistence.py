import json
from backend.app.media.durable_media_store import (
    latest_deliverable,
    list_media_assets,
    media_persistence_status,
    persist_deliverable,
    register_media_asset,
)

TENANT = "client_batch_d_media_test"

asset = register_media_asset(
    tenant_id=TENANT,
    url="https://example.com/demo-product-image.png",
    title="Demo product image",
    asset_type="generated_image",
    source="batch_d_test",
    mime_type="image/png",
)

record = persist_deliverable(
    tenant_id=TENANT,
    execution_id="execution_batch_d_test",
    deliverable={
        "title": "Batch D durable media deliverable",
        "summary": "Durable media metadata and deliverable persistence are working.",
        "tags": ["Durable media", "Deliverable persistence", "Launch QA"],
    },
    assets=[asset],
)

latest = latest_deliverable(TENANT)
assets = list_media_assets(TENANT)
status = media_persistence_status()

results = {
    "asset_registered": bool(asset.get("id")),
    "deliverable_persisted": bool(record.get("id")),
    "latest_deliverable_found": bool(latest and latest.get("deliverable")),
    "image_url_bound": latest["deliverable"].get("image_url") == asset["url"],
    "download_url_bound": latest["deliverable"].get("download_url") == asset["url"],
    "asset_count_for_tenant": len(assets),
    "status": status,
}

print("BATCH_D_DURABLE_MEDIA_RESULTS")
print(json.dumps(results, indent=2))

if not all([
    results["asset_registered"],
    results["deliverable_persisted"],
    results["latest_deliverable_found"],
    results["image_url_bound"],
    results["download_url_bound"],
]):
    raise SystemExit("BATCH_D_FAILED")

print("BATCH_D_DURABLE_MEDIA_OK")
