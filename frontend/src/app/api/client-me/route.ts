import { NextRequest, NextResponse } from "next/server";

export const dynamic = "force-dynamic";

const BACKEND_URL =
  process.env.BACKEND_URL ||
  process.env.NEXT_PUBLIC_BACKEND_URL ||
  "https://api.trance-formation.com.au";

function getSessionToken(req: NextRequest): string {
  const auth = req.headers.get("authorization") || "";
  if (auth.toLowerCase().startsWith("bearer ")) return auth.slice(7).trim();

  return (
    req.cookies.get("client_token")?.value ||
    req.cookies.get("token")?.value ||
    req.cookies.get("auth_token")?.value ||
    ""
  );
}

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

  const sessionToken = getSessionToken(req);
  let backendPath = path;

  if (sessionToken && (path === "/client/me" || path === "/client/business-profile")) {
    const joiner = backendPath.includes("?") ? "&" : "?";
    backendPath = `${backendPath}${joiner}session_token=${encodeURIComponent(sessionToken)}`;
  }

  const res = await fetch(`${BACKEND_URL}${backendPath}`, init);
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
  return proxy(req, "/client/me");
}

export async function POST(req: NextRequest) {
  return proxy(req, "/client/me");
}

export async function PUT(req: NextRequest) {
  return proxy(req, "/client/me");
}

export async function PATCH(req: NextRequest) {
  return proxy(req, "/client/me");
}
