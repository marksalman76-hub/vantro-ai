import { NextRequest, NextResponse } from "next/server";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.vantro.ai";

async function toJsonResponse(res: Response) {
  const text = await res.text();
  const contentType = res.headers.get("content-type") || "";
  const headers = contentType ? { "Content-Type": contentType } : undefined;

  if (text.trim()) {
    if (contentType.includes("application/json")) {
      return new NextResponse(text, { status: res.status, headers });
    }

    if (res.ok) {
      return NextResponse.json(
        { ok: true, status: res.status, response: text },
        { status: res.status }
      );
    }

    return NextResponse.json(
      { error: text || res.statusText || "Backend request failed" },
      { status: res.status }
    );
  }

  return NextResponse.json(
    res.ok
      ? { ok: true, status: res.status }
      : { error: res.statusText || "Backend request failed" },
    { status: res.status }
  );
}

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ agentId: string }> }
) {
  const { agentId } = await params;
  const token = request.headers.get("authorization") || "";
  try {
    const body = await request.text();
    const res = await fetch(`${API_URL}/api/admin/agents/${agentId}/run`, {
      method: "POST",
      headers: { Authorization: token, "Content-Type": "application/json" },
      body,
    });
    return toJsonResponse(res);
  } catch (error) {
    return NextResponse.json(
      { error: "Backend unreachable", detail: String(error) },
      { status: 502 }
    );
  }
}
