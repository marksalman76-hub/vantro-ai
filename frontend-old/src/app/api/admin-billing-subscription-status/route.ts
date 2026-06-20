import { NextRequest, NextResponse } from "next/server";
import { buildBillingSubscriptionStatus } from "@/lib/billingStripeSubscriptions";

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
    return NextResponse.json(
      { success: false, error: "Admin authorisation required." },
      { status: 401 }
    );
  }

  const tenantKey =
    req.nextUrl.searchParams.get("tenant_key") ||
    req.nextUrl.searchParams.get("tenant_id") ||
    req.headers.get("x-tenant-key") ||
    req.headers.get("x-tenant-id") ||
    "default_client_workspace";

  return NextResponse.json({
    ...buildBillingSubscriptionStatus(tenantKey),
    admin_safe: true,
    owner_visibility: true,
    credential_values_exposed: false,
  }, {
    status: 200,
    headers: { "cache-control": "no-store, no-cache, must-revalidate" },
  });
}
