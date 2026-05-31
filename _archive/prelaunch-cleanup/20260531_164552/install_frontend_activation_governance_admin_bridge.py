from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP_DIR = ROOT / "backups" / f"frontend_activation_governance_admin_bridge_before_{STAMP}"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

files = {
    ROOT / "frontend" / "src" / "app" / "api" / "admin-activation-governance" / "status" / "route.ts": r'''import { NextRequest, NextResponse } from "next/server";

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

  const upstream = await fetch(`${BACKEND_URL}/activation-governance-admin-visibility/status`, {
    method: "GET",
    headers: {
      authorization: bearer,
      "content-type": "application/json",
    },
    cache: "no-store",
  });

  const text = await upstream.text();

  try {
    return NextResponse.json(JSON.parse(text), { status: upstream.status });
  } catch {
    return NextResponse.json(
      {
        success: false,
        error: "upstream_parse_failed",
        credential_values_exposed: false,
        customer_safe: true,
      },
      { status: upstream.status },
    );
  }
}
''',

    ROOT / "frontend" / "src" / "app" / "api" / "admin-activation-governance" / "summary" / "route.ts": r'''import { NextRequest, NextResponse } from "next/server";

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
  const tenantId = searchParams.get("tenant_id") || "";

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

  const suffix = tenantId ? `?tenant_id=${encodeURIComponent(tenantId)}` : "";

  const upstream = await fetch(`${BACKEND_URL}/activation-governance-admin-visibility/summary${suffix}`, {
    method: "GET",
    headers: {
      authorization: bearer,
      "content-type": "application/json",
    },
    cache: "no-store",
  });

  const text = await upstream.text();

  try {
    return NextResponse.json(JSON.parse(text), { status: upstream.status });
  } catch {
    return NextResponse.json(
      {
        success: false,
        error: "upstream_parse_failed",
        credential_values_exposed: false,
        customer_safe: true,
      },
      { status: upstream.status },
    );
  }
}
''',

    ROOT / "test_frontend_activation_governance_admin_bridge.py": r'''from pathlib import Path

status_route = Path("frontend/src/app/api/admin-activation-governance/status/route.ts")
summary_route = Path("frontend/src/app/api/admin-activation-governance/summary/route.ts")

assert status_route.exists(), "Missing admin activation governance status route"
assert summary_route.exists(), "Missing admin activation governance summary route"

status_text = status_route.read_text(encoding="utf-8")
summary_text = summary_route.read_text(encoding="utf-8")

assert "activation-governance-admin-visibility/status" in status_text
assert "activation-governance-admin-visibility/summary" in summary_text
assert "ADMIN_PLATFORM_TOKEN" in status_text
assert "ADMIN_PLATFORM_TOKEN" in summary_text
assert "credential_values_exposed: false" in status_text
assert "credential_values_exposed: false" in summary_text
assert "customer_safe: true" in status_text
assert "customer_safe: true" in summary_text
assert "cache: \"no-store\"" in status_text
assert "cache: \"no-store\"" in summary_text

print("FRONTEND_ACTIVATION_GOVERNANCE_ADMIN_BRIDGE_TESTS_PASSED")
print("status_route_exists", status_route.exists())
print("summary_route_exists", summary_route.exists())
print("admin_token_fallback", "ADMIN_PLATFORM_TOKEN" in status_text and "ADMIN_PLATFORM_TOKEN" in summary_text)
'''
}

for path, content in files.items():
    path.parent.mkdir(parents=True, exist_ok=True)

    if path.exists():
        backup = BACKUP_DIR / path.relative_to(ROOT)
        backup.parent.mkdir(parents=True, exist_ok=True)
        backup.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")

    path.write_text(content, encoding="utf-8")

print("FRONTEND_ACTIVATION_GOVERNANCE_ADMIN_BRIDGE_INSTALLED")
print(f"Backup folder: {BACKUP_DIR}")
for path in files:
    print(f"Created/updated: {path}")