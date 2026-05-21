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

    const data = await response.json();

    return {
      ok: true,
      status: response.status,
      data,
    };
  } catch {
    return {
      ok: false,
      status: 0,
      data: null,
    };
  }
}

export default async function Home() {
  const health = await getBackendHealth();

  const capabilityCards = [
    "Governed AI execution",
    "Product and offer intelligence",
    "UGC creative planning",
    "Influencer outreach workflows",
    "Analytics optimisation",
    "White-label deployment ready",
  ];

  return (
    <main
      style={{
        minHeight: "100vh",
        padding: "64px 24px",
        fontFamily:
          "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif",
        background:
          "linear-gradient(135deg, #07111f 0%, #101827 45%, #111827 100%)",
        color: "white",
      }}
    >
      <section style={{ maxWidth: 1120, margin: "0 auto" }}>
        <p style={{ color: "#38bdf8", fontWeight: 700, letterSpacing: 1 }}>
          PREMIUM WHITE-LABEL ECOMMERCE AI AGENT PLATFORM
        </p>

        <h1
          style={{
            fontSize: "clamp(42px, 7vw, 82px)",
            lineHeight: 1,
            margin: "20px 0",
            maxWidth: 900,
          }}
        >
          Launch, optimise, and scale ecommerce operations with governed AI agents.
        </h1>

        <p
          style={{
            fontSize: 20,
            lineHeight: 1.7,
            color: "#cbd5e1",
            maxWidth: 760,
          }}
        >
          A production-ready ecommerce AI agent platform with owner approval gates,
          product intelligence, UGC planning, analytics optimisation, influencer
          outreach, memory, learning, and secure white-label deployment controls.
        </p>

        <div
          style={{
            marginTop: 34,
            display: "inline-flex",
            alignItems: "center",
            gap: 10,
            padding: "12px 16px",
            borderRadius: 999,
            background: health.ok ? "rgba(22, 163, 74, .18)" : "rgba(239, 68, 68, .18)",
            border: health.ok
              ? "1px solid rgba(34, 197, 94, .4)"
              : "1px solid rgba(248, 113, 113, .4)",
            color: health.ok ? "#bbf7d0" : "#fecaca",
            fontWeight: 700,
          }}
        >
          <span>{health.ok ? "● Backend live" : "● Backend unavailable"}</span>
          <span style={{ opacity: 0.8 }}>Status: {health.status}</span>
        </div>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))",
            gap: 16,
            marginTop: 44,
          }}
        >
          {capabilityCards.map((item) => (
            <div
              key={item}
              style={{
                border: "1px solid rgba(148,163,184,.25)",
                borderRadius: 18,
                padding: 22,
                background: "rgba(15,23,42,.72)",
                boxShadow: "0 20px 70px rgba(0,0,0,.22)",
              }}
            >
              <strong style={{ fontSize: 18 }}>{item}</strong>
            </div>
          ))}
        </div>

        <div
          style={{
            marginTop: 48,
            borderTop: "1px solid rgba(148,163,184,.22)",
            paddingTop: 24,
            color: "#94a3b8",
          }}
        >
          <div>
            Backend:
            <span style={{ color: "#e2e8f0", marginLeft: 8 }}>
              {BACKEND_URL}
            </span>
          </div>

          <section
            style={{
              border: "1px solid rgba(148, 163, 184, 0.22)",
              borderRadius: 18,
              padding: 22,
              background: "rgba(15, 23, 42, 0.56)",
              marginTop: 24,
            }}
          >
            <h2 style={{ margin: "0 0 10px", fontSize: 18 }}>Platform readiness</h2>
            <p style={{ margin: 0, color: "#cbd5e1", lineHeight: 1.7 }}>
              The ecommerce AI workforce is connected, monitored, and ready for governed execution.
              Internal diagnostics are protected from the client-facing experience.
            </p>
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
                gap: 14,
                marginTop: 18,
              }}
            >
              {["Secure runtime", "Governed execution", "White-label ready", "Learning enabled"].map((item) => (
                <div
                  key={item}
                  style={{
                    border: "1px solid rgba(148, 163, 184, 0.18)",
                    borderRadius: 14,
                    padding: 14,
                    background: "rgba(2, 6, 23, 0.38)",
                    color: "#f8fafc",
                    fontWeight: 700,
                  }}
                >
                  {item}
                </div>
              ))}
            </div>
          </section>
        </div>
      </section>
    </main>
  );
}
