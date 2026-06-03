from pathlib import Path

ROOT = Path.cwd()
page = ROOT / "frontend" / "src" / "app" / "admin" / "creative-assets" / "page.tsx"
api = ROOT / "frontend" / "src" / "app" / "api" / "admin-creative-media-assets" / "route.ts"

for path in [page, api]:
    if not path.exists():
        raise AssertionError(f"Missing: {path}")

page_text = page.read_text(encoding="utf-8", errors="ignore")
api_text = api.read_text(encoding="utf-8", errors="ignore")

for marker in [
    "Creative Media Assets",
    "Generated audio and video outputs",
    "Refresh assets",
    "Local file path",
    "Back to Admin",
]:
    if marker not in page_text:
        raise AssertionError(f"Missing page marker: {marker}")

for marker in [
    "/admin/creative/media-assets",
    "force-dynamic",
    "no-store",
    "credential_values_exposed",
]:
    if marker not in api_text:
        raise AssertionError(f"Missing API marker: {marker}")

print("ADMIN_CREATIVE_ASSETS_STANDALONE_PAGE_PASSED")
