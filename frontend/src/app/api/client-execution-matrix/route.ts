import { NextRequest, NextResponse } from "next/server";

export const dynamic = "force-dynamic";

const BACKEND_URL =
  process.env.BACKEND_URL ||
  process.env.NEXT_PUBLIC_BACKEND_URL ||
  "https://api.trance-formation.com.au";

function getBearer(req: NextRequest): string {
  const auth = req.headers.get("authorization") || "";
  if (auth.toLowerCase().startsWith("bearer ")) return auth;

  const cookieToken =
    req.cookies.get("client_token")?.value ||
    req.cookies.get("token")?.value ||
    req.cookies.get("auth_token")?.value ||
    "";

  return cookieToken ? `Bearer ${cookieToken}` : "";
}

async function proxy(req: NextRequest, path: string) {
  const bearer = getBearer(req);

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    "x-actor-role": req.headers.get("x-actor-role") || "client",
    "x-tenant-id": req.headers.get("x-tenant-id") || req.cookies.get("tenant_id")?.value || "tenant_unknown",
  };

  if (bearer) headers.Authorization = bearer;

  const init: RequestInit = {
    method: req.method,
    headers,
    cache: "no-store",
  };

  if (!["GET", "HEAD"].includes(req.method)) {
    const text = await req.text();
    if (text) init.body = text;
  }

  const res = await fetch(`${BACKEND_URL}${path}`, init);
  const contentType = res.headers.get("content-type") || "application/json";
  const body = await res.text();

  return new NextResponse(body, {
    status: res.status,
    headers: {
      "Content-Type": contentType,
      "Cache-Control": "no-store",
    },
  });
}

export async function GET(req: NextRequest) {
  return proxy(req, "/client/execution-events");
}

export async function POST(req: NextRequest) {
  return proxy(req, "/client/execution-events");
}

export async function PUT(req: NextRequest) {
  return proxy(req, "/client/execution-events");
}

export async function PATCH(req: NextRequest) {
  return proxy(req, "/client/execution-events");
}
