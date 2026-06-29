import { NextRequest, NextResponse } from "next/server";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.vantro.ai";

async function handler(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path: pathArr } = await params;
  const path = pathArr.join("/");
  const cookieToken = request.cookies.get("access_token")?.value;
  const token = cookieToken
    ? `Bearer ${cookieToken}`
    : (request.headers.get("authorization") || "");
  const query = new URL(request.url).search;
  const contentType = request.headers.get("content-type") || "";
  const headers: Record<string, string> = { Authorization: token };

  let body: BodyInit | undefined;
  if (request.method !== "GET" && request.method !== "HEAD") {
    if (contentType) headers["Content-Type"] = contentType;
    if (contentType.includes("multipart/form-data")) {
      body = Buffer.from(await request.arrayBuffer());
    } else {
      body = await request.text();
    }
  }

  try {
    const res = await fetch(`${API_URL}/api/agents/${path}${query}`, {
      method: request.method,
      headers,
      ...(body !== undefined ? { body } : {}),
    });

    const responseContentType = res.headers.get("content-type") || "";
    const responseText = await res.text();
    if (responseContentType.includes("application/json")) {
      return NextResponse.json(JSON.parse(responseText || "{}"), { status: res.status });
    }

    return new NextResponse(responseText, {
      status: res.status,
      headers: responseContentType ? { "Content-Type": responseContentType } : undefined,
    });
  } catch (e) {
    return NextResponse.json(
      { error: "Backend unreachable", detail: String(e) },
      { status: 502 }
    );
  }
}

export const GET = handler;
export const POST = handler;
export const PUT = handler;
export const PATCH = handler;
export const DELETE = handler;
