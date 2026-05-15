import PortalNav from "@/components/PortalNav";

const BACKEND_URL =
  process.env.BACKEND_URL || "https://ecommerce-ai-agent-platform-1.onrender.com";

async function getBackendHealth() {
  try {
    const response = await fetch(`${BACKEND_URL}/health`, {
      cache: "no-store",
    });

    if (!response.ok) {
      return {
        ok: false,
        status: response.status,
        data: null,
      };
    }

    return {
      ok: true,
      status: response.status,
      data: await response.json(),
    };
  } catch {
    return {
      ok: false,
      status: 0,
      data: null,
    };
  }
}

export default async function AdminPage() {
  const health = await getBackendHealth();

  return (
    <main
      style={{
        minHeight: "100vh",
        padding: "56px 24px",
        background: "#020617",
        color: "#f8fafc",
        fontFamily:
          "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif",
      }}
    >
      <section style={{ maxWidth: 1180, margin: "0 auto" }}>
        <PortalNav />

        <p style={{ color: "#38bdf8", fontWeight: 800, letterSpacing: 1 }}>
          OWNER ADMIN CONTROL CENTRE
        </p>

        <h1 style={{ fontSize: 54, lineHeight: 1.05, margin: "16px 0" }}>
          Ecommerce AI Agent Platform
        </h1>

        <p style={{ color: "#cbd5e1", fontSize: 18, maxWidth: 760 }}>
          Production admin shell for monitoring backend health, governance state,
          tenant readiness, agent execution status, and release operations.
        </p>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))",
            gap: 18,
            marginTop: 36,
          }}
        >
          {[
            ["Backend Runtime", health.ok ? "Live" : "Unavailable"],
            ["HTTP Status", String(health.status)],
            ["Owner Approval", "Required for spend/scaling/contracts"],
            ["Tenant Isolation", "Required"],
            ["Entitlement Controls", "Required"],
            ["Release State", "Production baseline active"],
          ].map(([label, value]) => (
            <div
              key={label}
              style={{
                padding: 22,
                borderRadius: 18,
                background: "rgba(15,23,42,.88)",
                border: "1px solid rgba(148,163,184,.22)",
              }}
            >
              <div style={{ color: "#94a3b8", fontSize: 13 }}>{label}</div>
              <strong style={{ display: "block", marginTop: 8, fontSize: 18 }}>
                {value}
              </strong>
            </div>
          ))}
        </div>

        {health.data && (
          <pre
            style={{
              marginTop: 32,
              padding: 22,
              borderRadius: 18,
              background: "rgba(2,6,23,.9)",
              border: "1px solid rgba(148,163,184,.22)",
              color: "#cbd5e1",
              overflowX: "auto",
              fontSize: 13,
            }}
          >
            {JSON.stringify(health.data, null, 2)}
          </pre>
        )}
      </section>
    </main>
  );
}