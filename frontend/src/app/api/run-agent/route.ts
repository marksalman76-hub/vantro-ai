import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL =
  process.env.BACKEND_URL ||
  process.env.NEXT_PUBLIC_BACKEND_URL ||
  "https://api.trance-formation.com.au";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    const selectedAgents = Array.isArray(body?.selected_agents)
      ? body.selected_agents
      : [];

    const primaryAgent =
      String(body?.agent_id || body?.agentId || selectedAgents[0] || "").trim();

    const task = String(body?.task || body?.prompt || "Run live agent execution").trim();

    if (!primaryAgent && selectedAgents.length === 0) {
      return NextResponse.json(
        { success: false, error: "missing_agent_selection" },
        { status: 400 }
      );
    }

    const backendPayload = {
      ...body,
      agent_id: primaryAgent || selectedAgents[0],
      selected_agents: selectedAgents.length > 0 ? selectedAgents : [primaryAgent],
      task,
      prompt: body?.prompt || task,
      source: "client_workspace",
      execution_surface: "client_page",
    };

    const tenantId =
      request.headers.get("x-tenant-id") ||
      request.cookies.get("tenant_id")?.value ||
      body?.tenant_id ||
      "client_demo_001";

    const actorRole =
      request.headers.get("x-actor-role") ||
      body?.actor_role ||
      "customer";

    const response = await fetch(`${BACKEND_URL.replace(/\/$/, "")}/run-agent`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-tenant-id": String(tenantId),
        "x-actor-role": String(actorRole),
      },
      body: JSON.stringify(backendPayload),
      cache: "no-store",
    });

    const text = await response.text();

    let data: any;
    try {
      data = JSON.parse(text);
    } catch {
      data = { raw_response: text };
    }

    return NextResponse.json(
      {
        success: response.ok,
        proxied_to_backend: true,
        backend_status: response.status,
        backend_url: "/run-agent",
        agent_id: backendPayload.agent_id,
        selected_agents: backendPayload.selected_agents,
        result: data,
        execution: data?.execution || data,
        deliverable: data?.deliverable || data?.execution?.deliverable || data?.result?.deliverable || null,
      },
      { status: response.ok ? 200 : response.status }
    );
  } catch (error) {
    return NextResponse.json(
      {
        success: false,
        error: "backend_execution_proxy_failed",
        detail: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 500 }
    );
  }
}