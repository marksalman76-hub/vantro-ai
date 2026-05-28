import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL =
  process.env.BACKEND_API_URL ||
  process.env.NEXT_PUBLIC_BACKEND_API_URL ||
  "https://api.trance-formation.com.au";

const ADMIN_TOKEN =
  process.env.ADMIN_PLATFORM_TOKEN ||
  process.env.ADMIN_AUTH_SECRET ||
  "";

export async function POST(req: NextRequest) {
  if (!ADMIN_TOKEN) {
    return NextResponse.json(
      { success: false, error: "admin_token_not_configured" },
      { status: 500 }
    );
  }

  const body = await req.json();

  const payload = {
    tenant_id: "owner_admin",
    requested_agent: body.requested_agent || "marketing_specialist_agent",
    workflow_stage: "admin_live_execution_output_viewer",
    task:
      body.task ||
      "Produce a commercial-quality governed live execution result.",
    action_type: "governed_live_provider_generation",
    region: body.region || "Global",
    language: body.language || "English",
    currency: body.currency || "USD",
    owner_approved: true,
    execute_real_world_action: true,
    project_id: "admin_live_execution_output_viewer",
    actor_role: "owner_admin",
    requested_credits: 1,
  };

  const response = await fetch(`${BACKEND_URL}/run-agent`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-admin-token": ADMIN_TOKEN,
      "x-actor-role": "owner_admin",
      "x-tenant-id": "owner_admin",
      "x-csrf-token": "admin-live-execution-output-viewer",
      origin: process.env.NEXT_PUBLIC_FRONTEND_URL || "https://trance-formation.com.au",
    },
    body: JSON.stringify(payload),
    cache: "no-store",
  });

  const data = await response.json();

  return NextResponse.json({
    success: response.ok,
    backend_status: response.status,
    data,
  });
}
