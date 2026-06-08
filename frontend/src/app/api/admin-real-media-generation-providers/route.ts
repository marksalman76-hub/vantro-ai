import { NextRequest, NextResponse } from "next/server";
import {
  selectRealMediaProvider,
  inferMediaCapability,
} from "@/lib/realMediaGenerationProviders";
import { resolveTenantKey } from "@/lib/deliverablePersistence";

export const dynamic = "force-dynamic";

function backendBaseUrl(): string {
  return (
    process.env.BACKEND_API_URL ||
    process.env.BACKEND_BASE_URL ||
    process.env.NEXT_PUBLIC_BACKEND_API_URL ||
    process.env.NEXT_PUBLIC_API_BASE_URL ||
    process.env.NEXT_PUBLIC_BACKEND_BASE_URL ||
    "https://api.trance-formation.com.au"
  ).replace(/\/$/, "");
}

const ADMIN_TOKEN =
  process.env.ADMIN_TOKEN ||
  process.env.ADMIN_PLATFORM_TOKEN ||
  process.env.ADMIN_AUTH_SECRET ||
  process.env.OWNER_ADMIN_TOKEN ||
  "";

// Same safe admin session recognition pattern as working admin media/job routes.
function adminPortalAuthorised(req: NextRequest): boolean {
  const suppliedAdminToken =
    req.headers.get("x-admin-token") || req.headers.get("authorization");
  const expectedPortalAccess = process.env.PORTAL_ACCESS_CODE || "";
  const portalAccess = req.cookies.get("portal_access")?.value || "";
  const adminSession = req.cookies.get("admin_session")?.value || "";
  return Boolean(
    suppliedAdminToken ||
    (expectedPortalAccess && portalAccess === expectedPortalAccess) ||
    (expectedPortalAccess && adminSession === expectedPortalAccess)
  );
}

function safeCookieNames(req: NextRequest): string[] {
  return req.cookies.getAll().map((c) => c.name).filter(Boolean).sort();
}

function unauthorisedResponse(req: NextRequest): NextResponse {
  const cookiesPresent = safeCookieNames(req);
  const expectedPortalAccess = process.env.PORTAL_ACCESS_CODE || "";
  const hasExpectedCookieName =
    cookiesPresent.includes("portal_access") || cookiesPresent.includes("admin_session");
  return NextResponse.json(
    {
      success: false,
      error: "admin_authorisation_required",
      authorised: false,
      credential_values_exposed: false,
      auth_sources_checked: [
        "cookie:portal_access",
        "cookie:admin_session",
        "header:x-admin-token",
        "header:authorization",
      ],
      cookies_present: cookiesPresent,
      reason: !expectedPortalAccess
        ? "portal_access_code_not_configured"
        : hasExpectedCookieName
          ? "admin_session_cookie_present_but_not_valid"
          : "missing_expected_admin_session_cookie",
    },
    { status: 401, headers: { "Cache-Control": "no-store" } }
  );
}

function backendAdminHeaders(): Record<string, string> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    "Cache-Control": "no-store",
    "x-actor-role": "owner_admin",
  };
  if (ADMIN_TOKEN) {
    headers.Authorization = `Bearer ${ADMIN_TOKEN}`;
    headers["x-admin-token"] = ADMIN_TOKEN;
  }
  return headers;
}

export async function GET(req: NextRequest): Promise<NextResponse> {
  if (!adminPortalAuthorised(req)) {
    return unauthorisedResponse(req);
  }

  try {
    const response = await fetch(
      `${backendBaseUrl()}/admin/creative/provider-credential-activation-checks`,
      { method: "GET", cache: "no-store", headers: backendAdminHeaders() }
    );

    const raw = await response.json();
    const data: Record<string, unknown> =
      typeof raw === "object" && raw !== null ? { ...raw } : {};

    // Never forward credential values to the browser regardless of backend response.
    delete data["api_key"];
    delete data["secret"];
    delete data["token"];
    delete data["ELEVENLABS_API_KEY"];
    delete data["RUNWAYML_API_SECRET"];
    delete data["KLING_ACCESS_KEY"];
    delete data["KLING_SECRET_KEY"];
    delete data["HEYGEN_API_KEY"];
    delete data["OPENAI_API_KEY"];

    return NextResponse.json(
      {
        ...data,
        success: response.ok || Boolean(data.success),
        admin_safe: true,
        credential_values_exposed: false,
        real_media_generation_providers_enabled: true,
        provider_queue_retry_failover_enabled: true,
        live_external_call_executed: false,
        external_action_performed: false,
        backend_status: response.status,
      },
      { status: 200, headers: { "cache-control": "no-store, no-cache, must-revalidate" } }
    );
  } catch (error) {
    return NextResponse.json(
      {
        success: false,
        admin_safe: true,
        credential_values_exposed: false,
        real_media_generation_providers_enabled: false,
        live_external_call_executed: false,
        external_action_performed: false,
        safe_error: error instanceof Error ? error.message : String(error),
        backend_status: 0,
        auth_sources_checked: [
          "cookie:portal_access",
          "cookie:admin_session",
          "header:x-admin-token",
          "header:authorization",
        ],
      },
      { status: 502, headers: { "cache-control": "no-store" } }
    );
  }
}

export async function POST(req: NextRequest): Promise<NextResponse> {
  if (!adminPortalAuthorised(req)) {
    return unauthorisedResponse(req);
  }

  let body: Record<string, unknown> = {};
  try {
    body = await req.json();
  } catch {
    body = {};
  }

  const tenantKey = resolveTenantKey(req.headers, body);
  const capability = inferMediaCapability(body);
  const decision = selectRealMediaProvider({
    tenant_key: tenantKey,
    requested_capability: capability,
    prompt: String(body.prompt || body.task || ""),
    asset_type: String(body.asset_type || ""),
    owner_approved: Boolean(body.owner_approved || body.owner_approval_granted),
    dry_run: true,
  });

  return NextResponse.json(
    {
      ...decision,
      success: true,
      admin_safe: true,
      credential_values_exposed: false,
      real_media_generation_providers_enabled: true,
      tenant_key_visible_to_admin: tenantKey,
    },
    { status: 200, headers: { "cache-control": "no-store, no-cache, must-revalidate" } }
  );
}
