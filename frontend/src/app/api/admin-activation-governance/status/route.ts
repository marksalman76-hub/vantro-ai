import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL =
  process.env.BACKEND_URL ||
  process.env.NEXT_PUBLIC_BACKEND_URL ||
  "https://api.trance-formation.com.au";

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

export async function GET(request: NextRequest) {
  const bearer = getBearerToken(request);

  if (!bearer) {
    return NextResponse.json(
      {
        success: false,
        error: "auth_required",
        message: "Missing bearer token.",
        credential_values_exposed: false,
        customer_safe: true,
      },
      { status: 401 },
    );
  }

  const upstream = await fetch(`${BACKEND_URL}/activation-governance-admin-visibility/status`, {
    method: "GET",
    headers: {
      authorization: bearer,
      "content-type": "application/json",
    },
    cache: "no-store",
  });

  const text = await upstream.text();

  try {
    return NextResponse.json(JSON.parse(text), { status: upstream.status });
  } catch {
    return NextResponse.json(
      {
        success: false,
        error: "upstream_parse_failed",
        credential_values_exposed: false,
        customer_safe: true,
      },
      { status: upstream.status },
    );
  }
}
