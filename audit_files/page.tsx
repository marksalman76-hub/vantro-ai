"use client";

import React, { useEffect, useMemo, useState } from "react";

const OWNER_FREE_CLIENT_WORKSPACE_IDS = new Set([
  "client_demo_001",
  "owner_free_client",
  "owner_test_workspace",
]);

function isOwnerFreeClientWorkspace(value: unknown): boolean {
  return OWNER_FREE_CLIENT_WORKSPACE_IDS.has(String(value || "").trim());
}

function normaliseBillingIntent(value: string | null): string {
  const intent = String(value || "manage_billing").trim().toLowerCase();
  if (intent === "upgrade") return "upgrade";
  if (intent === "buy_credits" || intent === "credits" || intent === "buy-more-credits") return "buy_credits";
  if (intent === "payment_update" || intent === "update_payment") return "payment_update";
  return "manage_billing";
}

export default function ClientBillingPage() {
  const [darkModeEnabled, setDarkModeEnabled] = useState(false);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [workspaceId, setWorkspaceId] = useState("");

  const ownerFreeWorkspace = useMemo(() => isOwnerFreeClientWorkspace(workspaceId), [workspaceId]);

  useEffect(() => {
    try {
      const savedTheme = window.localStorage.getItem("client_workspace_dark_mode");
      setDarkModeEnabled(savedTheme === "dark");

      const savedWorkspace =
        window.localStorage.getItem("client_workspace_id") ||
        window.localStorage.getItem("tenant_id") ||
        window.localStorage.getItem("client_tenant_id") ||
        "";
      if (savedWorkspace) setWorkspaceId(savedWorkspace);
    } catch {}

    fetch("/api/client-me", { cache: "no-store", credentials: "include" })
      .then((response) => response.json())
      .then((data) => {
        const nextWorkspaceId =
          data?.tenant_id ||
          data?.tenantId ||
          data?.workspace_id ||
          data?.workspaceId ||
          data?.client_id ||
          data?.clientId ||
          "";
        if (nextWorkspaceId) setWorkspaceId(String(nextWorkspaceId));
      })
      .catch(() => {});
  }, []);

  async function openSecureBilling() {
    setLoading(true);
    setMessage("");

    if (ownerFreeWorkspace) {
      setMessage("Owner free workspace exception active. Unlimited testing credits are enabled for this workspace only.");
      setLoading(false);
      return;
    }

    try {
      const intent = normaliseBillingIntent(new URLSearchParams(window.location.search).get("intent"));

      const response = await fetch("/api/billing-checkout", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({
          mode: intent,
          checkout_type: intent,
          intent,
          return_url: `${window.location.origin}/client`,
        }),
      });

      const data = await response.json().catch(() => ({}));
      const redirectUrl = data?.url || data?.checkout_url || data?.portal_url;

      if (redirectUrl) {
        window.location.href = redirectUrl;
        return;
      }

      setMessage("Secure Stripe billing could not be opened. Please try again or contact support.");
    } catch {
      setMessage("Secure Stripe billing could not be opened. Please try again or contact support.");
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
          Billing and workspace credits
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
          {ownerFreeWorkspace
            ? "This owner-deployed free workspace is billing-exempt and uses unlimited testing credits."
            : "Upgrade plans, buy credits, and manage billing are handled through the secure Stripe billing connection."}
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
            {ownerFreeWorkspace
              ? "Billing actions are disabled for this owner-deployed free workspace only."
              : "Stripe billing is required for this client workspace."}
          </div>

          <button
            type="button"
            onClick={openSecureBilling}
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
            {loading
              ? "Opening secure billing..."
              : ownerFreeWorkspace
                ? "Billing unavailable for owner free workspace"
                : "Open secure billing"}
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
