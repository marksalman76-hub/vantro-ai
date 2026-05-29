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
  const body = await req.json();

  if (!ADMIN_TOKEN) {
    return NextResponse.json(
      {
        success: false,
        error: "admin_token_not_configured",
        message: "Admin token is not configured for outcome action planning.",
      },
      { status: 500 }
    );
  }

  const response = await fetch(`${BACKEND_URL}/admin/outcome-action-plan`, {
    method: "POST",
    cache: "no-store",
    headers: {
      "Content-Type": "application/json",
      "x-admin-token": ADMIN_TOKEN,
      "x-actor-role": "owner_admin",
      "x-tenant-id": "owner_admin",
      "x-csrf-token": "outcome-action-plan",
      origin: process.env.NEXT_PUBLIC_FRONTEND_URL || "https://app.trance-formation.com.au",
    },
    body: JSON.stringify({
      outcome_text: body.outcome_text || "",
      source_agent: body.source_agent || "unknown_agent",
      tenant_id: body.tenant_id || "owner_admin",
      project_id: body.project_id || "admin_outcome_action_plan",
      owner_approved: body.owner_approved === true,
    }),
  });

  const data = await response.json().catch(() => ({
    success: false,
    error: "backend_response_not_json",
  }));

  return NextResponse.json(
    {
      success: response.ok && data?.success === true,
      backend_status: response.status,
      data,
    },
    { status: response.ok ? 200 : response.status }
  );
}

export async function GET() {
  return NextResponse.json({
    success: true,
    route: "outcome-action-plan",
    methods: ["POST"],
    status: "ready",
  });
}
