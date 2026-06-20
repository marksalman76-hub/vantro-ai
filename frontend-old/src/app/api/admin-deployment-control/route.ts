import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL =
  process.env.BACKEND_URL ||
  process.env.NEXT_PUBLIC_BACKEND_URL ||
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  "https://api.trance-formation.com.au";

const ADMIN_TOKEN =
  process.env.ADMIN_PLATFORM_TOKEN ||
  process.env.ADMIN_AUTH_SECRET ||
  process.env.ADMIN_AUTH_TOKEN ||
  process.env.ADMIN_BEARER_TOKEN ||
  process.env.OWNER_ADMIN_TOKEN ||
  "";

function safePath(path: string) {
  if (!path || typeof path !== "string") return "";

  if (path === "/run-agent") {
    return path;
  }

  if (path.startsWith("/admin/deployment-control/")) {
    return path;
  }

  const exactAdminReviewPaths = [
    "/admin/manual-review/list",
    "/admin/dead-letter/list",
    "/admin/manual-review/summary",
    "/admin/manual-review/decision",
    "/admin/dead-letter/resolve",
  ];

  for (const allowed of exactAdminReviewPaths) {
    if (path === allowed || path.startsWith(`${allowed}?`)) {
      return path;
    }
  }

  return "";
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json().catch(() => ({}));
    const path = safePath(body.path || "");
    const method = String(body.method || "POST").toUpperCase();
    const payload = body.payload || undefined;
    const optionalDashboardCall = body.optional === true && method === "GET";

    if (!path) {
      return NextResponse.json(
        { success: false, error: "invalid_admin_deployment_path" },
        { status: 400 }
      );
    }

    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      "x-tenant-id": "owner",
      "x-actor-role": "owner",
    };

    const requestId =
      request.headers.get("x-request-id") ||
      `admin-${Date.now()}-${Math.random().toString(36).slice(2)}`;

    const idempotencyKey =
      request.headers.get("x-idempotency-key") || requestId;

    headers["x-request-id"] = requestId;
    headers["x-idempotency-key"] = idempotencyKey;
    headers["x-csrf-token"] = requestId;

    if (ADMIN_TOKEN) {
      headers.Authorization = `Bearer ${ADMIN_TOKEN}`;
      headers["x-admin-token"] = ADMIN_TOKEN;
    }

    const frontendOrigin =
      process.env.FRONTEND_PUBLIC_URL ||
      process.env.FRONTEND_URL ||
      process.env.NEXT_PUBLIC_FRONTEND_URL ||
      "https://app.trance-formation.com.au";

    headers.Origin = frontendOrigin;
    headers.Referer = `${frontendOrigin}/admin`;

    const response = await fetch(`${BACKEND_URL}${path}`, {
      method,
      cache: "no-store",
      headers,
      body: method === "GET" ? undefined : JSON.stringify(payload || {}),
    });

    const data = await response.json().catch(() => ({
      success: false,
      error: "backend_response_not_json",
      status: response.status,
    }));

    if (optionalDashboardCall && !response.ok) {
      return NextResponse.json(
        {
          success: false,
          status: "optional_dashboard_data_unavailable",
          backend_status: response.status,
          data,
          customer_safe: true,
          credential_values_exposed: false,
        },
        { status: 200 }
      );
    }

    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    return NextResponse.json(
      {
        success: false,
        error: "admin_deployment_proxy_failed",
        message: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 500 }
    );
  }
}
