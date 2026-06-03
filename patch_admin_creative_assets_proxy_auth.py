from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP = ROOT / "backups" / f"admin_creative_assets_proxy_auth_before_{STAMP}"

API_FILE = ROOT / "frontend" / "src" / "app" / "api" / "admin-creative-media-assets" / "route.ts"
TEST_FILE = ROOT / "test_admin_creative_assets_proxy_auth.py"

NEW_CONTENT = r'''import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";

const BACKEND_BASE_URL =
  process.env.BACKEND_BASE_URL ||
  process.env.NEXT_PUBLIC_BACKEND_BASE_URL ||
  "https://api.trance-formation.com.au";

const ADMIN_TOKEN =
  process.env.ADMIN_TOKEN ||
  process.env.ADMIN_PLATFORM_TOKEN ||
  process.env.OWNER_ADMIN_TOKEN ||
  "";

export async function GET() {
  try {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
    };

    if (ADMIN_TOKEN) {
      headers.Authorization = `Bearer ${ADMIN_TOKEN}`;
      headers["x-admin-token"] = ADMIN_TOKEN;
    }

    const response = await fetch(`${BACKEND_BASE_URL}/admin/creative/media-assets?limit=50`, {
      method: "GET",
      cache: "no-store",
      headers,
    });

    const data = await response.json();

    return NextResponse.json(data, {
      status: response.status,
      headers: {
        "Cache-Control": "no-store",
      },
    });
  } catch (error) {
    return NextResponse.json(
      {
        success: false,
        layer: "frontend_admin_creative_media_assets_proxy",
        status: "proxy_error",
        error: error instanceof Error ? error.message : String(error),
        credential_values_exposed: false,
      },
      { status: 500 }
    );
  }
}
'''

TEST_CONTENT = r'''from pathlib import Path

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
'''

def main():
    BACKUP.mkdir(parents=True, exist_ok=True)

    if API_FILE.exists():
        dest = BACKUP / API_FILE.relative_to(ROOT)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(API_FILE, dest)

    API_FILE.write_text(NEW_CONTENT, encoding="utf-8", newline="\n")
    TEST_FILE.write_text(TEST_CONTENT, encoding="utf-8", newline="\n")

    print("ADMIN_CREATIVE_ASSETS_PROXY_AUTH_PATCHED")
    print(f"Backup: {BACKUP}")
    print(f"Updated: {API_FILE}")
    print(f"Created: {TEST_FILE}")

if __name__ == "__main__":
    main()