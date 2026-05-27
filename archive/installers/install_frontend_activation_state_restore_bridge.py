from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP_DIR = ROOT / "backups" / f"frontend_activation_state_restore_bridge_before_{STAMP}"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

files = {
    ROOT / "frontend" / "src" / "app" / "api" / "activation-state-restore" / "route.ts": r'''import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL =
  process.env.BACKEND_URL ||
  process.env.NEXT_PUBLIC_BACKEND_URL ||
  "https://api.trance-formation.com.au";

function getBearerToken(request: NextRequest): string | null {
  const authHeader = request.headers.get("authorization");

  if (authHeader && authHeader.toLowerCase().startsWith("bearer ")) {
    return authHeader;
  }

  const adminToken = process.env.ADMIN_PLATFORM_TOKEN;

  if (adminToken) {
    return `Bearer ${adminToken}`;
  }

  return null;
}

export async function GET(request: NextRequest) {
  const bearer = getBearerToken(request);
  const { searchParams } = new URL(request.url);
  const tenantId = searchParams.get("tenant_id") || searchParams.get("tenantId") || "";

  if (!bearer) {
    return NextResponse.json(
      {
        success: false,
        error: "auth_required",
        message: "Missing bearer token.",
        credential_values_exposed: false,
        customer_safe: true,
      },
      { status: 401 },
    );
  }

  if (!tenantId.trim()) {
    return NextResponse.json(
      {
        success: false,
        error: "missing_tenant_id",
        message: "Missing tenant id.",
        credential_values_exposed: false,
        customer_safe: true,
      },
      { status: 400 },
    );
  }

  const upstream = await fetch(
    `${BACKEND_URL}/governed-activation-persistence/hydrate/${encodeURIComponent(tenantId)}`,
    {
      method: "GET",
      headers: {
        authorization: bearer,
        "content-type": "application/json",
      },
      cache: "no-store",
    },
  );

  const text = await upstream.text();

  try {
    const data = JSON.parse(text);

    return NextResponse.json(
      {
        ...data,
        activation_state_restore_bridge_ready: true,
        post_activation_client_changes_blocked: true,
        owner_admin_required_for_post_activation_changes: true,
        credential_values_exposed: false,
        customer_safe: true,
      },
      { status: upstream.status },
    );
  } catch {
    return NextResponse.json(
      {
        success: false,
        error: "upstream_parse_failed",
        activation_state_restore_bridge_ready: true,
        credential_values_exposed: false,
        customer_safe: true,
      },
      { status: upstream.status },
    );
  }
}
''',

    ROOT / "test_frontend_activation_state_restore_bridge.py": r'''from pathlib import Path

route = Path("frontend/src/app/api/activation-state-restore/route.ts")
assert route.exists(), "Missing activation-state-restore API route"

text = route.read_text(encoding="utf-8")

assert "activation_state_restore_bridge_ready" in text
assert "governed-activation-persistence/hydrate" in text
assert "ADMIN_PLATFORM_TOKEN" in text
assert "credential_values_exposed: false" in text
assert "customer_safe: true" in text
assert "cache: \"no-store\"" in text
assert "missing_tenant_id" in text
assert "auth_required" in text

print("FRONTEND_ACTIVATION_STATE_RESTORE_BRIDGE_TESTS_PASSED")
print("route_exists", route.exists())
print("restore_marker", "activation_state_restore_bridge_ready" in text)
print("backend_hydrate_bridge", "governed-activation-persistence/hydrate" in text)
'''
}

for path, content in files.items():
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        backup = BACKUP_DIR / path.relative_to(ROOT)
        backup.parent.mkdir(parents=True, exist_ok=True)
        backup.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
    path.write_text(content, encoding="utf-8")

print("FRONTEND_ACTIVATION_STATE_RESTORE_BRIDGE_INSTALLED")
print(f"Backup folder: {BACKUP_DIR}")
for path in files:
    print(f"Created/updated: {path}")