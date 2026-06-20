import { NextRequest, NextResponse } from "next/server";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || process.env.API_BASE_URL || "http://127.0.0.1:8000";

export async function POST(request: NextRequest) {
  const body = await request.json().catch(() => ({}));

  const response = await fetch(`${API_BASE}/client/integrations/test`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-tenant-id": request.headers.get("x-tenant-id") || "client_demo_001",
      "x-actor-role": request.headers.get("x-actor-role") || "customer",
      "authorization": request.headers.get("authorization") || "",
    },
    body: JSON.stringify(body),
    cache: "no-store",
  });

  const data = await response.json().catch(() => ({ success: false, error: "invalid_backend_response" }));
  return NextResponse.json(data, { status: response.status });
}
