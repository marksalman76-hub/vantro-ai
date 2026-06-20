"use client";

import Link from "next/link";

export default function DemoPage() {
  return (
    <main
      style={{
        minHeight: "100vh",
        background: "radial-gradient(circle at 18% 0%, rgba(124,58,237,.28), transparent 32%), radial-gradient(circle at 86% 8%, rgba(14,207,188,.16), transparent 30%), #05070d",
        color: "#f8fafc",
        fontFamily: "Inter, ui-sans-serif, system-ui",
        padding: "64px 24px",
      }}
    >
      <section
        style={{
          maxWidth: 980,
          margin: "0 auto",
          background: "linear-gradient(180deg, rgba(255,255,255,.075), rgba(255,255,255,.03))",
          border: "1px solid rgba(165,180,252,.18)",
          borderRadius: 34,
          padding: "clamp(30px,5vw,56px)",
          boxShadow: "0 30px 90px rgba(0,0,0,.35), inset 0 1px 0 rgba(255,255,255,.08)",
          backdropFilter: "blur(18px)",
        }}
      >
        <div style={{ color: "#c4ff00", fontSize: 12, fontWeight: 950, letterSpacing: ".16em", textTransform: "uppercase", marginBottom: 14 }}>
          Demo
        </div>

        <h1 style={{ fontSize: "clamp(46px,7vw,84px)", lineHeight: .92, letterSpacing: "-.075em", margin: "0 0 22px", fontWeight: 950 }}>
          See the Nexus AI workforce in action.
        </h1>

        <p style={{ color: "#aab3c5", fontSize: 16, lineHeight: 1.7, maxWidth: 760, marginBottom: 30 }}>
          Explore how specialist ecommerce agents can support product research, UGC, ads, SEO, store pages,
          CRM workflows, customer support, analytics, and governed execution from one premium workspace.
        </p>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(220px,1fr))", gap: 16, marginBottom: 32 }}>
          {[
            ["AI workforce preview", "See how multiple ecommerce agents work together across strategy, creative, operations and execution."],
            ["Governed execution", "Understand how approvals protect high-risk actions such as spending, scaling, publishing and account changes."],
            ["Client workspace flow", "Review the business profile, agent selection, deliverables, integrations and support experience."]
          ].map(([title, body]) => (
            <div key={title} style={{ border: "1px solid rgba(165,180,252,.16)", borderRadius: 22, padding: 20, background: "rgba(12,24,49,.62)" }}>
              <strong style={{ display: "block", fontSize: 16, marginBottom: 9 }}>{title}</strong>
              <span style={{ color: "#cbd5e1", lineHeight: 1.6, fontSize: 13 }}>{body}</span>
            </div>
          ))}
        </div>

        <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
          <Link
            href="/signup"
            style={{
              display: "inline-flex",
              borderRadius: 16,
              padding: "14px 18px",
              background: "#c4ff00",
              color: "#05070d",
              textDecoration: "none",
              fontWeight: 950,
            }}
          >
            Request demo access
          </Link>

          <Link
            href="/"
            style={{
              display: "inline-flex",
              borderRadius: 16,
              padding: "14px 18px",
              border: "1px solid rgba(255,255,255,.16)",
              color: "#f8fafc",
              textDecoration: "none",
              fontWeight: 900,
            }}
          >
            Back to home
          </Link>
        </div>
      </section>
    </main>
  );
}
