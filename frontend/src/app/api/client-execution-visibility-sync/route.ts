import { NextRequest, NextResponse } from "next/server";
import { resolveTenantKey } from "@/lib/deliverablePersistence";
import { buildAdminClientExecutionVisibilityPacket } from "@/lib/adminClientExecutionVisibilitySync";

export const dynamic = "force-dynamic";

export async function GET(req: NextRequest): Promise<NextResponse> {
  const tenantKey = resolveTenantKey(req.headers, {});

  return NextResponse.json(
    buildAdminClientExecutionVisibilityPacket(tenantKey, "client"),
    {
      status: 200,
      headers: { "cache-control": "no-store, no-cache, must-revalidate" },
    }
  );
}
