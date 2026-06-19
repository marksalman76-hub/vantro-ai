"use client";

import { useEffect, useMemo, useState } from "react";

type ClientBillingState = {
  planName: string;
  planStatus: string;
  creditsAvailable: number | null;
  creditsUsed: number | null;
  creditsLimit: number | null;
  creditStatus: string;
  loading: boolean;
  error: string | null;
};

function readString(source: any, keys: string[], fallback = "Not available") {
  for (const key of keys) {
    const value = source?.[key];
    if (typeof value === "string" && value.trim()) {
      return value.trim();
    }
  }
  return fallback;
}

function readNumber(source: any, keys: string[]) {
  for (const key of keys) {
    const value = source?.[key];
    if (typeof value === "number" && Number.isFinite(value)) {
      return value;
    }
    if (typeof value === "string" && value.trim() && !Number.isNaN(Number(value))) {
      return Number(value);
    }
  }
  return null;
}

async function readJsonSafely(url: string) {
  try {
    const response = await fetch(url, { cache: "no-store" });
    const body = await response.json().catch(() => ({}));
    return { ok: response.ok, body };
  } catch {
    return { ok: false, body: {} };
  }
}

export default function ClientPlanCreditStatusCard() {
  const [state, setState] = useState<ClientBillingState>({
    planName: "Loading",
    planStatus: "Checking",
    creditsAvailable: null,
    creditsUsed: null,
    creditsLimit: null,
    creditStatus: "Checking",
    loading: true,
    error: null,
  });

  useEffect(() => {
    let cancelled = false;

    async function loadBillingAndCredits() {
      const [billing, credits] = await Promise.all([
        readJsonSafely("/api/billing-subscription-status"),
        readJsonSafely("/api/package-credit-enforcement-status"),
      ]);

      if (cancelled) {
        return;
      }

      const billingBody = billing.body || {};
      const creditBody = credits.body || {};

      const nestedBilling = billingBody.subscription || billingBody.billing || billingBody.data || billingBody;
      const nestedCredits = creditBody.credits || creditBody.package || creditBody.enforcement || creditBody.data || creditBody;

      const planName = readString(
        nestedBilling,
        ["plan_name", "planName", "plan", "package_name", "packageName", "tier", "subscription_plan"],
        "Owner test workspace",
      );

      const planStatus = readString(
        nestedBilling,
        ["status", "subscription_status", "subscriptionStatus", "plan_status", "planStatus"],
        billing.ok ? "Active" : "No billing required",
      );

      const creditsAvailable = readNumber(
        nestedCredits,
        ["available_credits", "availableCredits", "credits_available", "creditsAvailable", "remaining_credits", "remainingCredits", "balance", "credits"],
      );

      const creditsUsed = readNumber(
        nestedCredits,
        ["used_credits", "usedCredits", "credits_used", "creditsUsed"],
      );

      const creditsLimit = readNumber(
        nestedCredits,
        ["credit_limit", "creditLimit", "credits_limit", "creditsLimit", "monthly_credits", "monthlyCredits"],
      );

      const creditStatus = readString(
        nestedCredits,
        ["status", "credit_status", "creditStatus", "enforcement_status", "enforcementStatus"],
        credits.ok ? "Available" : "No billing required",
      );

      setState({
        planName,
        planStatus,
        creditsAvailable,
        creditsUsed,
        creditsLimit,
        creditStatus,
        loading: false,
        error: billing.ok || credits.ok ? null : "No billing required for this workspace.",
      });
    }

    loadBillingAndCredits();

    return () => {
      cancelled = true;
    };
  }, []);

  const creditSummary = useMemo(() => {
    if (state.creditsAvailable !== null) {
      return `${state.creditsAvailable}`;
    }
    if (state.creditsLimit !== null && state.creditsUsed !== null) {
      return `${Math.max(state.creditsLimit - state.creditsUsed, 0)}`;
    }
    return "Unlimited testing credits";
  }, [state.creditsAvailable, state.creditsLimit, state.creditsUsed]);

  const usageSummary = useMemo(() => {
    if (state.creditsUsed !== null && state.creditsLimit !== null) {
      return `${state.creditsUsed} used of ${state.creditsLimit}`;
    }
    if (state.creditsUsed !== null) {
      return `${state.creditsUsed} used`;
    }
    if (state.creditsLimit !== null) {
      return `${state.creditsLimit} included`;
    }
    return "Unlimited testing usage";
  }, [state.creditsLimit, state.creditsUsed]);

  const goToBilling = (intent: "upgrade" | "credits" | "manage") => {
    const params = new URLSearchParams({ intent });
    window.location.href = `/client/billing?${params.toString()}`;
  };

  return (
    <section
      data-client-plan-credit-status-card="true"
      style={{
        margin: "18px 0 24px",
        padding: 22,
        borderRadius: 24,
        border: "1px solid rgba(99, 102, 241, 0.34)",
        background: "linear-gradient(135deg, #081226 0%, #101946 100%)",
        boxShadow: "0 18px 45px rgba(0, 0, 0, 0.24)",
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          gap: 18,
          flexWrap: "wrap",
          alignItems: "flex-start",
        }}
      >
        <div>
          <p
            style={{
              margin: "0 0 8px",
              color: "#8ea7ff",
              fontSize: 12,
              fontWeight: 900,
              letterSpacing: "0.12em",
              textTransform: "uppercase",
            }}
          >
            Plan and credits
          </p>
          <h2 style={{ margin: 0, color: "#ffffff", fontSize: 24, fontWeight: 950 }}>
            Your current access
          </h2>
          <p style={{ margin: "8px 0 0", color: "#9fb1d1", fontSize: 14, lineHeight: 1.6 }}>
            See your active plan, available credits, and billing actions before starting new work.
          </p>
        </div>

        <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
          <button
            type="button"
            onClick={() => goToBilling("upgrade")}
            style={{
              border: 0,
              borderRadius: 999,
              padding: "11px 15px",
              background: "#6d5dfc",
              color: "#ffffff",
              fontWeight: 900,
              cursor: "pointer",
            }}
          >
            Upgrade plan
          </button>
          <button
            type="button"
            onClick={() => goToBilling("credits")}
            style={{
              border: "1px solid rgba(165, 180, 252, 0.45)",
              borderRadius: 999,
              padding: "11px 15px",
              background: "rgba(15, 23, 42, 0.84)",
              color: "#dbeafe",
              fontWeight: 900,
              cursor: "pointer",
            }}
          >
            Buy more credits
          </button>
          <button
            type="button"
            onClick={() => goToBilling("manage")}
            style={{
              border: "1px solid rgba(148, 163, 184, 0.32)",
              borderRadius: 999,
              padding: "11px 15px",
              background: "rgba(15, 23, 42, 0.58)",
              color: "#cbd5e1",
              fontWeight: 850,
              cursor: "pointer",
            }}
          >
            Manage billing
          </button>
        </div>
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(210px, 1fr))",
          gap: 12,
          marginTop: 18,
        }}
      >
        <div style={{ padding: 15, borderRadius: 18, background: "rgba(3, 7, 18, 0.58)", border: "1px solid rgba(148, 163, 184, 0.22)" }}>
          <p style={{ margin: "0 0 6px", color: "#94a3b8", fontSize: 12, fontWeight: 850 }}>Current plan</p>
          <strong style={{ color: "#ffffff", fontSize: 20 }}>{state.loading ? "Loading" : state.planName}</strong>
          <p style={{ margin: "6px 0 0", color: "#9fb1d1", fontSize: 12 }}>Status: {state.planStatus}</p>
        </div>

        <div style={{ padding: 15, borderRadius: 18, background: "rgba(3, 7, 18, 0.58)", border: "1px solid rgba(148, 163, 184, 0.22)" }}>
          <p style={{ margin: "0 0 6px", color: "#94a3b8", fontSize: 12, fontWeight: 850 }}>Available credits</p>
          <strong style={{ color: "#ffffff", fontSize: 20 }}>{state.loading ? "Loading" : creditSummary}</strong>
          <p style={{ margin: "6px 0 0", color: "#9fb1d1", fontSize: 12 }}>{usageSummary}</p>
        </div>

        <div style={{ padding: 15, borderRadius: 18, background: "rgba(3, 7, 18, 0.58)", border: "1px solid rgba(148, 163, 184, 0.22)" }}>
          <p style={{ margin: "0 0 6px", color: "#94a3b8", fontSize: 12, fontWeight: 850 }}>Credit status</p>
          <strong style={{ color: "#ffffff", fontSize: 20 }}>{state.loading ? "Checking" : state.creditStatus}</strong>
          <p style={{ margin: "6px 0 0", color: "#9fb1d1", fontSize: 12 }}>
            Unlimited testing credits are enabled for this owner workspace.
          </p>
        </div>
      </div>

      {state.error ? (
        <p style={{ margin: "14px 0 0", color: "#fbbf24", fontSize: 13 }}>
          {state.error}
        </p>
      ) : null}
    </section>
  );
}
