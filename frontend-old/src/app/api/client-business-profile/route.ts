import { NextRequest, NextResponse } from "next/server";
import { persistBusinessProfile, getBusinessProfile } from "@/lib/businessProfilePersistence";
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

function isProductionRuntime(): boolean {
  return process.env.NODE_ENV === "production";
}

function buildForwardHeaders(req: NextRequest): Record<string, string> {
  const headers: Record<string, string> = {
    "content-type": "application/json",
  };

  const auth = req.headers.get("authorization");
  const adminToken = req.headers.get("x-admin-token");
  const cookie = req.headers.get("cookie");
  const tenantId = req.headers.get("x-tenant-id") || req.cookies.get("tenant_id")?.value;
  const tenantKey = req.headers.get("x-tenant-key") || tenantId;
  const clientToken = req.cookies.get("client_token")?.value;

  if (auth) headers.authorization = auth;
  if (!auth && clientToken) headers.authorization = `Bearer ${clientToken}`;
  if (adminToken) headers["x-admin-token"] = adminToken;
  if (cookie) headers.cookie = cookie;
  if (tenantId) headers["x-tenant-id"] = tenantId;
  if (tenantKey) headers["x-tenant-key"] = tenantKey;

  return headers;
}

function safeBackendProfile(payload: Record<string, unknown>): Record<string, unknown> {
  const profile = (payload.profile || payload.business_profile || {}) as Record<string, unknown>;
  const displayName = String(
    payload.display_name ||
      profile.display_name ||
      profile.business_name ||
      profile.business_niche ||
      "Your business"
  );

  return {
    ...payload,
    success: payload.success !== false,
    business_profile_persisted: Boolean(payload.profile_saved ?? payload.business_profile_persisted ?? payload.success),
    persistence_source: "backend_client_business_profile_route",
    authority: "backend_canonical",
    fallback_used: false,
    dev_only: false,
    production_fail_closed: false,
    profile,
    business_profile: profile,
    display_name: displayName,
    profile_completed: Boolean(payload.profile_completed),
    credential_values_exposed: false,
  };
}

function advisoryProfileResponse(tenantKey: string, status = 200): NextResponse {
  const persisted = getBusinessProfile(tenantKey);

  return NextResponse.json({
    success: true,
    business_profile_persisted: Boolean(persisted),
    persistence_source: "business_profile_store",
    authority: "frontend_advisory",
    fallback_used: true,
    dev_only: true,
    production_fail_closed: false,
    profile: persisted,
    business_profile: persisted,
    display_name: persisted?.display_name || "Your business",
    profile_completed: Boolean(persisted?.profile_completed),
    credential_values_exposed: false,
  }, {
    status,
    headers: { "cache-control": "no-store, no-cache, must-revalidate" },
  });
}

function productionFailClosed(message: string, status = 503): NextResponse {
  return NextResponse.json({
    success: false,
    status: "backend_canonical_unavailable",
    error: message,
    authority: "backend_canonical",
    fallback_used: false,
    dev_only: false,
    production_fail_closed: true,
    business_profile_persisted: false,
    profile: null,
    business_profile: null,
    display_name: "Your business",
    profile_completed: false,
    credential_values_exposed: false,
  }, {
    status,
    headers: { "cache-control": "no-store, no-cache, must-revalidate" },
  });
}

async function readBackendProfile(req: NextRequest, init?: RequestInit): Promise<{ status: number; payload: Record<string, unknown> }> {
  const response = await fetch(`${backendBaseUrl()}/client-business-profile`, {
    method: init?.method || "GET",
    headers: buildForwardHeaders(req),
    body: init?.body,
    cache: "no-store",
  });

  const text = await response.text();
  let payload: Record<string, unknown> = {};
  try {
    payload = text ? JSON.parse(text) : {};
  } catch {
    payload = { backend_response_text: text };
  }

  return { status: response.status, payload };
}

export async function GET(req: NextRequest): Promise<NextResponse> {
  const tenantKey = resolveTenantKey(req.headers, {});

  try {
    const { status, payload } = await readBackendProfile(req);
    if (status < 500 && payload.success !== false) {
      return NextResponse.json(safeBackendProfile(payload), {
        status,
        headers: { "cache-control": "no-store, no-cache, must-revalidate" },
      });
    }

    if (isProductionRuntime()) {
      return productionFailClosed(String(payload.error || payload.status || "backend_profile_unavailable"), status >= 400 ? status : 503);
    }
  } catch (error) {
    if (isProductionRuntime()) {
      return productionFailClosed(error instanceof Error ? error.message : String(error));
    }
  }

  return advisoryProfileResponse(tenantKey);
}

export async function POST(req: NextRequest): Promise<NextResponse> {
  let body: Record<string, unknown> = {};

  try {
    body = await req.json();
  } catch {
    body = {};
  }

  const tenantKey = resolveTenantKey(req.headers, body);

  try {
    const { status, payload } = await readBackendProfile(req, {
      method: "POST",
      body: JSON.stringify(body),
    });

    if (status < 500 && payload.success !== false) {
      const advisory = !isProductionRuntime() ? persistBusinessProfile(tenantKey, body) : null;
      return NextResponse.json({
        ...safeBackendProfile(payload),
        business_profile_saved: true,
        frontend_advisory_profile_cached: Boolean(advisory),
      }, {
        status,
        headers: { "cache-control": "no-store, no-cache, must-revalidate" },
      });
    }

    if (isProductionRuntime()) {
      return productionFailClosed(String(payload.error || payload.status || "backend_profile_save_unavailable"), status >= 400 ? status : 503);
    }
  } catch (error) {
    if (isProductionRuntime()) {
      return productionFailClosed(error instanceof Error ? error.message : String(error));
    }
  }

  const persisted = persistBusinessProfile(tenantKey, body);
  return NextResponse.json({
    success: true,
    business_profile_saved: true,
    business_profile_persisted: true,
    persistence_source: "business_profile_store",
    authority: "frontend_advisory",
    fallback_used: true,
    dev_only: true,
    production_fail_closed: false,
    backend_sync_status: "pending",
    profile: persisted,
    business_profile: persisted,
    display_name: persisted.display_name,
    profile_completed: persisted.profile_completed,
    credential_values_exposed: false,
  }, {
    status: 200,
    headers: { "cache-control": "no-store, no-cache, must-revalidate" },
  });
}
