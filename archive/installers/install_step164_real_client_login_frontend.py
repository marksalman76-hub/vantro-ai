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
      return new NextResponse("Portal access is not configured.", { status: 503 });
    }

    if (ownerAccess !== expectedOwnerCode) {
      const loginUrl = new URL("/login", request.url);
      loginUrl.searchParams.set("next", pathname);
      return NextResponse.redirect(loginUrl);
    }

    return NextResponse.next();
  }

  if (isClientPath) {
    if (clientSession || ownerAccess === expectedOwnerCode) {
      return NextResponse.next();
    }

    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("next", pathname);
    return NextResponse.redirect(loginUrl);
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
      <section
        style={{
          width: "100%",
          maxWidth: 920,
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))",
          gap: 22,
        }}
      >
        <form
          method="POST"
          action="/api/client-login"
          style={{
            padding: 32,
            borderRadius: 22,
            background: "#0f172a",
            border: "1px solid rgba(148,163,184,.25)",
          }}
        >
          <p style={{ color: "#38bdf8", fontWeight: 800, letterSpacing: 1 }}>
            CLIENT LOGIN
          </p>

          <h1 style={{ marginTop: 10 }}>Access your workspace</h1>

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

        <form
          method="POST"
          action="/api/login"
          style={{
            padding: 32,
            borderRadius: 22,
            background: "#111827",
            border: "1px solid rgba(148,163,184,.25)",
          }}
        >
          <p style={{ color: "#f59e0b", fontWeight: 800, letterSpacing: 1 }}>
            OWNER / ADMIN ACCESS
          </p>

          <h1 style={{ marginTop: 10 }}>Owner access</h1>

          <input type="hidden" name="next" value="/admin" />

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
            Login as Owner
          </button>
        </form>
      </section>
    </main>
  );
}
''',

    FRONTEND / "src" / "app" / "api" / "client-login" / "route.ts": r'''import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL =
  process.env.BACKEND_URL || "https://ecommerce-ai-agent-platform-1.onrender.com";

export async function POST(request: NextRequest) {
  const formData = await request.formData();

  const email = String(formData.get("email") || "");
  const password = String(formData.get("password") || "");
  const next = String(formData.get("next") || "/client");

  const response = await fetch(`${BACKEND_URL}/client/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ email, password }),
  });

  const result = await response.json();

  if (!result.success || !result.session_token) {
    return new NextResponse("Client login failed.", { status: 401 });
  }

  const redirectUrl = new URL(next, request.url);
  const nextResponse = NextResponse.redirect(redirectUrl);

  nextResponse.cookies.set("client_session", result.session_token, {
    httpOnly: true,
    secure: true,
    sameSite: "strict",
    path: "/",
    maxAge: 60 * 60 * 8,
  });

  return nextResponse;
}
''',

    FRONTEND / "src" / "app" / "api" / "logout" / "route.ts": r'''import { NextResponse } from "next/server";

export async function GET() {
  const response = NextResponse.redirect(
    "https://ecommerce-ai-agent-platform.vercel.app/login"
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

print("STEP_164_REAL_CLIENT_LOGIN_FRONTEND_INSTALLED")
print("updated middleware")
print("updated login page")
print("added client login api")
print("updated logout api")
print("STEP_164_OK")