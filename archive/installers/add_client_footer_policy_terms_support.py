from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
CLIENT_PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
APP_DIR = ROOT / "frontend" / "src" / "app"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUP_DIR / f"client_page_before_footer_links_{stamp}.tsx"
shutil.copy2(CLIENT_PAGE, backup)

s = CLIENT_PAGE.read_text(encoding="utf-8")

footer = r'''
        <footer
          style={{
            marginTop: 22,
            padding: "18px 6px 4px",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            gap: 14,
            flexWrap: "wrap",
            color: darkModeEnabled ? "#94a3b8" : "#64748b",
            fontSize: 12,
          }}
        >
          <div style={{ fontWeight: 800 }}>
            © {new Date().getFullYear()} E-commerce AI Agent Platform
          </div>

          <nav
            aria-label="Footer links"
            style={{
              display: "flex",
              gap: 12,
              flexWrap: "wrap",
              alignItems: "center",
            }}
          >
            {[
              ["Privacy Policy", "/privacy-policy"],
              ["Terms of Service", "/terms-of-service"],
              ["Contact us", "/support-request"],
            ].map(([label, href]) => (
              <a
                key={label}
                href={href}
                style={{
                  color: darkModeEnabled ? "#cbd5e1" : "#334155",
                  textDecoration: "none",
                  fontWeight: 850,
                  border: darkModeEnabled ? "1px solid rgba(129,140,248,.24)" : "1px solid #e5eaf2",
                  background: darkModeEnabled ? "rgba(12,24,49,.72)" : "#ffffff",
                  borderRadius: 999,
                  padding: "8px 11px",
                }}
              >
                {label}
              </a>
            ))}
          </nav>
        </footer>
'''

marker = '''      </div>


{/* OUTPUT_VIEWER_POPUP_MODAL_LOCKED_V1 */}'''

if marker not in s:
    raise SystemExit("FAILED: client shell closing marker not found")

if "E-commerce AI Agent Platform" not in s or "/privacy-policy" not in s:
    s = s.replace(marker, footer + "\n" + marker, 1)

CLIENT_PAGE.write_text(s, encoding="utf-8")

shared_page = r'''"use client";

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

export default InfoPage;
'''

pages = {
    "privacy-policy": {
        "eyebrow": "Privacy",
        "title": "Privacy Policy",
        "body": "This page explains how client workspace information, business profile data, execution activity, and support details are handled within the E-commerce AI Agent Platform.",
        "bullets": [
            "We use client information to operate the workspace, provide AI execution services, manage subscriptions, and support account requests.",
            "Business profile details are used to tailor AI outputs and improve client-specific deliverables.",
            "Payment details are handled through secure payment providers and are not stored directly in the client workspace UI.",
            "Clients can contact support to request help with account access, billing, privacy, or workspace data."
        ],
    },
    "terms-of-service": {
        "eyebrow": "Terms",
        "title": "Terms of Service",
        "body": "These terms describe the expected use of the E-commerce AI Agent Platform, including workspace access, billing, AI-generated deliverables, and governed execution controls.",
        "bullets": [
            "Clients are responsible for reviewing AI-generated outputs before use in live business activity.",
            "High-risk actions, spending changes, campaign scaling, and major commercial changes remain subject to approval controls.",
            "Subscription access, available agents, credits, and workspace features depend on the client’s active plan.",
            "The platform may update features, workflows, and safeguards to improve security, quality, and reliability."
        ],
    },
    "support-request": {
        "eyebrow": "Support",
        "title": "Contact us / Support request",
        "body": "Use this page to request help with billing, account access, workspace setup, integrations, AI outputs, or subscription support.",
        "bullets": [
            "For billing or payment issues, include your business name and the email linked to your subscription.",
            "For workspace or AI output issues, include the agent used, the task requested, and what needs to be changed.",
            "For login, access, or 2FA issues, include the affected email address and the error you are seeing.",
            "Support request form connection is ready for the next backend/email integration step."
        ],
    },
}

for route, data in pages.items():
    page_dir = APP_DIR / route
    page_dir.mkdir(parents=True, exist_ok=True)
    content = shared_page.replace("export default InfoPage;", f'''export default function Page() {{
  return (
    <InfoPage
      eyebrow="{data["eyebrow"]}"
      title="{data["title"]}"
      body="{data["body"]}"
      bullets={{[
        {", ".join(repr(x) for x in data["bullets"])}
      ]}}
    />
  );
}}''')
    (page_dir / "page.tsx").write_text(content, encoding="utf-8")

print("CLIENT_FOOTER_POLICY_TERMS_SUPPORT_ADDED")
print(f"Backup: {backup}")
print("Created routes: /privacy-policy, /terms-of-service, /support-request")