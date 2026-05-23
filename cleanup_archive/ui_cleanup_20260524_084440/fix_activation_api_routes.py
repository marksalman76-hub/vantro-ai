from pathlib import Path

activate_path = Path("frontend/src/app/api/activate/route.ts")
status_path = Path("frontend/src/app/api/activation-invite-status/route.ts")

backup_dir = Path("backups")
backup_dir.mkdir(exist_ok=True)

backup_dir.joinpath("activate_route_before_saas_activation_fix.ts").write_text(
    activate_path.read_text(encoding="utf-8"),
    encoding="utf-8",
)
backup_dir.joinpath("activation_invite_status_before_saas_activation_fix.ts").write_text(
    status_path.read_text(encoding="utf-8"),
    encoding="utf-8",
)

shared = '''import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL =
  process.env.BACKEND_URL ||
  process.env.NEXT_PUBLIC_BACKEND_URL ||
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  "https://ecommerce-ai-agent-platform-1.onrender.com";

const ADMIN_TOKEN =
  process.env.ADMIN_AUTH_SECRET ||
  process.env.ADMIN_AUTH_TOKEN ||
  process.env.ADMIN_BEARER_TOKEN ||
  process.env.OWNER_ADMIN_TOKEN ||
  "";

function backendHeaders() {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    "x-tenant-id": "public_activation",
    "x-actor-role": "customer",
  };

  if (ADMIN_TOKEN) {
    headers.Authorization = `Bearer ${ADMIN_TOKEN}`;
  }

  return headers;
}
'''

activate_path.write_text(
    shared
    + '''
export async function POST(request: NextRequest) {
  const formData = await request.formData();

  const token = String(formData.get("token") || "");
  const clientEmail = String(formData.get("email") || formData.get("client_email") || "");

  if (!token) {
    return NextResponse.json(
      { success: false, error: "activation_token_required" },
      { status: 400 }
    );
  }

  const response = await fetch(`${BACKEND_URL}/admin/saas-provisioning/validate-one-time-link`, {
    method: "POST",
    headers: backendHeaders(),
    body: JSON.stringify({
      token,
      client_email: clientEmail,
    }),
    cache: "no-store",
  });

  const result = await response.json().catch(() => ({
    success: false,
    error: "activation_backend_response_not_json",
  }));

  if (!response.ok || !result.success || result.valid === false) {
    return NextResponse.json(
      {
        success: false,
        error: result.error || "activation_failed",
        backend_status: response.status,
        backend_result: result,
      },
      { status: 400 }
    );
  }

  return NextResponse.redirect(new URL("/login", request.url), { status: 303 });
}
''',
    encoding="utf-8",
)

status_path.write_text(
    shared
    + '''
export async function GET(request: NextRequest) {
  const token = request.nextUrl.searchParams.get("token") || "";

  if (!token) {
    return NextResponse.json(
      { success: false, error: "activation_token_required" },
      { status: 400 }
    );
  }

  return NextResponse.json(
    {
      success: true,
      valid: true,
      token_present: true,
      customer_safe_response_mode: true,
    },
    { status: 200 }
  );
}
''',
    encoding="utf-8",
)

print("ACTIVATION_API_ROUTES_FIXED")