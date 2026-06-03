import { NextRequest, NextResponse } from "next/server";
import { resolveTenantKey } from "@/lib/deliverablePersistence";
import { buildBillingSubscriptionStatus } from "@/lib/billingStripeSubscriptions";

export const dynamic = "force-dynamic";

export async function GET(req: NextRequest): Promise<NextResponse> {
  const tenantKey = resolveTenantKey(req.headers, {});

  return NextResponse.json(buildBillingSubscriptionStatus(tenantKey), {
    status: 200,
    headers: { "cache-control": "no-store, no-cache, must-revalidate" },
  });
}
