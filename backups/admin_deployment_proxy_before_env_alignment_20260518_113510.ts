import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL =
  process.env.BACKEND_URL ||
  process.env.NEXT_PUBLIC_BACKEND_URL ||
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  "https://ecommerce-ai-agent-platform-1.onrender.com";

const ADMIN_TOKEN =
  process.env.ADMIN_AUTH_TOKEN ||
  process.env.ADMIN_BEARER_TOKEN ||
  process.env.OWNER_ADMIN_TOKEN ||
  "";

function safePath(path: string) {
  if (!path || typeof path !== "string") return "";
  if (!path.startsWith("/admin/deployment-control/")) return "";
  return path;
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json().catch(() => ({}));
    const path = safePath(body.path || "");
    const method = String(body.method || "POST").toUpperCase();
    const payload = body.payload || undefined;

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

    if (ADMIN_TOKEN) {
      headers.Authorization = `Bearer ${ADMIN_TOKEN}`;
    }

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
