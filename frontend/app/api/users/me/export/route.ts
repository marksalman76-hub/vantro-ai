import { NextRequest, NextResponse } from "next/server";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.vantro.ai";

export async function GET(request: NextRequest) {
  const token = request.cookies.get("access_token")?.value
    ?? request.headers.get("authorization")?.replace("Bearer ", "");
  if (!token) return NextResponse.json({ error: "Not authenticated" }, { status: 401 });

  try {
    const res = await fetch(`${API_URL}/api/users/me/export`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    const data = await res.text();
    return new NextResponse(data, {
      status: res.status,
      headers: {
        "Content-Type": "application/json",
        "Content-Disposition": "attachment; filename=vantro-data-export.json",
      },
    });
  } catch {
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}
