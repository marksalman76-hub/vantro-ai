import { NextRequest, NextResponse } from "next/server";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.vantro.ai";

function getToken(request: NextRequest): string | null {
  return request.cookies.get("access_token")?.value
    ?? request.headers.get("authorization")?.replace("Bearer ", "")
    ?? null;
}

export async function GET(request: NextRequest) {
  const token = getToken(request);
  if (!token) return NextResponse.json({ error: "Not authenticated" }, { status: 401 });
  try {
    const res = await fetch(`${API_URL}/api/auth/me`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    const data = await res.json();
    return NextResponse.json(data, { status: res.status });
  } catch {
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}

export async function DELETE(request: NextRequest) {
  const token = getToken(request);
  if (!token) return NextResponse.json({ error: "Not authenticated" }, { status: 401 });
  try {
    const res = await fetch(`${API_URL}/api/users/me`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${token}` },
    });
    const data = await res.json();
    const response = NextResponse.json(data, { status: res.status });
    if (res.ok) response.cookies.delete("access_token");
    return response;
  } catch {
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}
