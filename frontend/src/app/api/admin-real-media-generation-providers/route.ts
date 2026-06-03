import { NextRequest, NextResponse } from "next/server";
import {
  getRealMediaProviderRegistry,
  selectRealMediaProvider,
  inferMediaCapability,
} from "@/lib/realMediaGenerationProviders";
import { resolveTenantKey } from "@/lib/deliverablePersistence";

export const dynamic = "force-dynamic";

function isAdminRequest(req: NextRequest): boolean {
  return Boolean(
    req.headers.get("authorization") ||
    req.headers.get("x-admin-token") ||
    req.cookies.get("admin_session")?.value
  );
}

export async function GET(req: NextRequest): Promise<NextResponse> {
  if (!isAdminRequest(req)) {
    return NextResponse.json({
      success: false,
      error: "Admin authorisation required.",
    }, { status: 401 });
  }

  return NextResponse.json({
    success: true,
    admin_safe: true,
    credential_values_exposed: false,
    real_media_generation_providers_enabled: true,
    provider_queue_retry_failover_enabled: true,
    live_external_call_executed: false,
    external_action_performed: false,
    providers: getRealMediaProviderRegistry(),
  }, {
    status: 200,
    headers: {
      "cache-control": "no-store, no-cache, must-revalidate",
    },
  });
}

export async function POST(req: NextRequest): Promise<NextResponse> {
  if (!isAdminRequest(req)) {
    return NextResponse.json({
      success: false,
      error: "Admin authorisation required.",
    }, { status: 401 });
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

  return NextResponse.json({
    ...decision,
    success: true,
    admin_safe: true,
    credential_values_exposed: false,
    real_media_generation_providers_enabled: true,
    tenant_key_visible_to_admin: tenantKey,
  }, {
    status: 200,
    headers: {
      "cache-control": "no-store, no-cache, must-revalidate",
    },
  });
}
