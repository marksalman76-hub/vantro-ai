import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.BACKEND_URL || process.env.NEXT_PUBLIC_BACKEND_URL || "https://api.trance-formation.com.au";

function getBearerToken(request: NextRequest): string | null {
  const authHeader = request.headers.get("authorization");
  if (authHeader && authHeader.toLowerCase().startsWith("bearer ")) {
    return authHeader;
  }

  const adminToken = process.env.ADMIN_PLATFORM_TOKEN;
  if (adminToken) {
    return `Bearer ${adminToken}`;
  }

  return null;
}

export async function POST(request: NextRequest) {
  const bearer = getBearerToken(request);

  if (!bearer) {
    return NextResponse.json(
      {
        success: false,
        error: "auth_required",
        message: "Missing bearer token.",
      },
      { status: 401 },
    );
  }

  const body = await request.text();

  const upstream = await fetch(`${BACKEND_URL}/signup-locked-activation/draft`, {
    method: "POST",
    headers: {
      authorization: bearer,
      "content-type": "application/json",
    },
    body,
    cache: "no-store",
  });

  const text = await upstream.text();

  try {
    return NextResponse.json(JSON.parse(text), { status: upstream.status });
  } catch {
    return new NextResponse(text, {
      status: upstream.status,
      headers: { "content-type": "application/json" },
    });
  }
}
