from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

ADMIN_PAGE = ROOT / "frontend" / "src" / "app" / "admin" / "page.tsx"
PROXY_DIR = ROOT / "frontend" / "src" / "app" / "api" / "admin-deployment-control"
PROXY_FILE = PROXY_DIR / "route.ts"

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# Backup admin page
admin_backup = BACKUPS / f"admin_page_before_deployment_proxy_{timestamp}.tsx"
shutil.copy2(ADMIN_PAGE, admin_backup)

text = ADMIN_PAGE.read_text(encoding="utf-8")

# Replace localhost registry list calls
text = text.replace(
    'const response = await fetch("http://127.0.0.1:8000/admin/deployment-control/list?limit=25", {',
    'const response = await fetch("/api/admin-deployment-control", {',
)

text = text.replace(
    '        cache: "no-store",\n        headers: { "x-tenant-id": "owner", "x-actor-role": "owner" },',
    '        method: "POST",\n        cache: "no-store",\n        headers: { "Content-Type": "application/json" },\n        body: JSON.stringify({ path: "/admin/deployment-control/list?limit=25", method: "GET" }),',
)

# Replace localhost summary calls
text = text.replace(
    'const response = await fetch("http://127.0.0.1:8000/admin/deployment-control/summary", {',
    'const response = await fetch("/api/admin-deployment-control", {',
)

text = text.replace(
    '        cache: "no-store",\n        headers: { "x-tenant-id": "owner", "x-actor-role": "owner" },',
    '        method: "POST",\n        cache: "no-store",\n        headers: { "Content-Type": "application/json" },\n        body: JSON.stringify({ path: "/admin/deployment-control/summary", method: "GET" }),',
    1,
)

# Replace callDeploymentControl fetch target/body
text = text.replace(
    'const response = await fetch(`http://127.0.0.1:8000${path}`, {',
    'const response = await fetch("/api/admin-deployment-control", {',
)

text = text.replace(
    '''        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "x-tenant-id": "owner",
          "x-actor-role": "owner",
        },
        body: JSON.stringify(payload),''',
    '''        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ path, method: "POST", payload }),'''
)

ADMIN_PAGE.write_text(text, encoding="utf-8")

# Create proxy route
PROXY_DIR.mkdir(parents=True, exist_ok=True)

proxy_code = r'''import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL =
  process.env.BACKEND_URL ||
  process.env.NEXT_PUBLIC_BACKEND_URL ||
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  "https://ecommerce-ai-agent-platform-1.onrender.com";

const ADMIN_TOKEN =
  process.env.ADMIN_AUTH_TOKEN ||
  process.env.ADMIN_BEARER_TOKEN ||
  process.env.OWNER_ADMIN_TOKEN ||
  "";

function safePath(path: string) {
  if (!path || typeof path !== "string") return "";
  if (!path.startsWith("/admin/deployment-control/")) return "";
  return path;
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json().catch(() => ({}));
    const path = safePath(body.path || "");
    const method = String(body.method || "POST").toUpperCase();
    const payload = body.payload || undefined;

    if (!path) {
      return NextResponse.json(
        { success: false, error: "invalid_admin_deployment_path" },
        { status: 400 }
      );
    }

    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      "x-tenant-id": "owner",
      "x-actor-role": "owner",
    };

    if (ADMIN_TOKEN) {
      headers.Authorization = `Bearer ${ADMIN_TOKEN}`;
    }

    const response = await fetch(`${BACKEND_URL}${path}`, {
      method,
      cache: "no-store",
      headers,
      body: method === "GET" ? undefined : JSON.stringify(payload || {}),
    });

    const data = await response.json().catch(() => ({
      success: false,
      error: "backend_response_not_json",
      status: response.status,
    }));

    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    return NextResponse.json(
      {
        success: false,
        error: "admin_deployment_proxy_failed",
        message: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 500 }
    );
  }
}
'''

PROXY_FILE.write_text(proxy_code, encoding="utf-8")

print("ADMIN_DEPLOYMENT_CONTROL_PROXY_INSTALLED")
print(f"Backup: {admin_backup}")
print("Created: frontend\\src\\app\\api\\admin-deployment-control\\route.ts")
print("Updated: frontend\\src\\app\\admin\\page.tsx")