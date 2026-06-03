import { NextRequest, NextResponse } from "next/server";
import {
  AGENT_CATALOGUE,
  getCatalogueForPackage,
  validateCatalogueSelection,
} from "@/lib/agentCatalogueProductionUx";

export const dynamic = "force-dynamic";

export async function GET(req: NextRequest): Promise<NextResponse> {
  const plan = req.nextUrl.searchParams.get("plan") || "starter";

  return NextResponse.json(getCatalogueForPackage(plan), {
    status: 200,
    headers: { "cache-control": "no-store, no-cache, must-revalidate" },
  });
}

export async function POST(req: NextRequest): Promise<NextResponse> {
  let body: Record<string, unknown> = {};

  try {
    body = await req.json();
  } catch {
    body = {};
  }

  const plan = body.plan || body.package_key || "starter";
  const selectedAgents = Array.isArray(body.selected_agents)
    ? body.selected_agents
    : Array.isArray(body.agents)
      ? body.agents
      : [];

  return NextResponse.json({
    ...validateCatalogueSelection(plan, selectedAgents),
    catalogue_total_count: AGENT_CATALOGUE.length,
  }, {
    status: 200,
    headers: { "cache-control": "no-store, no-cache, must-revalidate" },
  });
}
