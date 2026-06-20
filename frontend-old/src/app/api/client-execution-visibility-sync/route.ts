import { NextRequest, NextResponse } from "next/server";
import { resolveTenantKey } from "@/lib/deliverablePersistence";
import { buildAdminClientExecutionVisibilityPacket } from "@/lib/adminClientExecutionVisibilitySync";

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

function forwardHeaders(req: NextRequest, tenantKey: string): Record<string, string> {
  const headers: Record<string, string> = {
    "x-tenant-id": req.headers.get("x-tenant-id") || req.cookies.get("tenant_id")?.value || tenantKey,
    "x-tenant-key": tenantKey,
  };
  const auth = req.headers.get("authorization");
  const cookie = req.headers.get("cookie");
  const clientToken = req.cookies.get("client_token")?.value;
  if (auth) headers.authorization = auth;
  if (!auth && clientToken) headers.authorization = `Bearer ${clientToken}`;
  if (cookie) headers.cookie = cookie;
  return headers;
}

export async function GET(req: NextRequest): Promise<NextResponse> {
  const tenantKey = resolveTenantKey(req.headers, {});

  try {
    const response = await fetch(`${backendBaseUrl()}/client-execution-state?tenant_id=${encodeURIComponent(tenantKey)}`, {
      method: "GET",
      headers: forwardHeaders(req, tenantKey),
      cache: "no-store",
    });
    const payload = await response.json().catch(() => ({ success: false, error: "invalid_backend_response" }));

    if (response.status < 500 && payload.success !== false) {
      return NextResponse.json({
        ...payload,
        admin_client_execution_visibility_sync_enabled: true,
        visibility_mode: "client",
        tenant_scoped: true,
        client_safe: true,
        authority: "backend_canonical",
        fallback_used: false,
        dev_only: false,
        production_fail_closed: false,
        credential_values_exposed: false,
      }, {
        status: response.status,
        headers: { "cache-control": "no-store, no-cache, must-revalidate" },
      });
    }

    if (isProductionRuntime()) {
      return NextResponse.json({
        success: false,
        status: "backend_canonical_unavailable",
        error: payload.error || payload.status || "backend_execution_state_unavailable",
        authority: "backend_canonical",
        fallback_used: false,
        dev_only: false,
        production_fail_closed: true,
        credential_values_exposed: false,
      }, {
        status: response.status >= 400 ? response.status : 503,
        headers: { "cache-control": "no-store, no-cache, must-revalidate" },
      });
    }
  } catch (error) {
    if (isProductionRuntime()) {
      return NextResponse.json({
        success: false,
        status: "backend_canonical_unavailable",
        error: error instanceof Error ? error.message : String(error),
        authority: "backend_canonical",
        fallback_used: false,
        dev_only: false,
        production_fail_closed: true,
        credential_values_exposed: false,
      }, {
        status: 503,
        headers: { "cache-control": "no-store, no-cache, must-revalidate" },
      });
    }
  }

  return NextResponse.json(
    {
      ...buildAdminClientExecutionVisibilityPacket(tenantKey, "client"),
      authority: "frontend_advisory",
      fallback_used: true,
      dev_only: true,
      production_fail_closed: false,
      credential_values_exposed: false,
    },
    {
      status: 200,
      headers: { "cache-control": "no-store, no-cache, must-revalidate" },
    }
  );
}
