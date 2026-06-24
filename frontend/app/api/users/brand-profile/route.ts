import { NextRequest, NextResponse } from "next/server";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.vantro.ai";

async function proxy(request: NextRequest, method: "GET" | "PUT") {
  const token = request.headers.get("authorization");
  if (!token) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  try {
    const init: RequestInit = {
      method,
      headers: {
        Authorization: token,
        "Content-Type": "application/json",
      },
    };
    if (method === "PUT") init.body = await request.text();

    const res = await fetch(`${API_URL}/api/users/brand-profile`, init);
    const data = await res.json();
    return NextResponse.json(data, { status: res.status });
  } catch {
    return NextResponse.json({ error: "Backend unavailable" }, { status: 502 });
  }
}

export async function GET(request: NextRequest) {
  return proxy(request, "GET");
}

export async function PUT(request: NextRequest) {
  return proxy(request, "PUT");
}
