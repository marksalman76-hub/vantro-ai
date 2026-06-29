import { NextRequest, NextResponse } from "next/server";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.vantro.ai";

async function forwardBackendResponse(res: Response) {
  const contentType = res.headers.get("content-type") || "";
  const text = await res.text();

  if (!text.trim()) {
    return NextResponse.json(
      res.ok
        ? { ok: true, status: res.status }
        : { error: res.statusText || "Backend request failed" },
      { status: res.status },
    );
  }

  if (contentType.includes("application/json")) {
    return new NextResponse(text, {
      status: res.status,
      headers: { "Content-Type": contentType },
    });
  }

  return new NextResponse(text, {
    status: res.status,
    headers: contentType ? { "Content-Type": contentType } : undefined,
  });
}

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

    return forwardBackendResponse(res);
  } catch {
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}

export const GET = handler;
export const POST = handler;
export const PUT = handler;
export const DELETE = handler;
export const PATCH = handler;
