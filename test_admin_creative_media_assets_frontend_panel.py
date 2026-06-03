from pathlib import Path
import re

ROOT = Path.cwd()

admin_page = ROOT / "frontend" / "src" / "app" / "admin" / "page.tsx"
api_route = ROOT / "frontend" / "src" / "app" / "api" / "admin-creative-media-assets" / "route.ts"

for path in [admin_page, api_route]:
    if not path.exists():
        raise AssertionError(f"Missing required file: {path}")

admin_text = admin_page.read_text(encoding="utf-8", errors="ignore")
api_text = api_route.read_text(encoding="utf-8", errors="ignore")

required_admin_markers = [
    "Creative Media Assets",
    "admin-creative-media-assets",
    "preview_ready",
    "download_ready",
    "asset_type",
    "provider",
    "local_path",
]

for marker in required_admin_markers:
    if marker not in admin_text:
        raise AssertionError(f"Missing admin marker: {marker}")

required_api_markers = [
    "/admin/creative/media-assets",
    "force-dynamic",
    "no-store",
    "credential_values_exposed",
]

for marker in required_api_markers:
    if marker not in api_text:
        raise AssertionError(f"Missing API marker: {marker}")

if ".env.local" in api_text:
    raise AssertionError("Frontend API route must not reference .env.local")

print("ADMIN_CREATIVE_MEDIA_ASSETS_FRONTEND_PANEL_PASSED")
