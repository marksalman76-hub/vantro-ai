import { NextRequest, NextResponse } from "next/server";

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

export async function GET(request: NextRequest) {
  const sessionToken = request.cookies.get("client_session")?.value || "";

  if (!sessionToken) {
    return NextResponse.json(
      { success: false, error: "client_session_required" },
      { status: 401 }
    );
  }

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

  return NextResponse.json(result, { status: response.ok ? 200 : response.status });
}

export async function POST(request: NextRequest) {
  const sessionToken = request.cookies.get("client_session")?.value || "";

  if (!sessionToken) {
    return NextResponse.json(
      { success: false, error: "client_session_required" },
      { status: 401 }
    );
  }

  const body = await request.json().catch(() => ({}));
  const profile = body?.profile && typeof body.profile === "object" ? body.profile : {};
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

  return NextResponse.json(result, { status: response.ok ? 200 : response.status });
}
