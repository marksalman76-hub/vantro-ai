```ts
import { NextRequest, NextResponse } from "next/server";

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

  return cookieToken ? `Bearer ${cookieToken}` : "";
}

export async function GET(req: NextRequest) {
  try {
    const bearer = getBearer(req);

    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      "x-actor-role":
        req.headers.get("x-actor-role") || "client",
      "x-tenant-id":
        req.headers.get("x-tenant-id") ||
        req.cookies.get("tenant_id")?.value ||
        "client_demo_001",
    };

    if (bearer) {
      headers.Authorization = bearer;
    }

    const response = await fetch(
      `${BACKEND_URL}/client/execution-events`,
      {
        method: "GET",
        headers,
        cache: "no-store",
      }
    );

    const data = await response.json();

    const latest =
      data?.events?.[0] ||
      data?.executions?.[0] ||
      data?.records?.[0] ||
      null;

    return NextResponse.json({
      success: true,
      execution: latest,
      deliverable:
        latest?.deliverable ||
        latest?.result ||
        latest?.output ||
        latest?.execution_result ||
        null,
    });
  } catch (error) {
    return NextResponse.json({
      success: false,
      error: "client_latest_deliverable_proxy_failed",
      detail: String(error),
    });
  }
}
```
