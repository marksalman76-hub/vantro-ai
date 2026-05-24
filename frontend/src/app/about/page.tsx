"use client";

import Link from "next/link";

export default function AboutPage() {
  return (
    <main
      style={{
        minHeight: "100vh",
        background: "radial-gradient(circle at top, rgba(124,58,237,.24), transparent 34%), #020617",
        padding: "64px 24px",
        color: "#f8fafc",
        fontFamily: "Inter, ui-sans-serif, system-ui",
      }}
    >
      <section
        style={{
          maxWidth: 960,
          margin: "0 auto",
          background: "rgba(7,16,40,.92)",
          border: "1px solid rgba(99,102,241,.22)",
          borderRadius: 28,
          padding: "clamp(28px,4vw,46px)",
          boxShadow: "0 30px 70px rgba(0,0,0,.35)",
        }}
      >
        <div style={{ fontSize: 12, fontWeight: 900, letterSpacing: ".14em", color: "#a5b4fc", marginBottom: 10 }}>
          ABOUT NEXUS AI
        </div>

        <h1 style={{ fontSize: "clamp(40px,6vw,68px)", lineHeight: 0.95, margin: "0 0 22px", fontWeight: 950 }}>
          A governed AI workforce for modern ecommerce businesses.
        </h1>

        <p style={{ color: "#cbd5e1", lineHeight: 1.75, fontSize: 17, marginBottom: 24 }}>
          Nexus AI was built to replace fragmented AI tools with a single governed AI workforce designed for real business execution.
          The platform combines specialist agents for strategy, ecommerce operations, content, UGC, SEO, ads, analytics, CRM, support,
          automation and business growth inside one intelligent workspace.
        </p>

        <div style={{ display: "grid", gap: 16, marginTop: 26 }}>
          {[
            ["Not another chatbot", "Nexus AI is designed as an operating layer for ecommerce businesses — helping teams produce premium outputs, coordinate workflows and move from ideas to governed execution."],
            ["Built for control", "High-risk actions remain approval-gated, while safe operational workflows can move faster with audit visibility, entitlement controls and client-safe execution."],
            ["Globally adaptable", "Agents adapt to region, language style, currency, buyer behaviour, market context, product niche, brand positioning and customer expectations."],
            ["White-label ready", "The platform is built for agencies, operators and businesses that want to sell, deploy and manage premium AI agent systems without exposing internal logic."]
          ].map(([title, body]) => (
            <div
              key={title}
              style={{
                border: "1px solid rgba(99,102,241,.22)",
                borderRadius: 18,
                padding: "20px 22px",
                background: "rgba(12,24,49,.72)",
              }}
            >
              <div style={{ fontWeight: 950, fontSize: 19, marginBottom: 8 }}>{title}</div>
              <div style={{ color: "#cbd5e1", lineHeight: 1.7, fontSize: 15 }}>{body}</div>
            </div>
          ))}
        </div>

        <Link
          href="/"
          style={{
            display: "inline-flex",
            marginTop: 30,
            borderRadius: 16,
            padding: "14px 18px",
            background: "linear-gradient(135deg,#7c3aed,#4f46e5)",
            color: "#fff",
            textDecoration: "none",
            fontWeight: 900,
          }}
        >
          Back to home
        </Link>
      </section>
    </main>
  );
}
