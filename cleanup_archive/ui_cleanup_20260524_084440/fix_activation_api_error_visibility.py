from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
FILE = ROOT / "frontend" / "src" / "app" / "api" / "activate" / "route.ts"
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUPS / f"activate_api_before_error_visibility_{stamp}.ts"
shutil.copy2(FILE, backup)

FILE.write_text(r'''import { NextRequest, NextResponse } from "next/server";

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

  const backendUrl = `${BACKEND_URL}/client/activate-account`;

  const response = await fetch(backendUrl, {
    method: "POST",
    headers: backendHeaders(),
    body: JSON.stringify({
      token,
      password,
      confirm_password: confirmPassword,
    }),
  });

  const responseText = await response.text();
  let result: any = null;

  try {
    result = JSON.parse(responseText);
  } catch {
    return NextResponse.json(
      {
        success: false,
        error: "activation_backend_response_not_json",
        backend_status: response.status,
        backend_url: backendUrl,
        backend_response_preview: responseText.slice(0, 300),
      },
      { status: 400 }
    );
  }

  if (!response.ok || !result.success) {
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
''', encoding="utf-8")

print("ACTIVATION_API_ERROR_VISIBILITY_FIXED")
print(f"Backup: {backup}")