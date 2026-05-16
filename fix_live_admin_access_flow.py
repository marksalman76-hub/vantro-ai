from pathlib import Path
from datetime import datetime
import py_compile

ROOT = Path.cwd()
ADMIN_LOGIN_PAGE = ROOT / "frontend" / "src" / "app" / "admin-login" / "page.tsx"
ADMIN_API_DIR = ROOT / "frontend" / "src" / "app" / "api" / "admin-login"
ADMIN_LOGOUT_DIR = ROOT / "frontend" / "src" / "app" / "api" / "admin-logout"
MIDDLEWARE = ROOT / "frontend" / "src" / "middleware.ts"
TEST = ROOT / "test_live_admin_access_flow.py"
BACKUPS = ROOT / "backups"

BACKUPS.mkdir(parents=True, exist_ok=True)
ADMIN_API_DIR.mkdir(parents=True, exist_ok=True)
ADMIN_LOGOUT_DIR.mkdir(parents=True, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

for file in [ADMIN_LOGIN_PAGE, MIDDLEWARE, TEST]:
    if file.exists():
        backup = BACKUPS / f"{file.stem}_before_admin_access_flow_{timestamp}{file.suffix}"
        backup.write_text(file.read_text(encoding="utf-8"), encoding="utf-8")

ADMIN_LOGIN_ROUTE = ADMIN_API_DIR / "route.ts"
ADMIN_LOGOUT_ROUTE = ADMIN_LOGOUT_DIR / "route.ts"

ADMIN_LOGIN_PAGE.write_text(r'''
export default async function AdminLoginPage({
  searchParams,
}: {
  searchParams?: Promise<{ next?: string }>;
}) {
  const resolvedSearchParams = searchParams ? await searchParams : {};
  const nextPath = resolvedSearchParams.next || "/admin";

  return (
    <main
      style={{
        minHeight: "100vh",
        display: "grid",
        placeItems: "center",
        padding: 24,
        background: "#020617",
        color: "white",
        fontFamily:
          "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif",
      }}
    >
      <form
        method="POST"
        action="/api/admin-login"
        style={{
          width: "100%",
          maxWidth: 460,
          padding: 34,
          borderRadius: 24,
          background: "#111827",
          border: "1px solid rgba(245,158,11,.28)",
          boxShadow: "0 28px 90px rgba(0,0,0,.32)",
        }}
      >
        <p style={{ color: "#f59e0b", fontWeight: 800, letterSpacing: 1 }}>
          OWNER / ADMIN ACCESS
        </p>

        <h1 style={{ marginTop: 10, fontSize: 38, lineHeight: 1.1 }}>
          Admin control centre
        </h1>

        <input type="hidden" name="next" value={nextPath} />

        <label style={{ display: "block", marginTop: 20, marginBottom: 8 }}>
          Owner access code
        </label>

        <input
          name="access"
          type="password"
          placeholder="Owner access code"
          required
          style={{
            width: "100%",
            padding: 14,
            borderRadius: 10,
            border: "1px solid rgba(148,163,184,.35)",
          }}
        />

        <button
          type="submit"
          style={{
            width: "100%",
            marginTop: 20,
            padding: 14,
            borderRadius: 10,
            border: 0,
            background: "#f59e0b",
            color: "#111827",
            fontWeight: 800,
            cursor: "pointer",
          }}
        >
          Login as Owner/Admin
        </button>
      </form>
    </main>
  );
}
'''.lstrip(), encoding="utf-8")

ADMIN_LOGIN_ROUTE.write_text(r'''
import { NextRequest, NextResponse } from "next/server";

export const dynamic = "force-dynamic";

export async function GET(request: NextRequest) {
  return NextResponse.redirect(new URL("/admin-login", request.url), {
    status: 303,
  });
}

export async function POST(request: NextRequest) {
  const formData = await request.formData();
  const access = String(formData.get("access") || "");
  const next = String(formData.get("next") || "/admin");
  const expected = process.env.PORTAL_ACCESS_CODE;

  if (!expected || access !== expected) {
    return new NextResponse("Access denied.", { status: 401 });
  }

  const response = NextResponse.redirect(new URL(next, request.url), {
    status: 303,
  });

  response.cookies.set("portal_access", expected, {
    httpOnly: true,
    secure: true,
    sameSite: "lax",
    path: "/",
    maxAge: 60 * 60 * 8,
  });

  return response;
}
'''.lstrip(), encoding="utf-8")

ADMIN_LOGOUT_ROUTE.write_text(r'''
import { NextRequest, NextResponse } from "next/server";

export const dynamic = "force-dynamic";

function logout(request: NextRequest) {
  const response = NextResponse.redirect(new URL("/admin-login", request.url), {
    status: 303,
  });

  response.cookies.set("portal_access", "", {
    httpOnly: true,
    secure: true,
    sameSite: "lax",
    path: "/",
    maxAge: 0,
  });

  return response;
}

export async function GET(request: NextRequest) {
  return logout(request);
}

export async function POST(request: NextRequest) {
  return logout(request);
}
'''.lstrip(), encoding="utf-8")

MIDDLEWARE.write_text(r'''
import { NextRequest, NextResponse } from "next/server";

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  const publicPaths = [
    "/",
    "/login",
    "/admin-login",
    "/activate",
    "/api/login",
    "/api/logout",
    "/api/admin-login",
    "/api/admin-logout",
    "/api/client-login",
    "/api/client-me",
    "/api/activate",
  ];

  if (
    publicPaths.some((path) => pathname === path || pathname.startsWith(path + "/")) ||
    pathname.startsWith("/_next") ||
    pathname.startsWith("/favicon")
  ) {
    return NextResponse.next();
  }

  if (pathname.startsWith("/admin")) {
    const expected = process.env.PORTAL_ACCESS_CODE;
    const cookie = request.cookies.get("portal_access")?.value;

    if (!expected || cookie !== expected) {
      const loginUrl = new URL("/admin-login", request.url);
      loginUrl.searchParams.set("next", pathname);
      return NextResponse.redirect(loginUrl);
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
'''.lstrip(), encoding="utf-8")

TEST.write_text(r'''
from pathlib import Path
import subprocess

ROOT = Path.cwd()

admin_page = ROOT / "frontend" / "src" / "app" / "admin-login" / "page.tsx"
admin_login = ROOT / "frontend" / "src" / "app" / "api" / "admin-login" / "route.ts"
admin_logout = ROOT / "frontend" / "src" / "app" / "api" / "admin-logout" / "route.ts"
middleware = ROOT / "frontend" / "src" / "middleware.ts"

combined = "\n".join([
    admin_page.read_text(encoding="utf-8", errors="ignore"),
    admin_login.read_text(encoding="utf-8", errors="ignore"),
    admin_logout.read_text(encoding="utf-8", errors="ignore"),
    middleware.read_text(encoding="utf-8", errors="ignore"),
])

checks = {
    "admin_login_page_uses_dedicated_route": 'action="/api/admin-login"' in combined,
    "admin_login_post_present": "export async function POST" in admin_login.read_text(encoding="utf-8"),
    "admin_login_get_present": "export async function GET" in admin_login.read_text(encoding="utf-8"),
    "admin_logout_get_present": "export async function GET" in admin_logout.read_text(encoding="utf-8"),
    "admin_logout_post_present": "export async function POST" in admin_logout.read_text(encoding="utf-8"),
    "redirect_303_present": "status: 303" in combined,
    "middleware_allows_admin_login_api": "/api/admin-login" in combined,
    "middleware_protects_admin": 'pathname.startsWith("/admin")' in combined,
    "portal_access_code_used": "PORTAL_ACCESS_CODE" in combined,
}

print("LIVE_ADMIN_ACCESS_FLOW_FIX_RESULTS")
for name, passed in checks.items():
    print(name, passed)

failed = [name for name, passed in checks.items() if not passed]

print("RUNNING_FRONTEND_BUILD")
build = subprocess.run(["npm.cmd", "run", "build"], cwd=str(ROOT / "frontend"), text=True)
print("frontend_build_exit_code", build.returncode)

if build.returncode != 0:
    failed.append("frontend_build")

if failed:
    print("FAILED", failed)
    raise SystemExit(1)

print("LIVE_ADMIN_ACCESS_FLOW_FIX_OK")
'''.lstrip(), encoding="utf-8")

py_compile.compile(str(TEST), doraise=True)

print("LIVE_ADMIN_ACCESS_FLOW_FIX_INSTALLED")
print(f"Updated: {ADMIN_LOGIN_PAGE}")
print(f"Updated: {ADMIN_LOGIN_ROUTE}")
print(f"Updated: {ADMIN_LOGOUT_ROUTE}")
print(f"Updated: {MIDDLEWARE}")
print(f"Created/updated: {TEST}")