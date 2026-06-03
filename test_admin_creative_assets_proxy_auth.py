from pathlib import Path

api = Path("frontend/src/app/api/admin-creative-media-assets/route.ts")
text = api.read_text(encoding="utf-8", errors="ignore")

for marker in [
    "ADMIN_TOKEN",
    "ADMIN_PLATFORM_TOKEN",
    "OWNER_ADMIN_TOKEN",
    "Authorization",
    "x-admin-token",
    "/admin/creative/media-assets",
    "credential_values_exposed",
]:
    assert marker in text, f"Missing marker: {marker}"

assert ".env.local" not in text, "Frontend proxy must not reference .env.local directly"

print("ADMIN_CREATIVE_ASSETS_PROXY_AUTH_PASSED")
