export default function Home() {
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
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))",
            gap: 16,
            marginTop: 44,
          }}
        >
          {[
            "Governed AI execution",
            "Product and offer intelligence",
            "UGC creative planning",
            "Influencer outreach workflows",
            "Analytics optimisation",
            "White-label deployment ready",
          ].map((item) => (
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

        <div style={{ marginTop: 48, color: "#94a3b8" }}>
          Backend:
          <span style={{ color: "#e2e8f0", marginLeft: 8 }}>
            https://ecommerce-ai-agent-platform-1.onrender.com
          </span>
        </div>
      </section>
    </main>
  );
}