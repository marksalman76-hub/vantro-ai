import { NextResponse } from "next/server";
import { getClientSafeIntegrationConnectionHubStatus } from "@/lib/integrationConnectionHub";

export const dynamic = "force-dynamic";

export async function GET() {
  return NextResponse.json(getClientSafeIntegrationConnectionHubStatus());
}
