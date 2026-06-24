import { NextRequest, NextResponse } from "next/server";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function proxy(request: NextRequest, params: { path: string[] }) {
  const cookieToken = request.cookies.get("access_token")?.value;
  const token = cookieToken
    ? `Bearer ${cookieToken}`
    : request.headers.get("authorization") || "";

  const path = params.path.join("/");
  const url = new URL(request.url);
  const backendUrl = `${API_BASE}/api/teams/${path}${url.search}`;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(token ? { Authorization: token } : {}),
  };

  const body =
    request.method !== "GET" && request.method !== "HEAD"
      ? await request.text()
      : undefined;

  const res = await fetch(backendUrl, { method: request.method, headers, body });
  const data = await res.text();
  return new NextResponse(data, {
    status: res.status,
    headers: { "Content-Type": res.headers.get("Content-Type") || "application/json" },
  });
}

export const GET    = (req: NextRequest, ctx: { params: { path: string[] } }) => proxy(req, ctx.params);
export const POST   = (req: NextRequest, ctx: { params: { path: string[] } }) => proxy(req, ctx.params);
export const DELETE = (req: NextRequest, ctx: { params: { path: string[] } }) => proxy(req, ctx.params);
