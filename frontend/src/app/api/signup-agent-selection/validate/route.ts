import { NextRequest, NextResponse } from "next/server";
import { validateCatalogueSelection } from "@/lib/agentCatalogueProductionUx";

export const dynamic = "force-dynamic";

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

  const validation = validateCatalogueSelection(plan, selectedAgents);

  return NextResponse.json(validation, {
    status: validation.success ? 200 : 400,
    headers: { "cache-control": "no-store, no-cache, must-revalidate" },
  });
}
