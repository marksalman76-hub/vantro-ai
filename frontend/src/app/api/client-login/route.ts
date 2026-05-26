import { NextRequest, NextResponse } from "next/server";

export const dynamic = "force-dynamic";

const BACKEND_URL =
  process.env.BACKEND_URL ||
  process.env.NEXT_PUBLIC_BACKEND_URL ||
  "https://api.trance-formation.com.au";

function extractToken(payload: any): string {
  return (
    payload?.token ||
    payload?.access_token ||
    payload?.client_token ||
    payload?.auth_token ||
    payload?.session?.token ||
    payload?.data?.token ||
    payload?.data?.access_token ||
    ""
  );
}

function extractTenant(payload: any): string {
  return (
    payload?.tenant_id ||
    payload?.tenantId ||
    payload?.client?.tenant_id ||
    payload?.data?.tenant_id ||
    "tenant_unknown"
  );
}

export async function POST(req: NextRequest) {
  const body = await req.text();

  const candidates = ["/api/client-login", "/client-login", "/api/login", "/login"];
  let finalResponse: Response | null = null;
  let finalText = "";

  for (const path of candidates) {
    const res = await fetch(`${BACKEND_URL}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "x-actor-role": "client" },
      body,
      cache: "no-store",
    });

    finalResponse = res;
    finalText = await res.text();

    if (res.status !== 404) break;
  }

  let payload: any = {};
  try {
    payload = finalText ? JSON.parse(finalText) : {};
  } catch {
    payload = {};
  }

  const response = NextResponse.json(payload, {
    status: finalResponse?.status || 500,
    headers: { "Cache-Control": "no-store" },
  });

  const token = extractToken(payload);
  const tenantId = extractTenant(payload);

  if (token) {
    response.cookies.set("client_token", token, {
      httpOnly: false,
      secure: true,
      sameSite: "lax",
      path: "/",
      maxAge: 60 * 60 * 24 * 7,
    });
  }

  if (tenantId) {
    response.cookies.set("tenant_id", tenantId, {
      httpOnly: false,
      secure: true,
      sameSite: "lax",
      path: "/",
      maxAge: 60 * 60 * 24 * 7,
    });
  }

  return response;
}
