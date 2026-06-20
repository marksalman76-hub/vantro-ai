import { NextRequest, NextResponse } from "next/server";
import { validateCatalogueSelection } from "@/lib/agentCatalogueProductionUx";

export const dynamic = "force-dynamic";

const BACKEND_URL =
  process.env.BACKEND_API_URL ||
  process.env.NEXT_PUBLIC_BACKEND_API_URL ||
  "https://api.trance-formation.com.au";

const ADMIN_TOKEN =
  process.env.ADMIN_PLATFORM_TOKEN ||
  process.env.ADMIN_AUTH_SECRET ||
  "";

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

  const tenantId = String(body.tenant_id || body.tenantId || "client_demo_001");
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    "x-tenant-id": tenantId,
    "x-actor-role": String(body.actor_role || "owner_admin"),
    "x-csrf-token": "signup-agent-selection-validate",
    origin: process.env.NEXT_PUBLIC_FRONTEND_URL || "https://app.trance-formation.com.au",
  };

  if (ADMIN_TOKEN) {
    headers["x-admin-token"] = ADMIN_TOKEN;
    headers.Authorization = `Bearer ${ADMIN_TOKEN}`;
  }

  const backendResponse = await fetch(`${BACKEND_URL}/signup-agent-selection/validate`, {
    method: "POST",
    cache: "no-store",
    headers,
    body: JSON.stringify({ ...body, plan, selected_agents: selectedAgents }),
  }).catch(() => null);

  if (backendResponse) {
    const backendData = await backendResponse.json().catch(() => null);
    if (backendResponse.ok && backendData?.success !== false) {
      return NextResponse.json(backendData, {
        status: 200,
        headers: { "cache-control": "no-store, no-cache, must-revalidate" },
      });
    }
  }

  const validation = validateCatalogueSelection(plan, selectedAgents);

  return NextResponse.json(
    {
      ...validation,
      fallback_authority: "frontend_advisory_only",
      backend_activation_required: true,
      canonical_backend_unavailable: true,
    },
    {
      status: validation.success ? 200 : 400,
      headers: { "cache-control": "no-store, no-cache, must-revalidate" },
    }
  );
}
