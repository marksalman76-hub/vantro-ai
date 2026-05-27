from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
TARGET = ROOT / "frontend" / "src" / "app" / "support-request" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

backup = BACKUP_DIR / f"support_request_page_before_clickable_form_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
shutil.copy2(TARGET, backup)

TARGET.write_text(r'''"use client";

import React, { useEffect, useState } from "react";

export default function SupportRequestPage() {
  const [darkModeEnabled, setDarkModeEnabled] = useState(false);
  const [form, setForm] = useState({
    businessName: "",
    email: "",
    category: "Billing / payment",
    message: "",
  });
  const [sent, setSent] = useState(false);

  useEffect(() => {
    try {
      setDarkModeEnabled(window.localStorage.getItem("client_workspace_dark_mode") === "dark");
    } catch {}
  }, []);

  const textColor = darkModeEnabled ? "#f8fafc" : "#0f172a";
  const mutedColor = darkModeEnabled ? "#94a3b8" : "#64748b";
  const cardBg = darkModeEnabled ? "linear-gradient(180deg, rgba(10,22,46,.96), rgba(7,16,34,.98))" : "#ffffff";
  const inputBg = darkModeEnabled ? "rgba(3,10,24,.86)" : "#ffffff";
  const borderColor = darkModeEnabled ? "rgba(129,140,248,.28)" : "#e5eaf2";

  function updateField(key: string, value: string) {
    setForm((previous) => ({ ...previous, [key]: value }));
    setSent(false);
  }

  function submitSupportRequest(event: React.FormEvent) {
    event.preventDefault();

    const subject = encodeURIComponent(`Support request - ${form.category}`);
    const body = encodeURIComponent(
      `Business name: ${form.businessName}\nEmail: ${form.email}\nCategory: ${form.category}\n\nRequest:\n${form.message}`
    );

    setSent(true);
    window.location.href = `mailto:support@trance-formation.com.au?subject=${subject}&body=${body}`;
  }

  return (
    <main
      style={{
        minHeight: "100vh",
        background: darkModeEnabled
          ? "radial-gradient(circle at 18% 0%, rgba(79,70,229,.20), transparent 28%), radial-gradient(circle at 92% 6%, rgba(124,58,237,.16), transparent 30%), linear-gradient(180deg, #050b18 0%, #071120 48%, #050b18 100%)"
          : "#f4f7fb",
        color: textColor,
        fontFamily: 'Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
        padding: "clamp(24px,4vw,54px)",
        boxSizing: "border-box",
      }}
    >
      <section
        style={{
          maxWidth: 920,
          margin: "0 auto",
          borderRadius: 26,
          padding: "clamp(24px,4vw,38px)",
          background: cardBg,
          border: `1px solid ${borderColor}`,
          boxShadow: darkModeEnabled ? "0 24px 80px rgba(0,0,0,.34)" : "0 24px 70px rgba(15,23,42,.08)",
        }}
      >
        <div style={{ color: darkModeEnabled ? "#a5b4fc" : "#4f46e5", fontSize: 12, fontWeight: 900, letterSpacing: 1.3, textTransform: "uppercase", marginBottom: 10 }}>
          Support
        </div>

        <h1 style={{ margin: 0, fontSize: 34, letterSpacing: -1.1 }}>Contact us / Support request</h1>

        <p style={{ margin: "14px 0 0", color: mutedColor, fontSize: 15, lineHeight: 1.6 }}>
          Send a support request for billing, account access, workspace setup, integrations, AI outputs, or subscription support.
        </p>

        <form onSubmit={submitSupportRequest} style={{ marginTop: 24, display: "grid", gap: 14 }}>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(220px,1fr))", gap: 12 }}>
            <label style={{ display: "grid", gap: 7, fontSize: 12, fontWeight: 900, color: darkModeEnabled ? "#cbd5e1" : "#334155" }}>
              Business name
              <input
                value={form.businessName}
                onChange={(event) => updateField("businessName", event.target.value)}
                placeholder="Your business name"
                required
                style={{
                  height: 42,
                  borderRadius: 12,
                  border: `1px solid ${borderColor}`,
                  background: inputBg,
                  color: textColor,
                  padding: "0 12px",
                  font: "inherit",
                }}
              />
            </label>

            <label style={{ display: "grid", gap: 7, fontSize: 12, fontWeight: 900, color: darkModeEnabled ? "#cbd5e1" : "#334155" }}>
              Email
              <input
                type="email"
                value={form.email}
                onChange={(event) => updateField("email", event.target.value)}
                placeholder="you@example.com"
                required
                style={{
                  height: 42,
                  borderRadius: 12,
                  border: `1px solid ${borderColor}`,
                  background: inputBg,
                  color: textColor,
                  padding: "0 12px",
                  font: "inherit",
                }}
              />
            </label>
          </div>

          <label style={{ display: "grid", gap: 7, fontSize: 12, fontWeight: 900, color: darkModeEnabled ? "#cbd5e1" : "#334155" }}>
            Request type
            <select
              value={form.category}
              onChange={(event) => updateField("category", event.target.value)}
              style={{
                height: 42,
                borderRadius: 12,
                border: `1px solid ${borderColor}`,
                background: inputBg,
                color: textColor,
                padding: "0 12px",
                font: "inherit",
              }}
            >
              <option>Billing / payment</option>
              <option>Account access</option>
              <option>Workspace setup</option>
              <option>Integrations</option>
              <option>AI output issue</option>
              <option>Subscription support</option>
              <option>Other</option>
            </select>
          </label>

          <label style={{ display: "grid", gap: 7, fontSize: 12, fontWeight: 900, color: darkModeEnabled ? "#cbd5e1" : "#334155" }}>
            How can we help?
            <textarea
              value={form.message}
              onChange={(event) => updateField("message", event.target.value)}
              placeholder="Describe what you need help with..."
              required
              rows={6}
              style={{
                borderRadius: 14,
                border: `1px solid ${borderColor}`,
                background: inputBg,
                color: textColor,
                padding: 12,
                font: "inherit",
                resize: "vertical",
              }}
            />
          </label>

          <div style={{ display: "flex", gap: 10, flexWrap: "wrap", alignItems: "center" }}>
            <button
              type="submit"
              style={{
                border: 0,
                borderRadius: 14,
                padding: "12px 16px",
                background: "linear-gradient(135deg,#4f46e5,#7c3aed)",
                color: "#ffffff",
                fontWeight: 900,
                cursor: "pointer",
              }}
            >
              Send support request
            </button>

            <a
              href="/client"
              style={{
                borderRadius: 14,
                padding: "11px 14px",
                border: `1px solid ${borderColor}`,
                color: darkModeEnabled ? "#e2e8f0" : "#334155",
                textDecoration: "none",
                fontWeight: 850,
              }}
            >
              Back to workspace
            </a>
          </div>

          {sent ? (
            <div style={{ color: "#22c55e", fontWeight: 900, fontSize: 13 }}>
              Opening your email app with the support request.
            </div>
          ) : null}
        </form>
      </section>
    </main>
  );
}
''', encoding="utf-8")

print("SUPPORT_REQUEST_CLICKABLE_FORM_ADDED")
print(f"Backup: {backup}")