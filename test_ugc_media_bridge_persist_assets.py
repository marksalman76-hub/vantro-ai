from pathlib import Path
import py_compile

bridge = Path("backend/app/runtime/admin_ugc_live_media_execution_bridge.py")
api = Path("frontend/src/app/api/admin-creative-media-assets/route.ts")

for path in [bridge, api]:
    if not path.exists():
        raise AssertionError(f"Missing file: {path}")

py_compile.compile(str(bridge), doraise=True)

bridge_text = bridge.read_text(encoding="utf-8", errors="ignore")
api_text = api.read_text(encoding="utf-8", errors="ignore")

for marker in [
    "persist_creative_asset",
    "persisted_asset_records",
    "provider_asset_url",
    "download_url",
]:
    if marker not in bridge_text:
        raise AssertionError(f"Missing bridge marker: {marker}")

for marker in [
    "/admin/persisted-creative-assets",
    "x-actor-role",
    "owner_admin",
    "ADMIN_TOKEN",
]:
    if marker not in api_text:
        raise AssertionError(f"Missing frontend API marker: {marker}")

print("UGC_MEDIA_BRIDGE_PERSIST_ASSETS_PASSED")
