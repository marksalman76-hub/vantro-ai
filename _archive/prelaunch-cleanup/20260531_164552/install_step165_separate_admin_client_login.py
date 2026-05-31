from pathlib import Path

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
FRONTEND = ROOT / "frontend"

FILES = {
    FRONTEND / "middleware.ts": r'''import { NextRequest, NextResponse } from "next/server";

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  const isAdminPath = pathname === "/admin" || pathname.startsWith("/admin/");
  const isClientPath = pathname === "/client" || pathname.startsWith("/client/");

  if (!isAdminPath && !isClientPath) {
    return NextResponse.next();
  }

  const expectedOwnerCode = process.env.PORTAL_ACCESS_CODE;
  const ownerAccess = request.cookies.get("portal_access")?.value;
  const clientSession = request.cookies.get("client_session")?.value;

  if (isAdminPath) {
    if (!expectedOwnerCode) {
      return new NextResponse("Admin access is not configured.", { status: 503 });
    }

    if (ownerAccess !== expectedOwnerCode) {
      const loginUrl = new URL("/admin-login", request.url);
      loginUrl.searchParams.set("next", pathname);
      return NextResponse.redirect(loginUrl);
    }

    return NextResponse.next();
  }

  if (isClientPath) {
    if (!clientSession) {
      const loginUrl = new URL("/login", request.url);
      loginUrl.searchParams.set("next", pathname);
      return NextResponse.redirect(loginUrl);
    }

    return NextResponse.next();
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/admin/:path*", "/client/:path*"],
};
''',

    FRONTEND / "src" / "app" / "login" / "page.tsx": r'''export default async function LoginPage({
  searchParams,
}: {
  searchParams?: Promise<{ next?: string }>;
}) {
  const resolvedSearchParams = searchParams ? await searchParams : {};
  const nextPath = resolvedSearchParams.next || "/client";

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
        action="/api/client-login"
        style={{
          width: "100%",
          maxWidth: 460,
          padding: 34,
          borderRadius: 24,
          background: "#0f172a",
          border: "1px solid rgba(148,163,184,.25)",
          boxShadow: "0 28px 90px rgba(0,0,0,.32)",
        }}
      >
        <p style={{ color: "#38bdf8", fontWeight: 800, letterSpacing: 1 }}>
          CLIENT LOGIN
        </p>

        <h1 style={{ marginTop: 10, fontSize: 38, lineHeight: 1.1 }}>
          Access your workspace
        </h1>

        <input type="hidden" name="next" value={nextPath} />

        <label style={{ display: "block", marginTop: 20, marginBottom: 8 }}>
          Email
        </label>
        <input
          name="email"
          type="email"
          placeholder="client@example.com"
          required
          style={{
            width: "100%",
            padding: 14,
            borderRadius: 10,
            border: "1px solid rgba(148,163,184,.35)",
          }}
        />

        <label style={{ display: "block", marginTop: 16, marginBottom: 8 }}>
          Password
        </label>
        <input
          name="password"
          type="password"
          placeholder="Password"
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
            background: "#2563eb",
            color: "white",
            fontWeight: 800,
            cursor: "pointer",
          }}
        >
          Login as Client
        </button>
      </form>
    </main>
  );
}
''',

    FRONTEND / "src" / "app" / "admin-login" / "page.tsx": r'''export default async function AdminLoginPage({
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
        action="/api/login"
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
''',

    FRONTEND / "src" / "app" / "api" / "logout" / "route.ts": r'''import { NextRequest, NextResponse } from "next/server";

export async function GET(request: NextRequest) {
  const next = request.nextUrl.searchParams.get("next") || "/login";

  const response = NextResponse.redirect(
    new URL(next, "https://ecommerce-ai-agent-platform.vercel.app")
  );

  response.cookies.set("portal_access", "", {
    path: "/",
    expires: new Date(0),
  });

  response.cookies.set("client_session", "", {
    path: "/",
    expires: new Date(0),
  });

  return response;
}
''',
}

for path, content in FILES.items():
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

print("STEP_165_SEPARATE_ADMIN_CLIENT_LOGIN_INSTALLED")
print("client_login=/login")
print("admin_login=/admin-login")
print("admin_path=/admin")
print("client_path=/client")
print("STEP_165_OK")