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
      { success: false, error: "admin_token_not_configured" },
      { status: 500 }
    );
  }

  const response = await fetch(`${BACKEND_URL}/delegated-workforce-execution`, {
    method: "POST",
    cache: "no-store",
    headers: {
      "Content-Type": "application/json",
      "x-admin-token": ADMIN_TOKEN,
      "x-actor-role": "owner_admin",
      "x-tenant-id": body.tenant_id || "owner_admin",
      "x-csrf-token": "delegated-workforce-execution",
      origin: process.env.NEXT_PUBLIC_FRONTEND_URL || "https://app.trance-formation.com.au",
    },
    body: JSON.stringify({
      implementation_plan: body.implementation_plan || { action_packets: [] },
      owner_approved: body.owner_approved === true,
      client_owned_agents: body.client_owned_agents || [],
      package_tier: body.package_tier || "enterprise",
      connected_integrations: body.connected_integrations || [],
      tenant_id: body.tenant_id || "owner_admin",
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
    route: "delegated-workforce-execution",
    methods: ["POST"],
    status: "ready",
  });
}
