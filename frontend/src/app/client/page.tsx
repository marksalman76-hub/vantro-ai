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

export default async function ClientPortalPage() {
  const health = await getBackendHealth();

  const clientModules = [
    ["Run AI Agent", "Prepare ecommerce execution tasks with governed approval controls."],
    ["Product Intelligence", "Generate product positioning, offer angles, and conversion guidance."],
    ["UGC Creative", "Plan short-form video, creator briefs, and performance-led creative concepts."],
    ["Influencer Outreach", "Prepare creator targeting, outreach, follow-up, and collaboration workflows."],
    ["Analytics Optimisation", "Review performance signals and identify improvement opportunities."],
    ["Approval Queue", "Keep spend, scaling, contracts, and authority-sensitive actions owner-governed."],
  ];

  return (
    <main
      style={{
        minHeight: "100vh",
        padding: "56px 24px",
        background:
          "linear-gradient(135deg, #f8fafc 0%, #eef2ff 48%, #e0f2fe 100%)",
        color: "#0f172a",
        fontFamily:
          "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif",
      }}
    >
      <section style={{ maxWidth: 1180, margin: "0 auto" }}>
        <PortalNav />

        <p style={{ color: "#2563eb", fontWeight: 800, letterSpacing: 1 }}>
          CUSTOMER PORTAL
        </p>

        <h1 style={{ fontSize: 54, lineHeight: 1.05, margin: "16px 0" }}>
          Ecommerce AI Agent Workspace
        </h1>

        <p style={{ color: "#475569", fontSize: 18, maxWidth: 780 }}>
          Client-facing workspace for launching governed ecommerce AI workflows,
          reviewing outputs, tracking execution readiness, and keeping sensitive
          actions under owner approval.
        </p>

        <div
          style={{
            marginTop: 30,
            display: "inline-flex",
            alignItems: "center",
            gap: 10,
            padding: "12px 16px",
            borderRadius: 999,
            background: health.ok
              ? "rgba(22, 163, 74, .12)"
              : "rgba(239, 68, 68, .12)",
            border: health.ok
              ? "1px solid rgba(22, 163, 74, .35)"
              : "1px solid rgba(239, 68, 68, .35)",
            color: health.ok ? "#166534" : "#991b1b",
            fontWeight: 800,
          }}
        >
          <span>{health.ok ? "● Platform online" : "● Platform unavailable"}</span>
          <span style={{ opacity: 0.8 }}>Status: {health.status}</span>
        </div>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
            gap: 18,
            marginTop: 38,
          }}
        >
          {clientModules.map(([title, description]) => (
            <div
              key={title}
              style={{
                padding: 24,
                borderRadius: 20,
                background: "rgba(255,255,255,.86)",
                border: "1px solid rgba(148,163,184,.32)",
                boxShadow: "0 24px 80px rgba(15,23,42,.08)",
              }}
            >
              <strong style={{ display: "block", fontSize: 20 }}>{title}</strong>
              <p style={{ color: "#64748b", lineHeight: 1.65, marginTop: 10 }}>
                {description}
              </p>
            </div>
          ))}
        </div>

        <div
          style={{
            marginTop: 42,
            padding: 24,
            borderRadius: 20,
            background: "#0f172a",
            color: "#e2e8f0",
          }}
        >
          <strong>Governance notice</strong>
          <p style={{ color: "#cbd5e1", lineHeight: 1.7 }}>
            Spending increases, scaling actions, contracts, paid collaborations,
            and authority-sensitive decisions require owner approval before
            execution.
          </p>
        </div>
      </section>
    </main>
  );
}