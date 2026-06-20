import { NextRequest, NextResponse } from "next/server";
import { getCatalogueForPackage } from "@/lib/agentCatalogueProductionUx";

export const dynamic = "force-dynamic";

export async function GET(
  _req: NextRequest,
  context: { params: Promise<{ plan: string }> }
): Promise<NextResponse> {
  const { plan } = await context.params;

  return NextResponse.json(getCatalogueForPackage(plan), {
    status: 200,
    headers: { "cache-control": "no-store, no-cache, must-revalidate" },
  });
}
