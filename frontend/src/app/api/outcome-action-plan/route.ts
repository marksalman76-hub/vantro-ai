import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL =
  process.env.BACKEND_API_URL ||
  process.env.NEXT_PUBLIC_BACKEND_API_URL ||
  "https://api.trance-formation.com.au";

const ADMIN_TOKEN =
  process.env.ADMIN_PLATFORM_TOKEN ||
  process.env.ADMIN_AUTH_SECRET ||
  process.env.ADMIN_AUTH_TOKEN ||
  process.env.ADMIN_BEARER_TOKEN ||
  process.env.OWNER_ADMIN_TOKEN ||
  "";

function authSourcesChecked() {
  return [
    "cookie:portal_access",
    "cookie:admin_session",
    "header:x-admin-token",
    "header:authorization",
  ];
}

function cookiesPresent(req: NextRequest): string[] {
  return req.cookies.getAll().map((cookie) => cookie.name).filter(Boolean).sort();
}

function adminPortalAuthorised(req: NextRequest): boolean {
  const suppliedAdminToken = req.headers.get("x-admin-token") || req.headers.get("authorization");
  const expectedPortalAccess = process.env.PORTAL_ACCESS_CODE || "";
  const portalAccess = req.cookies.get("portal_access")?.value || "";
  const adminSession = req.cookies.get("admin_session")?.value || "";
  return Boolean(
    suppliedAdminToken ||
    (expectedPortalAccess && portalAccess === expectedPortalAccess) ||
    (expectedPortalAccess && adminSession === expectedPortalAccess)
  );
}

export async function POST(req: NextRequest) {
  const body = await req.json().catch(() => ({}));
  const authorised = adminPortalAuthorised(req);

  if (!authorised) {
    return NextResponse.json(
      {
        success: false,
        route_called: true,
        error_code: "admin_authorisation_required",
        auth_sources_checked: authSourcesChecked(),
        cookies_present: cookiesPresent(req),
        backend_status: null,
        backend_error_code: null,
        missing_fields: [],
        safe_error: "Admin session is required to create an outcome action plan.",
        customer_safe: true,
        credential_values_exposed: false,
      },
      { status: 403 }
    );
  }

  if (!ADMIN_TOKEN) {
    return NextResponse.json(
      {
        success: false,
        route_called: true,
        error_code: "admin_token_not_configured",
        auth_sources_checked: authSourcesChecked(),
        cookies_present: cookiesPresent(req),
        backend_status: null,
        backend_error_code: null,
        missing_fields: ["server_admin_token"],
        safe_error: "Admin token is not configured for outcome action planning.",
        customer_safe: true,
        credential_values_exposed: false,
      },
      { status: 500 }
    );
  }

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    Authorization: `Bearer ${ADMIN_TOKEN}`,
    "x-admin-token": ADMIN_TOKEN,
    "x-actor-role": "owner_admin",
    "x-tenant-id": "owner_admin",
    "x-csrf-token": "outcome-action-plan",
    origin: process.env.NEXT_PUBLIC_FRONTEND_URL || "https://app.trance-formation.com.au",
    referer: `${process.env.NEXT_PUBLIC_FRONTEND_URL || "https://app.trance-formation.com.au"}/admin`,
  };
  const cookie = req.headers.get("cookie");
  if (cookie) headers.cookie = cookie;

  const response = await fetch(`${BACKEND_URL}/admin/outcome-action-plan`, {
    method: "POST",
    cache: "no-store",
    headers,
    body: JSON.stringify({
      outcome_text: body.outcome_text || "",
      source_agent: body.source_agent || "unknown_agent",
      tenant_id: body.tenant_id || "owner_admin",
      project_id: body.project_id || "admin_outcome_action_plan",
      owner_approved: body.owner_approved === true,
      source_media_job_id: body.source_media_job_id || body.media_job_id || null,
    }),
  });

  const data = await response.json().catch(() => ({
    success: false,
    error: "backend_response_not_json",
  }));

  return NextResponse.json(
    {
      success: response.ok && data?.success === true,
      route_called: true,
      backend_status: response.status,
      backend_error_code: data?.error || data?.error_code || null,
      auth_sources_checked: authSourcesChecked(),
      cookies_present: cookiesPresent(req),
      missing_fields: [],
      safe_error: response.ok ? "" : "Outcome action plan backend rejected the request.",
      customer_safe: true,
      credential_values_exposed: false,
      data,
    },
    { status: response.ok ? 200 : response.status }
  );
}

export async function GET() {
  return NextResponse.json({
    success: true,
    route: "outcome-action-plan",
    methods: ["POST"],
    status: "ready",
  });
}
