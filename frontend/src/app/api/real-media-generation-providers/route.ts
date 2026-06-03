import { NextRequest, NextResponse } from "next/server";
import { resolveTenantKey } from "@/lib/deliverablePersistence";
import {
  attachRealMediaProviderDecision,
  getRealMediaProviderRegistry,
  inferMediaCapability,
  selectRealMediaProvider,
} from "@/lib/realMediaGenerationProviders";

export const dynamic = "force-dynamic";

export async function GET(): Promise<NextResponse> {
  const providers = getRealMediaProviderRegistry();

  return NextResponse.json({
    success: true,
    client_safe: true,
    real_media_generation_providers_enabled: true,
    live_external_call_executed: false,
    external_action_performed: false,
    providers,
  }, {
    status: 200,
    headers: {
      "cache-control": "no-store, no-cache, must-revalidate",
    },
  });
}

export async function POST(req: NextRequest): Promise<NextResponse> {
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

  return NextResponse.json(attachRealMediaProviderDecision(tenantKey, {
    ...body,
    ...decision,
  }), {
    status: 200,
    headers: {
      "cache-control": "no-store, no-cache, must-revalidate",
    },
  });
}
