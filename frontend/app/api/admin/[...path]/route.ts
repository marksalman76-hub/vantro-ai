import { NextRequest, NextResponse } from "next/server";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.vantro.ai";

async function handler(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path: pathArr } = await params;
  const path = pathArr.join("/");
  // Prefer httpOnly cookie; fall back to Authorization header for backward compat
  const cookieToken = request.cookies.get("access_token")?.value;
  const token = cookieToken ? `Bearer ${cookieToken}` : (request.headers.get("authorization") || "");

  let body: string | undefined;
  if (request.method !== "GET" && request.method !== "HEAD") {
    try {
      body = await request.text();
    } catch {
      body = undefined;
    }
  }

  try {
    const res = await fetch(`${API_URL}/api/admin/${path}`, {
      method: request.method,
      headers: {
        Authorization: token,
        "Content-Type": "application/json",
      },
      ...(body !== undefined ? { body } : {}),
    });
    const data = await res.json();
    return NextResponse.json(data, { status: res.status });
  } catch {
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}

export const GET = handler;
export const POST = handler;
export const PUT = handler;
export const DELETE = handler;
export const PATCH = handler;
