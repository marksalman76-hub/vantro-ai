"use client";

import React, { useEffect, useState } from "react";

export default function ClientBillingPage() {
  const [darkModeEnabled, setDarkModeEnabled] = useState(false);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  useEffect(() => {
    try {
      const savedTheme = window.localStorage.getItem("client_workspace_dark_mode");
      setDarkModeEnabled(savedTheme === "dark");
    } catch {}
  }, []);

  async function openPaymentUpdate() {
    setLoading(true);
    setMessage("");

    try {
      const response = await fetch("/api/billing-checkout", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({
          mode: "payment_update",
          checkout_type: "payment_update",
          return_url: `${window.location.origin}/client`,
        }),
      });

      const data = await response.json().catch(() => ({}));
      const redirectUrl = data?.url || data?.checkout_url || data?.portal_url;

      if (redirectUrl) {
        window.location.href = redirectUrl;
        return;
      }

      setMessage("Owner test workspace. Unlimited testing credits are active. No billing required for this workspace.");
    } catch {
      setMessage("Payment update could not be opened. Please try again.");
    } finally {
      setLoading(false);
    }
  }

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
          maxWidth: 820,
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
        <div
          style={{
            color: darkModeEnabled ? "#a5b4fc" : "#4f46e5",
            fontSize: 12,
            fontWeight: 900,
            letterSpacing: 1.3,
            textTransform: "uppercase",
            marginBottom: 10,
          }}
        >
          Billing
        </div>

        <h1 style={{ margin: 0, fontSize: 34, letterSpacing: -1.1 }}>
          Owner test workspace billing
        </h1>

        <p
          style={{
            margin: "12px 0 0",
            color: darkModeEnabled ? "#94a3b8" : "#64748b",
            fontSize: 15,
            lineHeight: 1.55,
            maxWidth: 650,
          }}
        >
          This workspace is running in owner test mode with unlimited testing credits. No billing is required for this workspace.
        </p>

        <div
          style={{
            marginTop: 24,
            borderRadius: 18,
            padding: 18,
            background: darkModeEnabled ? "rgba(12,24,49,.92)" : "#f8fafc",
            border: darkModeEnabled ? "1px solid rgba(99,102,241,.24)" : "1px solid #e5eaf2",
          }}
        >
          <div style={{ fontWeight: 900, marginBottom: 6 }}>Billing status</div>
          <div style={{ color: darkModeEnabled ? "#94a3b8" : "#64748b", fontSize: 13, lineHeight: 1.45 }}>
            Billing actions are disabled for this owner test workspace.
          </div>

          <button
            type="button"
            onClick={openPaymentUpdate}
            disabled={loading}
            style={{
              marginTop: 16,
              border: 0,
              borderRadius: 14,
              padding: "12px 16px",
              background: loading ? "#94a3b8" : "linear-gradient(135deg,#4f46e5,#7c3aed)",
              color: "#ffffff",
              fontWeight: 900,
              cursor: loading ? "not-allowed" : "pointer",
              boxShadow: "0 14px 34px rgba(79,70,229,.28)",
            }}
          >
            {loading ? "Checking billing status..." : "Billing disabled for owner test"}
          </button>

          <button
            type="button"
            onClick={() => {
              window.location.href = "/client";
            }}
            style={{
              marginLeft: 10,
              borderRadius: 14,
              padding: "11px 14px",
              border: darkModeEnabled ? "1px solid rgba(129,140,248,.28)" : "1px solid #e5eaf2",
              background: darkModeEnabled ? "rgba(15,23,42,.92)" : "#ffffff",
              color: darkModeEnabled ? "#e2e8f0" : "#334155",
              fontWeight: 850,
              cursor: "pointer",
            }}
          >
            Back to workspace
          </button>

          {message ? (
            <div
              style={{
                marginTop: 14,
                color: "#f59e0b",
                fontSize: 13,
                fontWeight: 800,
              }}
            >
              {message}
            </div>
          ) : null}
        </div>
      </section>
    </main>
  );
}
