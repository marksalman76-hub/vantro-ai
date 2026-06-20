import { NextRequest, NextResponse } from "next/server";
import { resolveTenantKey } from "@/lib/deliverablePersistence";
import { evaluatePackageCreditEnforcement } from "@/lib/packageCreditEnforcement";

export const dynamic = "force-dynamic";

export async function GET(req: NextRequest): Promise<NextResponse> {
  const tenantKey = resolveTenantKey(req.headers, {});
  const decision = evaluatePackageCreditEnforcement(tenantKey, req.headers, {});

  return NextResponse.json({
    success: true,
    client_safe: true,
    package_credit_enforcement_enabled: true,
    package_credit_decision: decision,
  }, {
    status: 200,
    headers: { "cache-control": "no-store, no-cache, must-revalidate" },
  });
}
