import { NextRequest, NextResponse } from "next/server";

function backendBase() {
  return process.env.BACKEND_URL || process.env.NEXT_PUBLIC_BACKEND_URL || "http://127.0.0.1:8000";
}

export async function GET(
  _request: NextRequest,
  context: { params: Promise<{ plan: string }> }
) {
  const { plan } = await context.params;

  const res = await fetch(`${backendBase()}/signup-agent-selection/options/${encodeURIComponent(plan)}`, {
    method: "GET",
    cache: "no-store",
  });

  const data = await res.json();
  return NextResponse.json(data, { status: res.status });
}
