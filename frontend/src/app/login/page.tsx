export const dynamic = "force-dynamic";
export const revalidate = 0;

import LoginSupportClient from "./support-client";

type LoginPageProps = {
  searchParams?: Promise<{ next?: string; error?: string; activated?: string }>;
};

export default async function LoginPage({ searchParams }: LoginPageProps) {
  const params = searchParams ? await searchParams : {};
  const nextPath = params.next || "/client";
  const error = params.error;
  const activated = params.activated === "1";

  return (
    <main style={{
      minHeight: "100vh",
      display: "grid",
      placeItems: "center",
      padding: 24,
      background: "radial-gradient(circle at top right, rgba(99,91,255,.22) 0, transparent 34%), radial-gradient(circle at bottom left, rgba(20,184,166,.16) 0, transparent 30%), linear-gradient(135deg, #050816 0%, #0b1020 55%, #050816 100%)",
      color: "#f8fafc",
      fontFamily: "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif",
      position: "relative",
      overflow: "hidden",
    }}>
      <form action="/api/client-login" method="POST" style={{
        width: "100%",
        maxWidth: 480,
        padding: 36,
        borderRadius: 28,
        background: "linear-gradient(180deg, rgba(15,23,42,.92), rgba(7,16,34,.96))",
        border: "1px solid rgba(148,163,184,.22)",
        boxShadow: "0 30px 90px rgba(0,0,0,.38)",
      }}>
        <p style={{ color: "#a78bfa", fontWeight: 900, letterSpacing: 1, fontSize: 12 }}>CLIENT PORTAL</p>
        <h1 style={{ margin: "12px 0", fontSize: 34, lineHeight: 1.05, letterSpacing: "-.04em" }}>Access your workspace</h1>
        <p style={{ color: "#cbd5e1", lineHeight: 1.7, marginTop: 0 }}>
          Sign in to manage your AI agents, approvals, outputs, and workspace activity.
        </p>

        {activated && (
          <div style={{ marginTop: 18, padding: 14, borderRadius: 16, background: "rgba(34,197,94,.12)", border: "1px solid rgba(34,197,94,.32)", color: "#86efac" }}>
            Your account is activated. Sign in with the password you created.
          </div>
        )}

        {error && (
          <div style={{ marginTop: 18, padding: 14, borderRadius: 16, background: "rgba(239,68,68,.12)", border: "1px solid rgba(239,68,68,.32)", color: "#fca5a5" }}>
            Login failed. Check the email and password, then try again.
          </div>
        )}

        <input type="hidden" name="next" value={nextPath} />

        <label style={labelStyle}>Email</label>
        <input name="email" type="email" placeholder="client@example.com" required style={inputStyle} />

        <label style={labelStyle}>Password</label>
        <input name="password" type="password" placeholder="Password" required style={inputStyle} />

        <div style={{ marginTop: 12, display: "flex", justifyContent: "space-between", alignItems: "center", gap: 12, flexWrap: "wrap" }}>
          <label style={{ display: "flex", alignItems: "center", gap: 8, color: "#cbd5e1", fontSize: 13, fontWeight: 700 }}>
            <input type="checkbox" name="remember" style={{ accentColor: "#8b5cf6" }} />
            Remember me
          </label>
          <a href="/support-request?topic=password-reset" style={{ color: "#c4b5fd", fontSize: 13, fontWeight: 800, textDecoration: "underline" }}>
            Reset password
          </a>
        </div>

        <button type="submit" style={buttonStyle}>Login to workspace</button>

        <p style={{ margin: "18px 0 0", color: "#cbd5e1", textAlign: "center", fontSize: 13 }}>
          Need access? <a href="/support-request" style={{ color: "#c4b5fd", fontWeight: 800 }}>Contact support</a>
        </p>
      </form>

      <LoginSupportClient />
    </main>
  );
}

const labelStyle: React.CSSProperties = { display: "block", marginTop: 18, marginBottom: 8, color: "#e2e8f0", fontWeight: 800 };
const inputStyle: React.CSSProperties = { width: "100%", padding: 14, borderRadius: 14, border: "1px solid rgba(148,163,184,.26)", background: "rgba(3,10,24,.72)", color: "#f8fafc", fontSize: 14, boxSizing: "border-box", outline: "none" };
const buttonStyle: React.CSSProperties = { width: "100%", marginTop: 22, padding: 15, borderRadius: 14, border: 0, background: "linear-gradient(135deg,#635BFF,#8b5cf6)", color: "white", fontWeight: 900, cursor: "pointer", boxShadow: "0 16px 42px rgba(99,91,255,.30)" };
