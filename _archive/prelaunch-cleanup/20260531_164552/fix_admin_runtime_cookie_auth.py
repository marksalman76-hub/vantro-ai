from pathlib import Path
from datetime import datetime
import shutil

root = Path.cwd()
target = root / "frontend" / "src" / "app" / "api" / "admin-runtime" / "route.ts"

backup_dir = root / "backups" / f"admin_runtime_cookie_auth_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)
shutil.copy2(target, backup_dir / "route.ts")

text = target.read_text(encoding="utf-8")

text = text.replace(
    'import { NextResponse } from "next/server";',
    'import { NextRequest, NextResponse } from "next/server";',
)

old_guard = '''function isAdminRequest(req: Request): boolean {
  const expected = process.env.ADMIN_PLATFORM_TOKEN || "";
  if (!expected) return false;

  const auth = req.headers.get("authorization") || "";
  const adminHeader = req.headers.get("x-admin-token") || "";

  return auth === `Bearer ${expected}` || adminHeader === expected;
}'''

new_guard = '''function isAdminRequest(req: NextRequest): boolean {
  const adminToken = process.env.ADMIN_PLATFORM_TOKEN || "";
  const portalAccessCode = process.env.PORTAL_ACCESS_CODE || "";

  const auth = req.headers.get("authorization") || "";
  const adminHeader = req.headers.get("x-admin-token") || "";
  const portalCookie = req.cookies.get("portal_access")?.value || "";

  const tokenAllowed =
    !!adminToken && (auth === `Bearer ${adminToken}` || adminHeader === adminToken);

  const portalCookieAllowed =
    !!portalAccessCode && portalCookie === portalAccessCode;

  return tokenAllowed || portalCookieAllowed;
}'''

if old_guard not in text:
    raise SystemExit("Expected admin guard block not found in admin-runtime route.")

text = text.replace(old_guard, new_guard, 1)

text = text.replace(
    "export async function GET(req: Request) {",
    "export async function GET(req: NextRequest) {",
    1,
)

target.write_text(text, encoding="utf-8")

print("ADMIN_RUNTIME_COOKIE_AUTH_FIXED")
print(f"Backup folder: {backup_dir}")
print(f"Updated: {target}")