from pathlib import Path
from datetime import datetime
import re

ROOT = Path.cwd()
FRONTEND = ROOT / "frontend"
APP = FRONTEND / "src" / "app"
BACKUPS = ROOT / "backups"

BACKUPS.mkdir(exist_ok=True)
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_dir = BACKUPS / f"client_session_proxy_before_{stamp}"
backup_dir.mkdir(exist_ok=True)

def backup(path: Path):
    if path.exists():
        dest = backup_dir / path.relative_to(ROOT)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")

def write_file(path: Path, content: str):
    backup(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

PROXY_ROUTE = r'''import { NextRequest, NextResponse } from "next/server";

export const dynamic = "force-dynamic";

const BACKEND_URL =
  process.env.BACKEND_URL ||
  process.env.NEXT_PUBLIC_BACKEND_URL ||
  "https://api.trance-formation.com.au";

function getBearer(req: NextRequest): string {
  const auth = req.headers.get("authorization") || "";
  if (auth.toLowerCase().startsWith("bearer ")) return auth;

  const cookieToken =
    req.cookies.get("client_token")?.value ||
    req.cookies.get("token")?.value ||
    req.cookies.get("auth_token")?.value ||
    "";

  return cookieToken ? `Bearer ${cookieToken}` : "";
}

async function proxy(req: NextRequest, path: string) {
  const bearer = getBearer(req);

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    "x-actor-role": req.headers.get("x-actor-role") || "client",
    "x-tenant-id": req.headers.get("x-tenant-id") || req.cookies.get("tenant_id")?.value || "tenant_unknown",
  };

  if (bearer) headers.Authorization = bearer;

  const init: RequestInit = {
    method: req.method,
    headers,
    cache: "no-store",
  };

  if (!["GET", "HEAD"].includes(req.method)) {
    const text = await req.text();
    if (text) init.body = text;
  }

  const res = await fetch(`${BACKEND_URL}${path}`, init);
  const contentType = res.headers.get("content-type") || "application/json";
  const body = await res.text();

  return new NextResponse(body, {
    status: res.status,
    headers: {
      "Content-Type": contentType,
      "Cache-Control": "no-store",
    },
  });
}

export async function GET(req: NextRequest) {
  return proxy(req, "__BACKEND_PATH__");
}

export async function POST(req: NextRequest) {
  return proxy(req, "__BACKEND_PATH__");
}

export async function PUT(req: NextRequest) {
  return proxy(req, "__BACKEND_PATH__");
}

export async function PATCH(req: NextRequest) {
  return proxy(req, "__BACKEND_PATH__");
}
'''

routes = {
    "client-me": "/api/client-me",
    "client-business-profile": "/api/client-business-profile",
    "client-execution-matrix": "/api/client-execution-matrix",
    "run-agent": "/run-agent",
}

for name, backend_path in routes.items():
    write_file(
        APP / "api" / name / "route.ts",
        PROXY_ROUTE.replace("__BACKEND_PATH__", backend_path),
    )

LOGIN_ROUTE = r'''import { NextRequest, NextResponse } from "next/server";

export const dynamic = "force-dynamic";

const BACKEND_URL =
  process.env.BACKEND_URL ||
  process.env.NEXT_PUBLIC_BACKEND_URL ||
  "https://api.trance-formation.com.au";

function extractToken(payload: any): string {
  return (
    payload?.token ||
    payload?.access_token ||
    payload?.client_token ||
    payload?.auth_token ||
    payload?.session?.token ||
    payload?.data?.token ||
    payload?.data?.access_token ||
    ""
  );
}

function extractTenant(payload: any): string {
  return (
    payload?.tenant_id ||
    payload?.tenantId ||
    payload?.client?.tenant_id ||
    payload?.data?.tenant_id ||
    "tenant_unknown"
  );
}

export async function POST(req: NextRequest) {
  const body = await req.text();

  const candidates = ["/api/client-login", "/client-login", "/api/login", "/login"];
  let finalResponse: Response | null = null;
  let finalText = "";

  for (const path of candidates) {
    const res = await fetch(`${BACKEND_URL}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "x-actor-role": "client" },
      body,
      cache: "no-store",
    });

    finalResponse = res;
    finalText = await res.text();

    if (res.status !== 404) break;
  }

  let payload: any = {};
  try {
    payload = finalText ? JSON.parse(finalText) : {};
  } catch {
    payload = {};
  }

  const response = NextResponse.json(payload, {
    status: finalResponse?.status || 500,
    headers: { "Cache-Control": "no-store" },
  });

  const token = extractToken(payload);
  const tenantId = extractTenant(payload);

  if (token) {
    response.cookies.set("client_token", token, {
      httpOnly: false,
      secure: true,
      sameSite: "lax",
      path: "/",
      maxAge: 60 * 60 * 24 * 7,
    });
  }

  if (tenantId) {
    response.cookies.set("tenant_id", tenantId, {
      httpOnly: false,
      secure: true,
      sameSite: "lax",
      path: "/",
      maxAge: 60 * 60 * 24 * 7,
    });
  }

  return response;
}
'''

write_file(APP / "api" / "client-login" / "route.ts", LOGIN_ROUTE)

# Replace hardcoded direct backend calls in frontend source with same-origin API routes where safe.
for path in (FRONTEND / "src").rglob("*"):
    if path.suffix not in {".ts", ".tsx", ".js", ".jsx"}:
        continue

    text = path.read_text(encoding="utf-8")
    original = text

    text = text.replace("https://ecommerce-ai-agent-platform-1.onrender.com/api/client-me", "/api/client-me")
    text = text.replace("https://ecommerce-ai-agent-platform-1.onrender.com/api/client-business-profile", "/api/client-business-profile")
    text = text.replace("https://ecommerce-ai-agent-platform-1.onrender.com/api/client-execution-matrix", "/api/client-execution-matrix")
    text = text.replace("https://ecommerce-ai-agent-platform-1.onrender.com/run-agent", "/api/run-agent")

    text = text.replace("https://api.trance-formation.com.au/api/client-me", "/api/client-me")
    text = text.replace("https://api.trance-formation.com.au/api/client-business-profile", "/api/client-business-profile")
    text = text.replace("https://api.trance-formation.com.au/api/client-execution-matrix", "/api/client-execution-matrix")
    text = text.replace("https://api.trance-formation.com.au/run-agent", "/api/run-agent")

    if text != original:
        backup(path)
        path.write_text(text, encoding="utf-8")

print("CLIENT_PORTAL_LIVE_SESSION_PROXY_FIXED")
print(f"Backup folder: {backup_dir}")
print("Created/updated:")
for name in list(routes.keys()) + ["client-login"]:
    print(f"- frontend/src/app/api/{name}/route.ts")
print("Replaced direct backend calls with same-origin proxy calls where found.")