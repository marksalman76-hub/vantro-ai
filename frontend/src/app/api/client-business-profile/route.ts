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

function buildForwardHeaders(req: NextRequest): Record<string, string> {
  const headers: Record<string, string> = {
    "content-type": "application/json",
  };

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
  const persisted = getBusinessProfile(tenantKey);

  if (persisted) {
    return NextResponse.json({
      success: true,
      business_profile_persisted: true,
      persistence_source: "business_profile_store",
      profile: persisted,
      business_profile: persisted,
      display_name: persisted.display_name,
      profile_completed: persisted.profile_completed,
    }, {
      status: 200,
      headers: { "cache-control": "no-store, no-cache, must-revalidate" },
    });
  }

  try {
    const response = await fetch(`${backendBaseUrl()}/client-business-profile`, {
      method: "GET",
      headers: buildForwardHeaders(req),
      cache: "no-store",
    });

    const text = await response.text();
    let payload: Record<string, unknown> = {};

    try {
      payload = JSON.parse(text);
    } catch {
      payload = { backend_response_text: text };
    }

    return NextResponse.json({
      ...payload,
      business_profile_persisted: false,
      persistence_source: "backend_client_business_profile_route",
    }, {
      status: response.status,
      headers: { "cache-control": "no-store, no-cache, must-revalidate" },
    });
  } catch {
    return NextResponse.json({
      success: true,
      business_profile_persisted: false,
      persistence_source: "empty_profile_fallback",
      profile: null,
      business_profile: null,
      display_name: "Your business",
      profile_completed: false,
    }, {
      status: 200,
      headers: { "cache-control": "no-store, no-cache, must-revalidate" },
    });
  }
}

export async function POST(req: NextRequest): Promise<NextResponse> {
  let body: Record<string, unknown> = {};

  try {
    body = await req.json();
  } catch {
    body = {};
  }

  const tenantKey = resolveTenantKey(req.headers, body);
  const persisted = persistBusinessProfile(tenantKey, body);

  let backendPayload: Record<string, unknown> = {};
  let backendStatus = 200;

  try {
    const response = await fetch(`${backendBaseUrl()}/client-business-profile`, {
      method: "POST",
      headers: buildForwardHeaders(req),
      body: JSON.stringify({
        ...body,
        display_name: persisted.display_name,
        business_name: persisted.business_name,
      }),
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
    backendPayload = { backend_sync_status: "pending" };
  }

  return NextResponse.json({
    ...backendPayload,
    success: true,
    business_profile_saved: true,
    business_profile_persisted: true,
    persistence_source: "business_profile_store",
    profile: persisted,
    business_profile: persisted,
    display_name: persisted.display_name,
    profile_completed: persisted.profile_completed,
  }, {
    status: backendStatus >= 500 ? 200 : backendStatus,
    headers: { "cache-control": "no-store, no-cache, must-revalidate" },
  });
}
