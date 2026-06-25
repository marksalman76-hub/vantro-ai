import { NextRequest, NextResponse } from "next/server";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.vantro.ai";

export async function GET(
  _request: NextRequest,
  { params }: { params: { token: string } }
) {
  try {
    const res = await fetch(`${API_URL}/api/auth/activate/${params.token}`, {
      method: "GET",
    });
    const data = await res.json();
    if (!res.ok) {
      const msg = res.status === 422 ? "Invalid input" : "Request failed";
      return NextResponse.json({ error: msg }, { status: res.status });
    }
    return NextResponse.json(data);
  } catch {
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}
