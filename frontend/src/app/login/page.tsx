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
      background: "radial-gradient(circle at top right, #dbeafe 0, transparent 34%), linear-gradient(135deg, #f8fafc 0%, #eef2ff 50%, #eff6ff 100%)",
      color: "#0f172a",
      fontFamily: "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif",
    }}>
      <form action="/api/client-login" method="POST" style={{
        width: "100%",
        maxWidth: 480,
        padding: 36,
        borderRadius: 28,
        background: "rgba(255,255,255,.94)",
        border: "1px solid rgba(148,163,184,.28)",
        boxShadow: "0 30px 90px rgba(15,23,42,.16)",
      }}>
        <p style={{ color: "#2563eb", fontWeight: 900, letterSpacing: 1, fontSize: 12 }}>CLIENT PORTAL</p>
        <h1 style={{ margin: "12px 0", fontSize: 38, lineHeight: 1.05, letterSpacing: "-.04em" }}>Access your workspace</h1>
        <p style={{ color: "#64748b", lineHeight: 1.7, marginTop: 0 }}>
          Sign in to manage your AI agents, approvals, outputs, and workspace activity.
        </p>

        {activated && (
          <div style={{ marginTop: 18, padding: 14, borderRadius: 16, background: "#ecfdf5", border: "1px solid #bbf7d0", color: "#166534" }}>
            Your account is activated. Sign in with the password you created.
          </div>
        )}

        {error && (
          <div style={{ marginTop: 18, padding: 14, borderRadius: 16, background: "#fef2f2", border: "1px solid #fecaca", color: "#991b1b" }}>
            Login failed. Check the email and password, then try again.
          </div>
        )}

        <input type="hidden" name="next" value={nextPath} />

        <label style={labelStyle}>Email</label>
        <input name="email" type="email" placeholder="client@example.com" required style={inputStyle} />

        <label style={labelStyle}>Password</label>
        <input name="password" type="password" placeholder="Password" required style={inputStyle} />

        <button type="submit" style={buttonStyle}>Login to workspace</button>
      </form>
    </main>
  );
}

const labelStyle: React.CSSProperties = { display: "block", marginTop: 18, marginBottom: 8, color: "#334155", fontWeight: 800 };
const inputStyle: React.CSSProperties = { width: "100%", padding: 14, borderRadius: 14, border: "1px solid #cbd5e1", fontSize: 15, boxSizing: "border-box" };
const buttonStyle: React.CSSProperties = { width: "100%", marginTop: 22, padding: 15, borderRadius: 14, border: 0, background: "#2563eb", color: "white", fontWeight: 900, cursor: "pointer", boxShadow: "0 14px 30px rgba(37,99,235,.24)" };
