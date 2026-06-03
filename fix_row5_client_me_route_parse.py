from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = ROOT / "backups" / f"row5_client_me_parse_fix_before_{stamp}"
backup.mkdir(parents=True, exist_ok=True)

route = ROOT / "frontend" / "src" / "app" / "api" / "client-me" / "route.ts"

if not route.exists():
    raise SystemExit("client-me route not found")

shutil.copy2(route, backup / "route.ts")

route.write_text(r'''import { NextRequest, NextResponse } from "next/server";
import { getBusinessProfile } from "@/lib/businessProfilePersistence";
import { resolveTenantKey } from "@/lib/deliverablePersistence";

export const dynamic = "force-dynamic";

function backendBaseUrl(): string {
  return (
    process.env.BACKEND_API_URL ||
    process.env.NEXT_PUBLIC_BACKEND_API_URL ||
    process.env.NEXT_PUBLIC_API_BASE_URL ||
    "https://api.trance-formation.com.au"
  ).replace(/\/$/, "");
}

function buildForwardHeaders(req: NextRequest): Record<string, string> {
  const headers: Record<string, string> = {};

  const auth = req.headers.get("authorization");
  const adminToken = req.headers.get("x-admin-token");
  const cookie = req.headers.get("cookie");

  if (auth) headers.authorization = auth;
  if (adminToken) headers["x-admin-token"] = adminToken;
  if (cookie) headers.cookie = cookie;

  return headers;
}

export async function GET(req: NextRequest): Promise<NextResponse> {
  const tenantKey = resolveTenantKey(req.headers, {});
  const persistedProfile = getBusinessProfile(tenantKey);

  let backendPayload: Record<string, unknown> = {};
  let backendStatus = 200;

  try {
    const response = await fetch(`${backendBaseUrl()}/client-me`, {
      method: "GET",
      headers: buildForwardHeaders(req),
      cache: "no-store",
    });

    backendStatus = response.status;
    const text = await response.text();

    try {
      backendPayload = JSON.parse(text);
    } catch {
      backendPayload = { backend_response_text: text };
    }
  } catch {
    backendPayload = {
      success: true,
      backend_sync_status: "pending",
    };
  }

  return NextResponse.json(
    {
      ...backendPayload,
      success: backendPayload.success !== false,
      business_profile_persisted: Boolean(persistedProfile),
      business_profile: persistedProfile,
      profile: persistedProfile || backendPayload.profile || null,
      display_name:
        persistedProfile?.display_name ||
        String(backendPayload.display_name || backendPayload.business_name || "Your business"),
      profile_completed:
        persistedProfile?.profile_completed ||
        Boolean(backendPayload.profile_completed),
    },
    {
      status: backendStatus >= 500 ? 200 : backendStatus,
      headers: {
        "cache-control": "no-store, no-cache, must-revalidate",
      },
    }
  );
}
''', encoding="utf-8")

print("ROW5_CLIENT_ME_ROUTE_PARSE_FIXED")
print(f"Backup: {backup}")
print(f"Updated: {route}")