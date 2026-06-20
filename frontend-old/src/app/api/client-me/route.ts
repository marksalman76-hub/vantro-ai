import { NextRequest, NextResponse } from "next/server";
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
  const tenantId = req.headers.get("x-tenant-id") || req.cookies.get("tenant_id")?.value;
  const clientToken = req.cookies.get("client_token")?.value;

  if (auth) headers.authorization = auth;
  if (!auth && clientToken) headers.authorization = `Bearer ${clientToken}`;
  if (adminToken) headers["x-admin-token"] = adminToken;
  if (cookie) headers.cookie = cookie;
  if (tenantId) headers["x-tenant-id"] = tenantId;

  return headers;
}

function isProductionRuntime(): boolean {
  return process.env.NODE_ENV === "production";
}

export async function GET(req: NextRequest): Promise<NextResponse> {
  const tenantKey = resolveTenantKey(req.headers, {});
  const advisoryProfile = getBusinessProfile(tenantKey);

  let backendPayload: Record<string, unknown> = {};
  let profilePayload: Record<string, unknown> = {};
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
      success: !isProductionRuntime(),
      backend_sync_status: "pending",
    };
  }

  try {
    const response = await fetch(`${backendBaseUrl()}/client-business-profile`, {
      method: "GET",
      headers: buildForwardHeaders(req),
      cache: "no-store",
    });
    const text = await response.text();
    try {
      profilePayload = text ? JSON.parse(text) : {};
    } catch {
      profilePayload = { backend_response_text: text };
    }
  } catch {
    profilePayload = {};
  }

  const canonicalProfileAvailable = profilePayload.success !== false && Boolean(profilePayload.profile || profilePayload.business_profile);
  const profile = canonicalProfileAvailable
    ? ((profilePayload.profile || profilePayload.business_profile) as Record<string, unknown>)
    : (!isProductionRuntime() ? advisoryProfile : null);
  const profileAuthority = canonicalProfileAvailable ? "backend_canonical" : (!isProductionRuntime() && advisoryProfile ? "frontend_advisory" : "backend_canonical");

  return NextResponse.json(
    {
      ...backendPayload,
      success: backendPayload.success !== false,
      business_profile_persisted: Boolean(canonicalProfileAvailable || advisoryProfile),
      business_profile: profile,
      profile: profile || backendPayload.profile || null,
      display_name:
        String((profile as Record<string, unknown> | null)?.display_name || (profile as Record<string, unknown> | null)?.business_name || backendPayload.display_name || backendPayload.business_name || "Your business"),
      profile_completed:
        Boolean(profilePayload.profile_completed || (profile as Record<string, unknown> | null)?.profile_completed || backendPayload.profile_completed),
      authority: profileAuthority,
      fallback_used: profileAuthority === "frontend_advisory",
      dev_only: profileAuthority === "frontend_advisory",
      production_fail_closed: isProductionRuntime() && !canonicalProfileAvailable,
      credential_values_exposed: false,
    },
    {
      status: backendStatus >= 500 ? 200 : backendStatus,
      headers: {
        "cache-control": "no-store, no-cache, must-revalidate",
      },
    }
  );
}
