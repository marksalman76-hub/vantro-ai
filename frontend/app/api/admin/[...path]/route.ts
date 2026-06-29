import { NextRequest, NextResponse } from "next/server";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.vantro.ai";

async function handler(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path: pathArr } = await params;
  const path = pathArr.join("/");

  // Skip brand-assets — it has dedicated handlers
  if (path.startsWith("brand-assets")) {
    return NextResponse.json({ detail: "Not Found" }, { status: 404 });
  }

  // Prefer httpOnly cookie; fall back to Authorization header for backward compat
  const cookieToken = request.cookies.get("access_token")?.value;
  const token = cookieToken ? `Bearer ${cookieToken}` : (request.headers.get("authorization") || "");

  let body: ArrayBuffer | undefined;
  if (request.method !== "GET" && request.method !== "HEAD") {
    try {
      body = await request.arrayBuffer();
    } catch {
      body = undefined;
    }
  }

  try {
    const headers: Record<string, string> = {
      Authorization: token,
    };
    const incomingContentType = request.headers.get("content-type");
    if (incomingContentType) {
      headers["Content-Type"] = incomingContentType;
    }

    const res = await fetch(`${API_URL}/api/admin/${path}`, {
      method: request.method,
      headers,
      ...(body !== undefined ? { body } : {}),
    });

    const contentType = res.headers.get("content-type") || "application/json";
    if (contentType.includes("application/json")) {
      const data = await res.json();
      return NextResponse.json(data, { status: res.status });
    } else {
      const data = await res.arrayBuffer();
      return new NextResponse(data, { status: res.status, headers: { "Content-Type": contentType } });
    }
  } catch {
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}

export const GET = handler;
export const POST = handler;
export const PUT = handler;
export const DELETE = handler;
export const PATCH = handler;
