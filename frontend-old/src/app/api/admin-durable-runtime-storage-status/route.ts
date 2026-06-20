import { NextRequest, NextResponse } from "next/server";
import { buildDurableRuntimeStorageStatus } from "@/lib/durableRuntimeStorage";

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

  return NextResponse.json({
    ...buildDurableRuntimeStorageStatus(),
    admin_safe: true,
    owner_visibility: true,
    credential_values_exposed: false,
  }, {
    status: 200,
    headers: { "cache-control": "no-store, no-cache, must-revalidate" },
  });
}
