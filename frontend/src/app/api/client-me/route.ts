import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL =
  process.env.BACKEND_URL ||
  process.env.NEXT_PUBLIC_BACKEND_URL ||
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  "https://ecommerce-ai-agent-platform-1.onrender.com";

const ADMIN_TOKEN =
  process.env.ADMIN_AUTH_SECRET ||
  process.env.ADMIN_AUTH_TOKEN ||
  process.env.ADMIN_BEARER_TOKEN ||
  process.env.OWNER_ADMIN_TOKEN ||
  "";

function backendHeaders() {
  const headers: Record<string, string> = {
    "x-tenant-id": "owner",
    "x-actor-role": "owner",
  };

  if (ADMIN_TOKEN) {
    headers.Authorization = `Bearer ${ADMIN_TOKEN}`;
  }

  return headers;
}

export async function GET(request: NextRequest) {
  const sessionToken = request.cookies.get("client_session")?.value || "";

  if (!sessionToken) {
    return NextResponse.json(
      { success: false, error: "not_authenticated" },
      { status: 401 }
    );
  }

  const response = await fetch(
    `${BACKEND_URL}/client/me?session_token=${encodeURIComponent(sessionToken)}`,
    {
      cache: "no-store",
      headers: backendHeaders(),
    }
  );

  const result = await response.json().catch(() => ({
    success: false,
    error: "client_me_backend_response_not_json",
  }));

  if (!response.ok || !result.success) {
    return NextResponse.json(
      {
        success: false,
        error: result.error || "client_account_lookup_failed",
      },
      { status: 401 }
    );
  }

  const account = result.account || {};

  return NextResponse.json({
    success: true,
    account: {
      company_name: account.company_name || "Client Workspace",
      contact_email: account.email || "",
      package_name: account.package || account.package_name || "Active package",
      package_status: account.status || "active",
      billing_status: "active",
      credits_remaining: account.credits_remaining ?? 0,
      credits_monthly: account.monthly_credits ?? 0,
      credits_used: account.credits_used ?? 0,
      active_agents: account.active_agents || [],
      paid_agents: account.active_agents || [],
    },
  });
}
