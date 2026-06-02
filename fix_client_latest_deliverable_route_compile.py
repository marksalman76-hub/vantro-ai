from pathlib import Path

p = Path("frontend/src/app/api/client-latest-deliverable/route.ts")

p.write_text("""import { NextRequest, NextResponse } from "next/server";

export const dynamic = "force-dynamic";

const BACKEND_URL =
  process.env.BACKEND_URL ||
  process.env.NEXT_PUBLIC_BACKEND_URL ||
  "https://api.trance-formation.com.au";

function getBearer(req: NextRequest): string {
  const auth = req.headers.get("authorization") || "";

  if (auth.toLowerCase().startsWith("bearer ")) {
    return auth;
  }

  const cookieToken =
    req.cookies.get("client_token")?.value ||
    req.cookies.get("token")?.value ||
    req.cookies.get("auth_token")?.value ||
    "";

  return cookieToken ? "Bearer " + cookieToken : "";
}

export async function GET(req: NextRequest) {
  try {
    const bearer = getBearer(req);

    const tenantId =
      req.headers.get("x-tenant-id") ||
      req.cookies.get("tenant_id")?.value ||
      "owner_managed_demo_client";

    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      "x-actor-role": req.headers.get("x-actor-role") || "client",
      "x-tenant-id": tenantId,
    };

    if (bearer) {
      headers.Authorization = bearer;
    }

    const url =
      BACKEND_URL +
      "/client/execution-events?tenant_id=" +
      encodeURIComponent(tenantId) +
      "&project_id=default_project&limit=20";

    const response = await fetch(url, {
      method: "GET",
      headers,
      cache: "no-store",
    });

    const data = await response.json();

    const latest =
      data?.events?.[0] ||
      data?.executions?.[0] ||
      data?.records?.[0] ||
      null;

    const deliverable =
      latest?.deliverable ||
      latest?.result ||
      latest?.output ||
      latest?.execution_result ||
      latest?.payload ||
      null;

    return NextResponse.json({
      success: true,
      source: "backend_runtime",
      execution: latest,
      deliverable,
    });
  } catch (error) {
    return NextResponse.json({
      success: false,
      error: "client_latest_deliverable_proxy_failed",
      detail: String(error),
    });
  }
}
""", encoding="utf-8")

print("CLIENT_LATEST_DELIVERABLE_ROUTE_COMPILE_FIXED")