import { NextRequest, NextResponse } from "next/server";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.vantro.ai";

async function forwardBackendResponse(res: Response) {
  const text = await res.text();
  const contentType = res.headers.get("content-type") || "";

  if (text.trim()) {
    if (contentType.includes("application/json")) {
      return new NextResponse(text, { status: res.status, headers: { "Content-Type": "application/json" } });
    }

    // Non-JSON error (nginx/ALB/WAF HTML page) — return a clean error, not raw markup
    if (!res.ok) {
      const status = res.status;
      const detail =
        status === 403 ? "Access denied by the server. Check that the backend service is healthy and the admin token is valid." :
        status === 502 || status === 503 || status === 504 ? "Backend service is temporarily unavailable. Please retry in a moment." :
        `Backend request failed (HTTP ${status}).`;
      return NextResponse.json({ error: detail }, { status });
    }

    return NextResponse.json({ ok: true, status: res.status, response: text }, { status: res.status });
  }

  return NextResponse.json(
    res.ok
      ? { ok: true, status: res.status }
      : { error: `Backend request failed (HTTP ${res.status}).` },
    { status: res.status },
  );
}

export async function POST(request: NextRequest) {
  const cookieToken = request.cookies?.get("access_token")?.value;
  const token = cookieToken ? `Bearer ${cookieToken}` : (request.headers.get("authorization") || "");

  try {
    const body = await request.json();
    const agentId = typeof body.agent_id === "string" ? body.agent_id.trim() : "";

    if (!agentId) {
      return NextResponse.json({ error: "Missing agent_id" }, { status: 400 });
    }

    const backendBody = JSON.stringify({
      prompt: body.prompt,
      context: body.context,
    });

    let res = await fetch(`${API_URL}/api/admin/agents/${agentId}/run`, {
      method: "POST",
      headers: { Authorization: token, "Content-Type": "application/json" },
      body: backendBody,
    });

    if (res.status === 404) {
      console.warn(`[admin-run-agent] admin endpoint 404 for agent=${agentId}, falling back to client route`);
      res = await fetch(`${API_URL}/api/agents/${agentId}/run`, {
        method: "POST",
        headers: { Authorization: token, "Content-Type": "application/json" },
        body: backendBody,
      });
    }

    return forwardBackendResponse(res);
  } catch (error) {
    const detail = error instanceof Error ? `${error.name}: ${error.message}` : String(error);
    console.error("[admin-run-agent] request failed", { detail });
    return NextResponse.json(
      { error: "Could not start admin agent request" },
      { status: 502 },
    );
  }
}
