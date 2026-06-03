from pathlib import Path

checks = {
    "frontend/src/lib/mediaAssetLifecycle.ts": [
        "persistMediaAssets",
        "getMediaAssets",
        "getLatestMediaAsset",
        "attachMediaAssetLifecycle",
        "media-assets.json",
        "preview_ready",
        "download_ready",
        "expired",
    ],
    "frontend/src/app/api/delegated-workforce-execution/route.ts": [
        "persistMediaAssets",
        "attachMediaAssetLifecycle",
        "media_assets_persisted",
        "media_asset_lifecycle_enabled",
    ],
    "frontend/src/app/api/client-latest-deliverable/route.ts": [
        "attachMediaAssetLifecycle",
        "media_asset_lifecycle_enabled",
    ],
    "frontend/src/app/api/client-media-assets/route.ts": [
        "getMediaAssets",
        "getLatestMediaAsset",
        "asset_lifecycle_status",
        "asset_preview_ready",
        "asset_download_ready",
    ],
}

missing = {}

for file, needles in checks.items():
    text = Path(file).read_text(encoding="utf-8")
    absent = [needle for needle in needles if needle not in text]
    if absent:
        missing[file] = absent

if missing:
    raise SystemExit(f"ROW7_MEDIA_ASSET_LIFECYCLE_FAILED missing={missing}")

print("ROW7_MEDIA_ASSET_LIFECYCLE_PASSED")
