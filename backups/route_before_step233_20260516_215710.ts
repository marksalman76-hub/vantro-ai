import { cookies } from "next/headers";
import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL =
  process.env.BACKEND_URL ||
  process.env.NEXT_PUBLIC_BACKEND_URL ||
  "https://ecommerce-ai-agent-platform-1.onrender.com";

function scrubClientVisiblePayload(value: unknown): unknown {
  const raw = JSON.stringify(value ?? {});
  const scrubbed = raw
    .replace(/client_[a-zA-Z0-9_-]+/g, "[protected]")
    .replace(/tenant_[a-zA-Z0-9_-]+/g, "[protected]")
    .replace(/sk_live_[a-zA-Z0-9]+/g, "[protected]")
    .replace(/sk_test_[a-zA-Z0-9]+/g, "[protected]")
    .replace(/whsec_[a-zA-Z0-9]+/g, "[protected]")
    .replace(/postgresql:\/\/[^"]+/g, "[protected]");

  try {
    return JSON.parse(scrubbed);
  } catch {
    return {
      success: false,
      message: "Unable to render response safely.",
    };
  }
}

export async function POST(request: NextRequest) {
  const cookieStore = await cookies();
  const sessionToken = cookieStore.get("client_session")?.value;

  if (!sessionToken) {
    return NextResponse.json(
      {
        success: false,
        message: "Please log in again before running an agent.",
      },
      { status: 401 }
    );
  }

  const body = await request.json();

  const meResponse = await fetch(
    `${BACKEND_URL}/client/me?session_token=${encodeURIComponent(sessionToken)}`,
    {
      method: "GET",
      cache: "no-store",
    }
  );

  const meData = await meResponse.json().catch(() => null);

  if (!meResponse.ok || !meData?.success || !meData?.account) {
    return NextResponse.json(
      {
        success: false,
        message: "Client account could not be verified.",
      },
      { status: 401 }
    );
  }

  const account = meData.account;
  const activeAgents: string[] = Array.isArray(account.active_agents)
    ? account.active_agents
    : [];

  const requestedAgent = String(body.requested_agent || "");

  if (!activeAgents.includes(requestedAgent)) {
    return NextResponse.json(
      {
        success: false,
        message: "This agent is not active on your account.",
      },
      { status: 403 }
    );
  }

  const backendPayload = {
    tenant_id: account.tenant_id,
    requested_agent: requestedAgent,
    workflow_stage: "store_creation",
    action_type: "product_copy_generation",
    actor_role: "customer",
    owner_approved: false,
    task: String(body.task || ""),
    region: body.region || "Global",
    language: body.language || "English",
    currency: body.currency || "USD",
  };

  const response = await fetch(`${BACKEND_URL}/run-agent`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-tenant-id": account.tenant_id,
      "x-actor-role": "customer",
    },
    body: JSON.stringify(backendPayload),
  });

  const data = await response.json().catch(() => ({
    success: false,
    message: "Backend returned an invalid response.",
  }));

  const safeData = scrubClientVisiblePayload(data);

  return NextResponse.json(safeData, { status: response.status });
}
