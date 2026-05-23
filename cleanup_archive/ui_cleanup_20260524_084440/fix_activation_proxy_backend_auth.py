from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

activate_api = ROOT / "frontend" / "src" / "app" / "api" / "activate" / "route.ts"
status_dir = ROOT / "frontend" / "src" / "app" / "api" / "activation-invite-status"
status_file = status_dir / "route.ts"
activate_page = ROOT / "frontend" / "src" / "app" / "activate" / "page.tsx"

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

for file in [activate_api, activate_page]:
    shutil.copy2(file, BACKUPS / f"{file.stem}_before_activation_proxy_{stamp}{file.suffix}")

activate_api.write_text(r'''import { NextRequest, NextResponse } from "next/server";

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
    "x-tenant-id": "owner",
    "x-actor-role": "owner",
  };

  if (ADMIN_TOKEN) {
    headers.Authorization = `Bearer ${ADMIN_TOKEN}`;
  }

  return headers;
}

export async function POST(request: NextRequest) {
  const formData = await request.formData();

  const token = String(formData.get("token") || "");
  const password = String(formData.get("password") || "");
  const confirmPassword = String(formData.get("confirm_password") || "");

  const response = await fetch(`${BACKEND_URL}/client/activate-account`, {
    method: "POST",
    headers: backendHeaders(),
    body: JSON.stringify({
      token,
      password,
      confirm_password: confirmPassword,
    }),
  });

  const result = await response.json().catch(() => ({
    success: false,
    error: "activation_backend_response_not_json",
  }));

  if (!result.success) {
    return new NextResponse(`Activation failed: ${result.error}`, {
      status: 400,
    });
  }

  return NextResponse.redirect(new URL("/login", request.url));
}
''', encoding="utf-8")

status_dir.mkdir(parents=True, exist_ok=True)
status_file.write_text(r'''import { NextRequest, NextResponse } from "next/server";

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
    "x-tenant-id": "owner",
    "x-actor-role": "owner",
  };

  if (ADMIN_TOKEN) {
    headers.Authorization = `Bearer ${ADMIN_TOKEN}`;
  }

  return headers;
}

export async function GET(request: NextRequest) {
  const token = request.nextUrl.searchParams.get("token") || "";

  if (!token) {
    return NextResponse.json(
      { success: false, error: "activation_token_required" },
      { status: 400 }
    );
  }

  const response = await fetch(
    `${BACKEND_URL}/client/activation-invite-status?token=${encodeURIComponent(token)}`,
    {
      cache: "no-store",
      headers: backendHeaders(),
    }
  );

  const data = await response.json().catch(() => ({
    success: false,
    error: "activation_status_backend_response_not_json",
  }));

  return NextResponse.json(data, { status: response.status });
}
''', encoding="utf-8")

page_text = activate_page.read_text(encoding="utf-8")
page_text = page_text.replace(
    '''const BACKEND_URL =
  process.env.BACKEND_URL || "https://ecommerce-ai-agent-platform-1.onrender.com";

''',
    ""
)
page_text = page_text.replace(
    '''    const response = await fetch(
      `${BACKEND_URL}/client/activation-invite-status?token=${encodeURIComponent(
        token
      )}`,
      { cache: "no-store" }
    );''',
    '''    const response = await fetch(
      `${process.env.NEXT_PUBLIC_APP_URL || ""}/api/activation-invite-status?token=${encodeURIComponent(
        token
      )}`,
      { cache: "no-store" }
    );'''
)

activate_page.write_text(page_text, encoding="utf-8")

print("ACTIVATION_PROXY_BACKEND_AUTH_FIXED")
print("Updated: frontend\\src\\app\\api\\activate\\route.ts")
print("Created: frontend\\src\\app\\api\\activation-invite-status\\route.ts")
print("Updated: frontend\\src\\app\\activate\\page.tsx")