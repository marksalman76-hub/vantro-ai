import { NextRequest, NextResponse } from "next/server";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.vantro.ai";

export async function POST(
  request: NextRequest,
  { params }: { params: { agentId: string } }
) {
  const token = request.headers.get("authorization") || "";
  try {
    const body = await request.text();
    const res = await fetch(`${API_URL}/api/admin/agents/${params.agentId}/run`, {
      method: "POST",
      headers: { Authorization: token, "Content-Type": "application/json" },
      body,
    });
    const data = await res.json();
    return NextResponse.json(data, { status: res.status });
  } catch {
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}
