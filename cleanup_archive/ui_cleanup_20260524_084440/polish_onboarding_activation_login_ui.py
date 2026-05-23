from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

activate_page = ROOT / "frontend" / "src" / "app" / "activate" / "page.tsx"
login_page = ROOT / "frontend" / "src" / "app" / "login" / "page.tsx"

for file in [activate_page, login_page]:
    backup = BACKUP_DIR / f"{file.stem}_before_onboarding_ui_polish_{datetime.now().strftime('%Y%m%d_%H%M%S')}{file.suffix}"
    backup.write_text(file.read_text(encoding="utf-8"), encoding="utf-8")

activate_page.write_text(r'''import { headers } from "next/headers";
export const dynamic = "force-dynamic";

type ActivatePageProps = {
  searchParams?: Promise<{ token?: string }>;
};

async function getInviteStatus(token: string) {
  try {
    const headerStore = await headers();
    const host = headerStore.get("host") || "ecommerce-ai-agent-platform.vercel.app";
    const proto = headerStore.get("x-forwarded-proto") || "https";
    const origin = `${proto}://${host}`;

    const response = await fetch(
      `${origin}/api/activation-invite-status?token=${encodeURIComponent(token)}`,
      { cache: "no-store" }
    );

    if (!response.ok) return null;
    return await response.json();
  } catch {
    return null;
  }
}

export default async function ActivatePage({ searchParams }: ActivatePageProps) {
  const resolvedSearchParams = searchParams ? await searchParams : {};
  const token = resolvedSearchParams.token || "";
  const invite = token ? await getInviteStatus(token) : null;
  const isValid = Boolean(invite?.success === true && invite?.valid === true);

  return (
    <main style={{
      minHeight: "100vh",
      display: "grid",
      placeItems: "center",
      padding: 24,
      background: "radial-gradient(circle at top left, #dbeafe 0, transparent 34%), linear-gradient(135deg, #f8fafc 0%, #eef2ff 50%, #eff6ff 100%)",
      color: "#0f172a",
      fontFamily: "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif",
    }}>
      <section style={{
        width: "100%",
        maxWidth: 560,
        padding: 36,
        borderRadius: 28,
        background: "rgba(255,255,255,.92)",
        border: "1px solid rgba(148,163,184,.28)",
        boxShadow: "0 30px 90px rgba(15,23,42,.16)",
      }}>
        <p style={{ color: "#2563eb", fontWeight: 900, letterSpacing: 1, fontSize: 12 }}>
          SECURE CLIENT ONBOARDING
        </p>

        <h1 style={{ fontSize: 38, lineHeight: 1.05, margin: "12px 0", letterSpacing: "-.04em" }}>
          Create your workspace password
        </h1>

        <p style={{ color: "#64748b", lineHeight: 1.7, marginTop: 0 }}>
          Set your secure password to activate your AI workspace and access your selected agents.
        </p>

        {!token && (
          <div style={noticeStyle("#fef2f2", "#fecaca", "#991b1b")}>
            Activation token is missing. Please use the activation link provided by the platform owner.
          </div>
        )}

        {token && !isValid && (
          <div style={noticeStyle("#fef2f2", "#fecaca", "#991b1b")}>
            This activation link is invalid, expired, or has already been used. Please request a new activation link.
          </div>
        )}

        {isValid && (
          <>
            <div style={{
              marginTop: 22,
              padding: 18,
              borderRadius: 18,
              background: "#f8fafc",
              border: "1px solid #e2e8f0",
            }}>
              <strong>{invite.company_name || "Client Account"}</strong>
              <p style={{ color: "#475569", margin: "8px 0 0" }}>{invite.email || "Client email confirmed"}</p>
              <p style={{ color: "#64748b", margin: "6px 0 0" }}>Package: {invite.package || "Active client workspace"}</p>
            </div>

            <form method="POST" action="/api/activate" style={{ marginTop: 24 }}>
              <input type="hidden" name="token" value={token} />

              <label style={labelStyle}>Password</label>
              <input name="password" type="password" required minLength={10} placeholder="Minimum 10 characters" style={inputStyle} />

              <label style={labelStyle}>Confirm password</label>
              <input name="confirm_password" type="password" required minLength={10} placeholder="Confirm password" style={inputStyle} />

              <button type="submit" style={buttonStyle}>Activate workspace</button>
            </form>
          </>
        )}
      </section>
    </main>
  );
}

function noticeStyle(background: string, border: string, color: string): React.CSSProperties {
  return { marginTop: 20, padding: 16, borderRadius: 16, background, border: `1px solid ${border}`, color, lineHeight: 1.6 };
}

const labelStyle: React.CSSProperties = { display: "block", marginBottom: 8, marginTop: 16, color: "#334155", fontWeight: 800 };
const inputStyle: React.CSSProperties = { width: "100%", padding: 14, borderRadius: 14, border: "1px solid #cbd5e1", marginBottom: 4, fontSize: 15, boxSizing: "border-box" };
const buttonStyle: React.CSSProperties = { width: "100%", padding: 15, borderRadius: 14, border: 0, background: "#2563eb", color: "white", fontWeight: 900, cursor: "pointer", marginTop: 20, boxShadow: "0 14px 30px rgba(37,99,235,.24)" };
''', encoding="utf-8")

login_page.write_text(r'''type LoginPageProps = {
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
''', encoding="utf-8")

print("ONBOARDING_ACTIVATION_LOGIN_UI_POLISHED")