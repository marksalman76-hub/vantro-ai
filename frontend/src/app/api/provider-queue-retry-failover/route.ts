import { NextRequest, NextResponse } from "next/server";
import { resolveTenantKey } from "@/lib/deliverablePersistence";
import {
  getLatestProviderQueueJob,
  getProviderQueueJobs,
  persistProviderQueueJob,
} from "@/lib/providerQueueRetryFailover";
import { selectRealMediaProvider, inferMediaCapability } from "@/lib/realMediaGenerationProviders";

export const dynamic = "force-dynamic";

export async function GET(req: NextRequest): Promise<NextResponse> {
  const tenantKey = resolveTenantKey(req.headers, {});
  const jobs = getProviderQueueJobs(tenantKey);
  const latest = getLatestProviderQueueJob(tenantKey);

  return NextResponse.json({
    success: true,
    tenant_scoped: true,
    client_safe: true,
    provider_queue_retry_failover_enabled: true,
    live_external_call_executed: false,
    external_action_performed: false,
    provider_queue_count: jobs.length,
    latest_provider_queue_job: latest,
    provider_queue_jobs: jobs,
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

  const job = persistProviderQueueJob(tenantKey, decision, body);

  return NextResponse.json({
    success: true,
    tenant_scoped: true,
    client_safe: true,
    provider_queue_retry_failover_enabled: true,
    provider_queue_job: job,
    provider_queue_status: job.status,
    provider_failover_available: job.failover_available,
    live_external_call_executed: false,
    external_action_performed: false,
  }, {
    status: 200,
    headers: {
      "cache-control": "no-store, no-cache, must-revalidate",
    },
  });
}
