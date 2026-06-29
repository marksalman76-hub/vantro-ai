import { NextRequest, NextResponse } from "next/server";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.vantro.ai";

async function handler(request: NextRequest, { params }: { params: Promise<{ path: string[] }> }) {
  const { path: pathArr } = await params;
  const path = pathArr.join("/");
  const cookieToken = request.cookies.get("access_token")?.value;
  const token = cookieToken ? `Bearer ${cookieToken}` : (request.headers.get("authorization") || "");
  const url = new URL(request.url);
  const query = url.search;

  const contentType = request.headers.get("content-type") || "";
  const isMultipart = contentType.includes("multipart/form-data");

  let body: BodyInit | undefined;
  if (request.method !== "GET" && request.method !== "HEAD") {
    try {
      body = isMultipart ? await request.blob() : await request.text();
    } catch { body = undefined; }
  }

  const forwardHeaders: Record<string, string> = { Authorization: token };
  if (isMultipart) {
    forwardHeaders["Content-Type"] = contentType; // preserve boundary
  } else {
    forwardHeaders["Content-Type"] = "application/json";
  }

  try {
    const res = await fetch(`${API_URL}/api/agents/${path}${query}`, {
      method: request.method,
      headers: forwardHeaders,
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
