from pathlib import Path
from datetime import datetime

path = Path("frontend/src/app/api/client-business-profile/route.ts")

if not path.exists():
    raise SystemExit("Route file not found. Run this from ecommerce-ai-agent-platform root.")

text = path.read_text(encoding="utf-8")

backup_dir = Path("backups")
backup_dir.mkdir(exist_ok=True)
backup = backup_dir / f"client_business_profile_route_before_session_cookie_{datetime.now().strftime('%Y%m%d_%H%M%S')}.ts"
backup.write_text(text, encoding="utf-8")

replacement = r'''import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL =
  process.env.BACKEND_URL ||
  process.env.NEXT_PUBLIC_BACKEND_URL ||
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  "https://api.trance-formation.com.au";

function getFrontendOrigin(request: NextRequest) {
  return (
    process.env.NEXT_PUBLIC_FRONTEND_URL ||
    process.env.FRONTEND_URL ||
    request.nextUrl.origin ||
    "https://app.trance-formation.com.au"
  );
}

function createClientSessionToken() {
  const randomPart =
    typeof crypto !== "undefined" && "randomUUID" in crypto
      ? crypto.randomUUID()
      : `${Date.now()}-${Math.random().toString(36).slice(2)}`;

  return `client_session_${randomPart}`;
}

function getOrCreateSessionToken(request: NextRequest) {
  const existing = request.cookies.get("client_session")?.value || "";
  return existing || createClientSessionToken();
}

function getTenantId(request: NextRequest, fallbackProfile?: Record<string, unknown>) {
  return (
    request.cookies.get("tenant_id")?.value ||
    request.cookies.get("client_tenant_id")?.value ||
    request.cookies.get("client_id")?.value ||
    String(fallbackProfile?.tenant_id || fallbackProfile?.client_id || "") ||
    "client_workspace"
  );
}

function backendHeaders(request: NextRequest, tenantId: string) {
  const origin = getFrontendOrigin(request);

  return {
    "Content-Type": "application/json",
    "x-tenant-id": tenantId,
    "x-actor-role": "customer",
    Origin: origin,
    Referer: `${origin}/client`,
  };
}

function attachSessionCookie(response: NextResponse, sessionToken: string) {
  response.cookies.set("client_session", sessionToken, {
    httpOnly: true,
    sameSite: "lax",
    secure: true,
    path: "/",
    maxAge: 60 * 60 * 24 * 30,
  });

  return response;
}

export async function GET(request: NextRequest) {
  const sessionToken = getOrCreateSessionToken(request);
  const tenantId = getTenantId(request);

  const response = await fetch(
    `${BACKEND_URL}/client/business-profile?session_token=${encodeURIComponent(sessionToken)}`,
    {
      method: "GET",
      headers: backendHeaders(request, tenantId),
      cache: "no-store",
    }
  );

  const result = await response.json().catch(() => ({
    success: false,
    error: "business_profile_backend_response_not_json",
  }));

  return attachSessionCookie(
    NextResponse.json(result, { status: response.ok ? 200 : response.status }),
    sessionToken
  );
}

export async function POST(request: NextRequest) {
  const body = await request.json().catch(() => ({}));
  const profile = body?.profile && typeof body.profile === "object" ? body.profile : {};

  const sessionToken = getOrCreateSessionToken(request);
  const tenantId = getTenantId(request, profile);

  const response = await fetch(`${BACKEND_URL}/client/business-profile`, {
    method: "POST",
    headers: backendHeaders(request, tenantId),
    body: JSON.stringify({
      session_token: sessionToken,
      tenant_id: tenantId,
      profile,
    }),
    cache: "no-store",
  });

  const result = await response.json().catch(() => ({
    success: false,
    error: "business_profile_backend_response_not_json",
  }));

  return attachSessionCookie(
    NextResponse.json(result, { status: response.ok ? 200 : response.status }),
    sessionToken
  );
}
'''

path.write_text(replacement, encoding="utf-8")

print("CLIENT_BUSINESS_PROFILE_SESSION_COOKIE_FIXED")
print(f"Backup: {backup}")