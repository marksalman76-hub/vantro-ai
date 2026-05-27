import { NextRequest, NextResponse } from "next/server";

function backendBase() {
  return process.env.BACKEND_URL || process.env.NEXT_PUBLIC_BACKEND_URL || "http://127.0.0.1:8000";
}

export async function POST(request: NextRequest) {
  const body = await request.json().catch(() => ({}));

  const res = await fetch(`${backendBase()}/signup-agent-selection/activation-packet`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    cache: "no-store",
    body: JSON.stringify(body),
  });

  const data = await res.json();
  return NextResponse.json(data, { status: res.status });
}
