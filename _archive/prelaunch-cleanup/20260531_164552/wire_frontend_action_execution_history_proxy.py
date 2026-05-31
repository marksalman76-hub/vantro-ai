from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()

api_dir = ROOT / "frontend" / "src" / "app" / "api" / "action-execution-history"
api_dir.mkdir(parents=True, exist_ok=True)

target = api_dir / "route.ts"

backup_dir = ROOT / "backups" / f"frontend_action_execution_history_proxy_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)

if target.exists():
    shutil.copy2(target, backup_dir / target.name)

target.write_text(r'''
import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL =
  process.env.BACKEND_API_URL ||
  process.env.NEXT_PUBLIC_BACKEND_API_URL ||
  "https://api.trance-formation.com.au";

const ADMIN_TOKEN =
  process.env.ADMIN_PLATFORM_TOKEN ||
  process.env.ADMIN_AUTH_SECRET ||
  "";

export async function GET(req: NextRequest) {
  const url = new URL(req.url);
  const tenantId = url.searchParams.get("tenant_id") || "";
  const limit = url.searchParams.get("limit") || "50";
  const readiness = url.searchParams.get("readiness") === "true";

  if (!ADMIN_TOKEN) {
    return NextResponse.json(
      { success: false, error: "admin_token_not_configured" },
      { status: 500 }
    );
  }

  const endpoint = readiness
    ? `${BACKEND_URL}/admin/action-execution-history/readiness`
    : `${BACKEND_URL}/admin/action-execution-history?tenant_id=${encodeURIComponent(
        tenantId
      )}&limit=${encodeURIComponent(limit)}`;

  const response = await fetch(endpoint, {
    method: "GET",
    cache: "no-store",
    headers: {
      "Content-Type": "application/json",
      "x-admin-token": ADMIN_TOKEN,
      "x-actor-role": "owner_admin",
      "x-tenant-id": tenantId || "owner_admin",
      "x-csrf-token": "action-execution-history",
      origin:
        process.env.NEXT_PUBLIC_FRONTEND_URL ||
        "https://app.trance-formation.com.au",
    },
  });

  const data = await response.json().catch(() => ({
    success: false,
    error: "backend_response_not_json",
  }));

  return NextResponse.json(
    {
      success: response.ok && data?.success === true,
      backend_status: response.status,
      data,
    },
    { status: response.ok ? 200 : response.status }
  );
}
''', encoding="utf-8")

test_file = ROOT / "test_frontend_action_execution_history_proxy_exists.py"
test_file.write_text(r'''
from pathlib import Path

target = Path("frontend/src/app/api/action-execution-history/route.ts")
assert target.exists()

text = target.read_text(encoding="utf-8")
assert "/admin/action-execution-history" in text
assert "x-admin-token" in text
assert "x-actor-role" in text
assert "owner_admin" in text
assert "readiness" in text

print("FRONTEND_ACTION_EXECUTION_HISTORY_PROXY_EXISTS_TEST_PASSED")
''', encoding="utf-8")

print("FRONTEND_ACTION_EXECUTION_HISTORY_PROXY_WIRED")
print(f"Backup: {backup_dir}")
print(f"Created/updated: {target}")
print(f"Created: {test_file}")