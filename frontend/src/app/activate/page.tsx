import { headers } from "next/headers";
export const dynamic = "force-dynamic";

type ActivatePageProps = {
  searchParams?: Promise<{
    token?: string;
  }>;
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

    if (!response.ok) {
      return null;
    }

    return await response.json();
  } catch {
    return null;
  }
}

export default async function ActivatePage({ searchParams }: ActivatePageProps) {
  const resolvedSearchParams = searchParams ? await searchParams : {};
  const token = resolvedSearchParams.token || "";
  const invite = token ? await getInviteStatus(token) : null;

  const isValid =
    invite &&
    invite.success === true &&
    (
      invite.valid === true ||
      (invite.expired === false && invite.used === false)
    );

  return (
    <main
      style={{
        minHeight: "100vh",
        display: "grid",
        placeItems: "center",
        padding: 24,
        background:
          "linear-gradient(135deg, #020617 0%, #0f172a 48%, #172554 100%)",
        color: "white",
        fontFamily:
          "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif",
      }}
    >
      <section
        style={{
          width: "100%",
          maxWidth: 520,
          padding: 34,
          borderRadius: 24,
          background: "rgba(15,23,42,.92)",
          border: "1px solid rgba(148,163,184,.28)",
          boxShadow: "0 28px 90px rgba(0,0,0,.32)",
        }}
      >
        <p style={{ color: "#38bdf8", fontWeight: 800, letterSpacing: 1 }}>
          CLIENT ACCOUNT ACTIVATION
        </p>

        <h1 style={{ fontSize: 38, lineHeight: 1.05, margin: "14px 0" }}>
          Create your secure portal password
        </h1>

        {!token && (
          <p style={{ color: "#fecaca", lineHeight: 1.7 }}>
            Activation token is missing. Please use the activation link provided
            by the platform owner.
          </p>
        )}

        {token && !isValid && (
          <p style={{ color: "#fecaca", lineHeight: 1.7 }}>
            This activation link is invalid, expired, or has already been used.
            Please request a new activation link.
          </p>
        )}

        {isValid && (
          <>
            <div
              style={{
                marginTop: 20,
                padding: 18,
                borderRadius: 16,
                background: "rgba(2,6,23,.72)",
                border: "1px solid rgba(148,163,184,.2)",
              }}
            >
              <strong>{invite.company_name || "Client Account"}</strong>
              <p style={{ color: "#cbd5e1", marginBottom: 0 }}>
                {invite.email}
              </p>
              <p style={{ color: "#94a3b8", marginBottom: 0 }}>
                Package: {invite.package}
              </p>
            </div>

            <form method="POST" action="/api/activate" style={{ marginTop: 24 }}>
              <input type="hidden" name="token" value={token} />

              <label style={{ display: "block", marginBottom: 10 }}>
                Password
              </label>
              <input
                name="password"
                type="password"
                required
                minLength={10}
                placeholder="Create password"
                style={{
                  width: "100%",
                  padding: 14,
                  borderRadius: 12,
                  border: "1px solid rgba(148,163,184,.4)",
                  marginBottom: 16,
                }}
              />

              <label style={{ display: "block", marginBottom: 10 }}>
                Confirm password
              </label>
              <input
                name="confirm_password"
                type="password"
                required
                minLength={10}
                placeholder="Confirm password"
                style={{
                  width: "100%",
                  padding: 14,
                  borderRadius: 12,
                  border: "1px solid rgba(148,163,184,.4)",
                  marginBottom: 18,
                }}
              />

              <button
                type="submit"
                style={{
                  width: "100%",
                  padding: 15,
                  borderRadius: 12,
                  border: 0,
                  background: "#2563eb",
                  color: "white",
                  fontWeight: 800,
                  cursor: "pointer",
                }}
              >
                Activate Account
              </button>
            </form>
          </>
        )}
      </section>
    </main>
  );
}