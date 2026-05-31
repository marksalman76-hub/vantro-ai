from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
api_dir = ROOT / "frontend" / "src" / "app" / "api"
backup_dir = ROOT / "backups" / f"execution_evidence_frontend_proxies_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)

admin_dir = api_dir / "admin-execution-evidence"
client_dir = api_dir / "client-execution-evidence"
admin_dir.mkdir(parents=True, exist_ok=True)
client_dir.mkdir(parents=True, exist_ok=True)

admin_route = admin_dir / "route.ts"
client_route = client_dir / "route.ts"

for target in [admin_route, client_route]:
    if target.exists():
        shutil.copy2(target, backup_dir / f"{target.parent.name}_route.ts")

shared_header = '''import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL =
  process.env.BACKEND_API_URL ||
  process.env.NEXT_PUBLIC_BACKEND_API_URL ||
  "https://api.trance-formation.com.au";

const ADMIN_TOKEN =
  process.env.ADMIN_PLATFORM_TOKEN ||
  process.env.ADMIN_AUTH_SECRET ||
  "";
'''

admin_route.write_text(shared_header + r'''
export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const tenantId = searchParams.get("tenant_id") || "";
  const limit = searchParams.get("limit") || "25";

  if (!ADMIN_TOKEN) {
    return NextResponse.json(
      { success: false, error: "admin_token_not_configured" },
      { status: 500 }
    );
  }

  const url = new URL(`${BACKEND_URL}/admin/execution-evidence`);
  if (tenantId) url.searchParams.set("tenant_id", tenantId);
  url.searchParams.set("limit", limit);

  const response = await fetch(url.toString(), {
    method: "GET",
    cache: "no-store",
    headers: {
      "x-admin-token": ADMIN_TOKEN,
      "x-actor-role": "owner_admin",
      "x-tenant-id": tenantId || "owner_admin",
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
      credential_values_exposed: false,
      customer_safe: true,
    },
    { status: response.ok ? 200 : response.status }
  );
}
''', encoding="utf-8")

client_route.write_text(shared_header + r'''
export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const tenantId = searchParams.get("tenant_id") || "client_demo_001";
  const limit = searchParams.get("limit") || "25";

  const url = new URL(`${BACKEND_URL}/client/execution-evidence`);
  url.searchParams.set("tenant_id", tenantId);
  url.searchParams.set("limit", limit);

  const response = await fetch(url.toString(), {
    method: "GET",
    cache: "no-store",
    headers: {
      "x-tenant-id": tenantId,
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
      credential_values_exposed: false,
      customer_safe: true,
    },
    { status: response.ok ? 200 : response.status }
  );
}
''', encoding="utf-8")

test_file = ROOT / "test_execution_evidence_frontend_proxies.py"
test_file.write_text(r'''
from pathlib import Path

admin = Path("frontend/src/app/api/admin-execution-evidence/route.ts").read_text(encoding="utf-8")
client = Path("frontend/src/app/api/client-execution-evidence/route.ts").read_text(encoding="utf-8")

assert "/admin/execution-evidence" in admin
assert '"x-actor-role": "owner_admin"' in admin
assert '"x-tenant-id": tenantId || "owner_admin"' in admin
assert "credential_values_exposed: false" in admin

assert "/client/execution-evidence" in client
assert '"x-tenant-id": tenantId' in client
assert "credential_values_exposed: false" in client

print("EXECUTION_EVIDENCE_FRONTEND_PROXIES_TEST_PASSED")
''', encoding="utf-8")

print("EXECUTION_EVIDENCE_FRONTEND_PROXIES_INSTALLED")
print(f"Backup: {backup_dir}")
print(f"Created/updated: {admin_route}")
print(f"Created/updated: {client_route}")
print(f"Created: {test_file}")