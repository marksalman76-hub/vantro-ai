import { NextRequest, NextResponse } from "next/server";
import { resolveTenantKey } from "@/lib/deliverablePersistence";
import { selectRealMediaProvider, inferMediaCapability } from "@/lib/realMediaGenerationProviders";

export const dynamic = "force-dynamic";

function backendBaseUrl(): string | null {
  const raw =
    process.env.BACKEND_API_URL ||
    process.env.NEXT_PUBLIC_BACKEND_API_URL ||
    process.env.NEXT_PUBLIC_API_BASE_URL ||
    "";

  const trimmed = raw.trim();
  return trimmed ? trimmed.replace(/\/$/, "") : null;
}

function backendHeaders(req: NextRequest, tenantKey: string): Record<string, string> {
  const headers: Record<string, string> = {
    "content-type": "application/json",
    "x-tenant-key": tenantKey,
  };

  const auth = req.headers.get("authorization");
  const adminToken = req.headers.get("x-admin-token") || process.env.ADMIN_PLATFORM_TOKEN || "";
  const cookie = req.headers.get("cookie");

  if (auth) headers.authorization = auth;
  if (adminToken) headers["x-admin-token"] = adminToken;
  if (cookie) headers.cookie = cookie;

  return headers;
}

function backendUnavailable(): NextResponse {
  return NextResponse.json({
    success: false,
    durable_provider_ledger_available: false,
    provider_queue_retry_failover_enabled: false,
    error: "provider_queue_backend_unavailable",
    tenant_scoped: true,
    client_safe: true,
    credential_values_exposed: false,
    live_external_call_executed: false,
    external_action_performed: false,
  }, {
    status: 503,
    headers: {
      "cache-control": "no-store, no-cache, must-revalidate",
    },
  });
}

async function readBackendJson(response: Response): Promise<unknown> {
  const text = await response.text();
  if (!text) return {};

  try {
    return JSON.parse(text);
  } catch {
    return {
      success: false,
      error: "provider_queue_backend_returned_non_json",
      raw_status: response.status,
      credential_values_exposed: false,
    };
  }
}

export async function GET(req: NextRequest): Promise<NextResponse> {
  const tenantKey = resolveTenantKey(req.headers, {});
  const backendUrl = backendBaseUrl();

  if (!backendUrl) {
    return backendUnavailable();
  }

  const url = new URL(`${backendUrl}/provider-queue-retry-failover`);
  url.searchParams.set("tenant_id", tenantKey);
  const provider = req.nextUrl.searchParams.get("provider");
  if (provider) url.searchParams.set("provider", provider);

  const response = await fetch(url, {
    method: "GET",
    headers: backendHeaders(req, tenantKey),
    cache: "no-store",
  });
  const payload = await readBackendJson(response);

  return NextResponse.json(payload, {
    status: response.status,
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
  const backendUrl = backendBaseUrl();

  if (!backendUrl) {
    return backendUnavailable();
  }

  const capability = inferMediaCapability(body);
  const decision = selectRealMediaProvider({
    tenant_key: tenantKey,
    requested_capability: capability,
    prompt: String(body.prompt || body.task || ""),
    asset_type: String(body.asset_type || ""),
    owner_approved: Boolean(body.owner_approved || body.owner_approval_granted),
    dry_run: true,
  });

  const explicitIdempotencyKey = String(
    body.idempotency_key ||
    body.client_request_id ||
    body.request_id ||
    body.job_id ||
    ""
  );
  const providerPayload = {
    ...body,
    tenant_id: String(body.tenant_id || body.tenant_key || tenantKey),
    tenant_key: tenantKey,
    provider: decision.provider_selected || body.provider || body.primary_provider || "unknown",
    primary_provider: decision.provider_selected,
    requested_capability: capability,
    action_type: String(body.action_type || capability),
    real_media_provider_decision: decision,
    idempotency_key: explicitIdempotencyKey || undefined,
    live_external_call_executed: false,
    external_action_performed: false,
  };

  const response = await fetch(`${backendUrl}/provider-queue-retry-failover`, {
    method: "POST",
    headers: backendHeaders(req, tenantKey),
    body: JSON.stringify(providerPayload),
    cache: "no-store",
  });
  const payload = await readBackendJson(response);
  const payloadObject = payload && typeof payload === "object" ? payload as Record<string, unknown> : {};

  return NextResponse.json({
    ...payloadObject,
    tenant_scoped: true,
    client_safe: true,
    provider_queue_retry_failover_enabled: Boolean(
      payloadObject.provider_queue_retry_failover_enabled ?? payloadObject.success
    ),
    live_external_call_executed: false,
    external_action_performed: false,
  }, {
    status: response.status,
    headers: {
      "cache-control": "no-store, no-cache, must-revalidate",
    },
  });
}
