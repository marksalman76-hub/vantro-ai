"use client";

import Link from "next/link";

export default function CookiesPage() {
  return (
    <main
      style={{
        minHeight: "100vh",
        background: "radial-gradient(circle at top, rgba(67,56,202,.24), transparent 34%), #020617",
        padding: "64px 24px",
        color: "#f8fafc",
        fontFamily: "Inter, ui-sans-serif, system-ui",
      }}
    >
      <section
        style={{
          maxWidth: 820,
          margin: "0 auto",
          background: "rgba(7,16,40,.92)",
          border: "1px solid rgba(99,102,241,.22)",
          borderRadius: 28,
          padding: "40px",
          boxShadow: "0 30px 70px rgba(0,0,0,.35)",
        }}
      >
        <div style={{ fontSize: 12, fontWeight: 900, letterSpacing: ".14em", color: "#a5b4fc", marginBottom: 10 }}>
          COOKIES
        </div>

        <h1 style={{ fontSize: "clamp(38px,5vw,56px)", lineHeight: 1, marginBottom: 20, fontWeight: 900 }}>
          Cookie Policy
        </h1>

        <p style={{ color: "#cbd5e1", lineHeight: 1.7, fontSize: 16, marginBottom: 26 }}>
          This Cookie Policy explains how the Ecommerce AI Agent Platform may use cookies and similar technologies to operate the workspace, maintain sessions, improve performance, support security, and remember user preferences.
        </p>

        {[
          ["Essential cookies", "Required for login sessions, workspace access, security checks, account state, billing flow continuity, and core platform operation."],
          ["Preference cookies", "Used to remember choices such as colour mode, workspace preferences, and interface settings."],
          ["Performance cookies", "May help understand platform reliability, page performance, errors, and user experience improvements."],
          ["Third-party services", "Some connected providers, payment processors, analytics tools, or embedded systems may use their own cookies under their respective policies."],
          ["Managing cookies", "Clients can manage browser cookie settings directly in their browser. Blocking essential cookies may affect login, billing, or workspace functionality."]
        ].map(([title, body]) => (
          <div
            key={title}
            style={{
              border: "1px solid rgba(99,102,241,.22)",
              borderRadius: 18,
              padding: "20px 22px",
              marginBottom: 16,
              background: "rgba(12,24,49,.72)",
            }}
          >
            <div style={{ fontWeight: 900, fontSize: 18, marginBottom: 10 }}>{title}</div>
            <div style={{ color: "#cbd5e1", lineHeight: 1.7, fontSize: 15 }}>{body}</div>
          </div>
        ))}

        <Link
          href="/"
          style={{
            display: "inline-flex",
            marginTop: 24,
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
