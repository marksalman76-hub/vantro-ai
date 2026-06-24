import { NextRequest, NextResponse } from "next/server";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.vantro.ai";

async function handler(request: NextRequest, { params }: { params: Promise<{ path: string[] }> }) {
  const { path: pathArr } = await params;
  const path = pathArr.join("/");
  const token = request.headers.get("authorization") || "";

  let body: string | undefined;
  if (request.method !== "GET" && request.method !== "HEAD") {
    try { body = await request.text(); } catch { body = undefined; }
  }

  try {
    const res = await fetch(`${API_URL}/api/packages/${path}`, {
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
