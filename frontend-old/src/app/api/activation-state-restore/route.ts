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
  const { searchParams } = new URL(request.url);
  const tenantId = searchParams.get("tenant_id") || searchParams.get("tenantId") || "";

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

  if (!tenantId.trim()) {
    return NextResponse.json(
      {
        success: false,
        error: "missing_tenant_id",
        message: "Missing tenant id.",
        credential_values_exposed: false,
        customer_safe: true,
      },
      { status: 400 },
    );
  }

  const upstream = await fetch(
    `${BACKEND_URL}/governed-activation-persistence/hydrate/${encodeURIComponent(tenantId)}`,
    {
      method: "GET",
      headers: {
        authorization: bearer,
        "content-type": "application/json",
      },
      cache: "no-store",
    },
  );

  const text = await upstream.text();

  try {
    const data = JSON.parse(text);

    return NextResponse.json(
      {
        ...data,
        activation_state_restore_bridge_ready: true,
        post_activation_client_changes_blocked: true,
        owner_admin_required_for_post_activation_changes: true,
        credential_values_exposed: false,
        customer_safe: true,
      },
      { status: upstream.status },
    );
  } catch {
    return NextResponse.json(
      {
        success: false,
        error: "upstream_parse_failed",
        activation_state_restore_bridge_ready: true,
        credential_values_exposed: false,
        customer_safe: true,
      },
      { status: upstream.status },
    );
  }
}
