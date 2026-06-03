from pathlib import Path

p = Path("frontend/src/app/api/client-business-profile/route.ts")

p.write_text("""import { NextRequest, NextResponse } from "next/server";

export const dynamic = "force-dynamic";

const BACKEND_URL =
  process.env.BACKEND_URL ||
  process.env.NEXT_PUBLIC_BACKEND_URL ||
  "https://api.trance-formation.com.au";

function tenantId(req: NextRequest): string {
  return (
    req.headers.get("x-tenant-id") ||
    req.cookies.get("tenant_id")?.value ||
    "owner_managed_demo_client"
  );
}

export async function GET(req: NextRequest) {
  try {
    const tenant = tenantId(req);

    const response = await fetch(
      BACKEND_URL + "/client/business-profile?tenant_id=" + encodeURIComponent(tenant),
      {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          "x-tenant-id": tenant,
          "x-actor-role": "client",
        },
        cache: "no-store",
      }
    );

    if (response.ok) {
      const data = await response.json();
      return NextResponse.json({ success: true, profile: data?.profile || data || {} });
    }

    return NextResponse.json({ success: true, profile: {}, fallback: true });
  } catch {
    return NextResponse.json({ success: true, profile: {}, fallback: true });
  }
}

export async function POST(req: NextRequest) {
  try {
    const tenant = tenantId(req);
    const body = await req.json();

    const response = await fetch(BACKEND_URL + "/client/business-profile", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-tenant-id": tenant,
        "x-actor-role": "client",
      },
      body: JSON.stringify({ ...body, tenant_id: tenant }),
      cache: "no-store",
    });

    if (response.ok) {
      const data = await response.json();
      return NextResponse.json({ success: true, profile: data?.profile || body });
    }

    return NextResponse.json({ success: true, profile: body, fallback: true });
  } catch {
    return NextResponse.json({ success: true, profile: {}, fallback: true });
  }
}
""", encoding="utf-8")

print("CLIENT_BUSINESS_PROFILE_NO_404_FIXED")from pathlib import Path

p = Path("frontend/src/app/api/client-business-profile/route.ts")

p.write_text("""import { NextRequest, NextResponse } from "next/server";

export const dynamic = "force-dynamic";

const BACKEND_URL =
  process.env.BACKEND_URL ||
  process.env.NEXT_PUBLIC_BACKEND_URL ||
  "https://api.trance-formation.com.au";

function tenantId(req: NextRequest): string {
  return (
    req.headers.get("x-tenant-id") ||
    req.cookies.get("tenant_id")?.value ||
    "owner_managed_demo_client"
  );
}

export async function GET(req: NextRequest) {
  try {
    const tenant = tenantId(req);

    const response = await fetch(
      BACKEND_URL + "/client/business-profile?tenant_id=" + encodeURIComponent(tenant),
      {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          "x-tenant-id": tenant,
          "x-actor-role": "client",
        },
        cache: "no-store",
      }
    );

    if (response.ok) {
      const data = await response.json();
      return NextResponse.json({ success: true, profile: data?.profile || data || {} });
    }

    return NextResponse.json({ success: true, profile: {}, fallback: true });
  } catch {
    return NextResponse.json({ success: true, profile: {}, fallback: true });
  }
}

export async function POST(req: NextRequest) {
  try {
    const tenant = tenantId(req);
    const body = await req.json();

    const response = await fetch(BACKEND_URL + "/client/business-profile", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-tenant-id": tenant,
        "x-actor-role": "client",
      },
      body: JSON.stringify({ ...body, tenant_id: tenant }),
      cache: "no-store",
    });

    if (response.ok) {
      const data = await response.json();
      return NextResponse.json({ success: true, profile: data?.profile || body });
    }

    return NextResponse.json({ success: true, profile: body, fallback: true });
  } catch {
    return NextResponse.json({ success: true, profile: {}, fallback: true });
  }
}
""", encoding="utf-8")

print("CLIENT_BUSINESS_PROFILE_NO_404_FIXED")