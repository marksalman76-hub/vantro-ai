import { NextResponse } from "next/server";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.vantro.ai";

async function forwardBackendResponse(res: Response) {
  const text = await res.text();
  const contentType = res.headers.get("content-type") || "";
  const headers = contentType ? { "Content-Type": contentType } : undefined;

  if (text.trim()) {
    if (contentType.includes("application/json")) {
      return new NextResponse(text, { status: res.status, headers });
    }

    return NextResponse.json(
      res.ok
        ? { ok: true, status: res.status, response: text }
        : { error: text || res.statusText || "Backend request failed" },
      { status: res.status },
    );
  }

  return NextResponse.json(
    res.ok
      ? { ok: true, status: res.status }
      : { error: res.statusText || "Backend request failed" },
    { status: res.status },
  );
}

export async function POST(request: Request) {
  const token = request.headers.get("authorization") || "";

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

    if (res.status >= 500) {
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
      { error: "Could not start admin agent request", detail },
      { status: 502 },
    );
  }
}
