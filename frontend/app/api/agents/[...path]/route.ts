import { NextRequest, NextResponse } from "next/server";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.vantro.ai";

async function handler(request: NextRequest, { params }: { params: { path: string[] } }) {
  const path = params.path.join("/");
  const token = request.headers.get("authorization") || "";
  const url = new URL(request.url);
  const query = url.search;

  let body: string | undefined;
  if (request.method !== "GET" && request.method !== "HEAD") {
    try { body = await request.text(); } catch { body = undefined; }
  }

  try {
    const res = await fetch(`${API_URL}/api/agents/${path}${query}`, {
      method: request.method,
      headers: { Authorization: token, "Content-Type": "application/json" },
      ...(body !== undefined ? { body } : {}),
    });
    const data = await res.json();
    return NextResponse.json(data, { status: res.status });
  } catch (e) {
    return NextResponse.json({ error: "Backend unreachable", detail: String(e) }, { status: 502 });
  }
}

export const GET = handler;
export const POST = handler;
export const PUT = handler;
export const PATCH = handler;
export const DELETE = handler;
