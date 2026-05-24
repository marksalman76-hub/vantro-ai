"use client";

import React, { useEffect, useState } from "react";

type InfoPageProps = {
  eyebrow: string;
  title: string;
  body: string;
  bullets: string[];
};

function InfoPage({ eyebrow, title, body, bullets }: InfoPageProps) {
  const [darkModeEnabled, setDarkModeEnabled] = useState(false);

  useEffect(() => {
    try {
      setDarkModeEnabled(window.localStorage.getItem("client_workspace_dark_mode") === "dark");
    } catch {}
  }, []);

  return (
    <main
      style={{
        minHeight: "100vh",
        background: darkModeEnabled
          ? "radial-gradient(circle at 18% 0%, rgba(79,70,229,.20), transparent 28%), radial-gradient(circle at 92% 6%, rgba(124,58,237,.16), transparent 30%), linear-gradient(180deg, #050b18 0%, #071120 48%, #050b18 100%)"
          : "#f4f7fb",
        color: darkModeEnabled ? "#f8fafc" : "#0f172a",
        fontFamily: 'Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
        padding: "clamp(24px,4vw,54px)",
        boxSizing: "border-box",
      }}
    >
      <section
        style={{
          maxWidth: 880,
          margin: "0 auto",
          borderRadius: 26,
          padding: "clamp(24px,4vw,38px)",
          background: darkModeEnabled
            ? "linear-gradient(180deg, rgba(10,22,46,.96), rgba(7,16,34,.98))"
            : "#ffffff",
          border: darkModeEnabled ? "1px solid rgba(129,140,248,.28)" : "1px solid #e5eaf2",
          boxShadow: darkModeEnabled ? "0 24px 80px rgba(0,0,0,.34)" : "0 24px 70px rgba(15,23,42,.08)",
        }}
      >
        <div style={{ color: darkModeEnabled ? "#a5b4fc" : "#4f46e5", fontSize: 12, fontWeight: 900, letterSpacing: 1.3, textTransform: "uppercase", marginBottom: 10 }}>
          {eyebrow}
        </div>

        <h1 style={{ margin: 0, fontSize: 34, letterSpacing: -1.1 }}>{title}</h1>

        <p style={{ margin: "14px 0 0", color: darkModeEnabled ? "#94a3b8" : "#64748b", fontSize: 15, lineHeight: 1.6 }}>
          {body}
        </p>

        <div style={{ marginTop: 22, display: "grid", gap: 12 }}>
          {bullets.map((item) => (
            <div
              key={item}
              style={{
                borderRadius: 16,
                padding: 14,
                background: darkModeEnabled ? "rgba(12,24,49,.92)" : "#f8fafc",
                border: darkModeEnabled ? "1px solid rgba(99,102,241,.24)" : "1px solid #e5eaf2",
                color: darkModeEnabled ? "#cbd5e1" : "#334155",
                fontWeight: 750,
                lineHeight: 1.45,
              }}
            >
              {item}
            </div>
          ))}
        </div>

        <a
          href="/client"
          style={{
            display: "inline-flex",
            marginTop: 24,
            borderRadius: 14,
            padding: "11px 14px",
            background: "linear-gradient(135deg,#4f46e5,#7c3aed)",
            color: "#ffffff",
            textDecoration: "none",
            fontWeight: 900,
          }}
        >
          Back to workspace
        </a>
      </section>
    </main>
  );
}

export default function Page() {
  return (
    <InfoPage
      eyebrow="Terms"
      title="Terms of Service"
      body="These terms describe the expected use of the E-commerce AI Agent Platform, including workspace access, billing, AI-generated deliverables, and governed execution controls."
      bullets={[
        'Clients are responsible for reviewing AI-generated outputs before use in live business activity.', 'High-risk actions, spending changes, campaign scaling, and major commercial changes remain subject to approval controls.', 'Subscription access, available agents, credits, and workspace features depend on the client’s active plan.', 'The platform may update features, workflows, and safeguards to improve security, quality, and reliability.'
      ]}
    />
  );
}
