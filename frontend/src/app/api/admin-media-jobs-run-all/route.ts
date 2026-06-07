import { NextRequest, NextResponse } from "next/server";

export const dynamic = "force-dynamic";

const BACKEND_BASE_URL =
  process.env.BACKEND_BASE_URL ||
  process.env.NEXT_PUBLIC_BACKEND_BASE_URL ||
  "https://api.trance-formation.com.au";

const ADMIN_TOKEN =
  process.env.ADMIN_TOKEN ||
  process.env.ADMIN_PLATFORM_TOKEN ||
  process.env.ADMIN_AUTH_SECRET ||
  process.env.OWNER_ADMIN_TOKEN ||
  "";

function trustedFrontendOrigin(req: NextRequest): string {
  return (
    req.headers.get("origin") ||
    process.env.FRONTEND_URL ||
    process.env.NEXT_PUBLIC_APP_URL ||
    "https://app.trance-formation.com.au"
  ).replace(/\/$/, "");
}

function adminPortalAuthorised(req: NextRequest): boolean {
  const suppliedAdminToken = req.headers.get("x-admin-token") || req.headers.get("authorization");
  const expectedPortalAccess = process.env.PORTAL_ACCESS_CODE || "";
  const portalAccess = req.cookies.get("portal_access")?.value || "";
  return Boolean(suppliedAdminToken || (expectedPortalAccess && portalAccess === expectedPortalAccess));
}

export async function POST(req: NextRequest) {
  if (!adminPortalAuthorised(req)) {
    return NextResponse.json(
      {
        success: false,
        error: "admin_authorisation_required",
        authorised: false,
        processor_invoked: false,
        processed_job_count: 0,
        final_status_counts: {},
        security_profile: "priority5_security_audit_enforcement_v1",
        credential_values_exposed: false,
      },
      { status: 401, headers: { "Cache-Control": "no-store" } },
    );
  }

  const auth = req.headers.get("authorization");
  const incomingAdminToken = req.headers.get("x-admin-token");
  const cookie = req.headers.get("cookie");
  const origin = trustedFrontendOrigin(req);
  const headers: Record<string, string> = {
    "Cache-Control": "no-store",
    "Content-Type": "application/json",
    "x-actor-role": "owner_admin",
    "x-tenant-id": "owner_admin",
    "origin": origin,
    "referer": req.headers.get("referer") || `${origin}/admin`,
  };
  const adminToken = incomingAdminToken || ADMIN_TOKEN;
  if (auth) headers.Authorization = auth;
  if (!auth && adminToken) headers.Authorization = `Bearer ${adminToken}`;
  if (adminToken) headers["x-admin-token"] = adminToken;
  if (cookie) {
    headers.cookie = cookie;
  }

  const response = await fetch(`${BACKEND_BASE_URL}/admin/media-jobs/run-all`, {
    method: "POST",
    cache: "no-store",
    headers,
  });

  const data = await response.json();
  return NextResponse.json(data, { status: response.status, headers: { "Cache-Control": "no-store" } });
}
