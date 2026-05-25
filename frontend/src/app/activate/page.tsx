import { headers } from "next/headers";
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
      background: "radial-gradient(circle at top left, #dbeafe 0, transparent 34%), linear-gradient(135deg, #e2e8f0 0%, #eef2ff 50%, #eff6ff 100%)",
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
        <p style={{ color: "#8b5cf6", fontWeight: 900, letterSpacing: 1, fontSize: 12 }}>
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
              background: "#e2e8f0",
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
const buttonStyle: React.CSSProperties = { width: "100%", padding: 15, borderRadius: 14, border: 0, background: "#8b5cf6", color: "white", fontWeight: 900, cursor: "pointer", marginTop: 20, boxShadow: "0 14px 30px rgba(37,99,235,.24)" };
