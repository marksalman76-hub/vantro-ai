import { cookies } from "next/headers";
import PortalNav from "@/components/PortalNav";

const BACKEND_URL =
  process.env.BACKEND_URL || "https://ecommerce-ai-agent-platform-1.onrender.com";

type ClientAccount = {
  tenant_id: string;
  email: string;
  company_name?: string;
  package?: string;
  active_agents?: string[];
  status?: string;
  created_at?: string;
  activated_at?: string;
  monthly_credits?: number;
  credits_used?: number;
  credits_remaining?: number;
};

async function getClientAccount() {
  const cookieStore = await cookies();
  const sessionToken = cookieStore.get("client_session")?.value;

  if (!sessionToken) {
    return null;
  }

  try {
    const response = await fetch(
      `${BACKEND_URL}/client/me?session_token=${encodeURIComponent(sessionToken)}`,
      { cache: "no-store" }
    );

    if (!response.ok) {
      return null;
    }

    const result = await response.json();

    if (!result.success || !result.account) {
      return null;
    }

    return result.account as ClientAccount;
  } catch {
    return null;
  }
}

async function getBackendHealth() {
  try {
    const response = await fetch(`${BACKEND_URL}/health`, {
      cache: "no-store",
    });

    if (!response.ok) {
      return {
        ok: false,
        status: response.status,
      };
    }

    return {
      ok: true,
      status: response.status,
    };
  } catch {
    return {
      ok: false,
      status: 0,
    };
  }
}

function titleCaseAgent(agent: string) {
  return agent
    .replace(/_/g, " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

export default async function ClientPortalPage() {
  const [health, account] = await Promise.all([
    getBackendHealth(),
    getClientAccount(),
  ]);

  const activeAgents = account?.active_agents || [];

  const monthlyCreditAllocation = account?.monthly_credits ?? 0;
  const creditsUsed = account?.credits_used ?? 0;
  const creditsRemaining =
    account?.credits_remaining ?? Math.max(monthlyCreditAllocation - creditsUsed, 0);
  const usagePercentage =
    monthlyCreditAllocation > 0
      ? Math.round((creditsUsed / monthlyCreditAllocation) * 100)
      : 0;

  return (
    <main
      style={{
        minHeight: "100vh",
        padding: "56px 24px",
        background:
          "linear-gradient(135deg, #f8fafc 0%, #eef2ff 48%, #e0f2fe 100%)",
        color: "#0f172a",
        fontFamily:
          "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif",
      }}
    >
      <section style={{ maxWidth: 1180, margin: "0 auto" }}>
        <PortalNav />

        <p style={{ color: "#2563eb", fontWeight: 800, letterSpacing: 1 }}>
          CUSTOMER PORTAL
        </p>

        <h1 style={{ fontSize: 54, lineHeight: 1.05, margin: "16px 0" }}>
          {account?.company_name || "Ecommerce AI Agent Workspace"}
        </h1>

        <p style={{ color: "#475569", fontSize: 18, maxWidth: 780 }}>
          Client-facing workspace for launching governed ecommerce AI workflows,
          reviewing outputs, tracking execution readiness, and keeping sensitive
          actions under owner approval.
        </p>

        <div
          style={{
            marginTop: 30,
            display: "inline-flex",
            alignItems: "center",
            gap: 10,
            padding: "12px 16px",
            borderRadius: 999,
            background: health.ok
              ? "rgba(22, 163, 74, .12)"
              : "rgba(239, 68, 68, .12)",
            border: health.ok
              ? "1px solid rgba(22, 163, 74, .35)"
              : "1px solid rgba(239, 68, 68, .35)",
            color: health.ok ? "#166534" : "#991b1b",
            fontWeight: 800,
          }}
        >
          <span>{health.ok ? "● Platform online" : "● Platform unavailable"}</span>
          <span style={{ opacity: 0.8 }}>Status: {health.status}</span>
        </div>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))",
            gap: 18,
            marginTop: 38,
          }}
        >
          {[
            ["Account Email", account?.email || "Not available"],
            ["Package", account?.package || "Not assigned"],
            ["Account Status", account?.status || "Unknown"],
            ["Active Agents", String(activeAgents.length)],
          ].map(([label, value]) => (
            <div
              key={label}
              style={{
                padding: 22,
                borderRadius: 20,
                background: "rgba(255,255,255,.88)",
                border: "1px solid rgba(148,163,184,.32)",
                boxShadow: "0 24px 80px rgba(15,23,42,.08)",
              }}
            >
              <div style={{ color: "#64748b", fontSize: 13 }}>{label}</div>
              <strong style={{ display: "block", marginTop: 8, fontSize: 18 }}>
                {value}
              </strong>
            </div>
          ))}
        </div>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))",
            gap: 18,
            marginTop: 26,
          }}
        >
          {[
            ["Monthly Credit Allocation", `${monthlyCreditAllocation} credits`],
            ["Credits Used", `${creditsUsed} credits`],
            ["Credits Remaining", `${creditsRemaining} credits`],
            ["Usage", `${usagePercentage}%`],
          ].map(([label, value]) => (
            <div
              key={label}
              style={{
                padding: 22,
                borderRadius: 20,
                background: "#0f172a",
                color: "#e2e8f0",
                border: "1px solid rgba(148,163,184,.22)",
              }}
            >
              <div style={{ color: "#94a3b8", fontSize: 13 }}>{label}</div>
              <strong style={{ display: "block", marginTop: 8, fontSize: 18 }}>
                {value}
              </strong>
            </div>
          ))}
        </div>

        <div
          style={{
            marginTop: 26,
            padding: 24,
            borderRadius: 20,
            background: "rgba(255,255,255,.9)",
            border: "1px solid rgba(148,163,184,.32)",
          }}
        >
          <strong style={{ fontSize: 20 }}>Credit top-up options</strong>
          <p style={{ color: "#64748b", lineHeight: 1.7 }}>
            Credit top-ups will appear here once owner/admin credit assignment
            and Stripe top-up products are connected. This space is reserved for
            monthly allocation, manual owner-issued credits, and paid top-up
            bundles.
          </p>
        </div>

        <div
          style={{
            marginTop: 38,
          }}
        >
          <h2 style={{ fontSize: 30 }}>Available AI Agents</h2>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
              gap: 18,
              marginTop: 18,
            }}
          >
            {activeAgents.length > 0 ? (
              activeAgents.map((agent) => (
                <div
                  key={agent}
                  style={{
                    padding: 24,
                    borderRadius: 20,
                    background: "rgba(255,255,255,.86)",
                    border: "1px solid rgba(148,163,184,.32)",
                    boxShadow: "0 24px 80px rgba(15,23,42,.08)",
                  }}
                >
                  <strong style={{ display: "block", fontSize: 20 }}>
                    {titleCaseAgent(agent)}
                  </strong>
                  <p
                    style={{
                      color: "#64748b",
                      lineHeight: 1.65,
                      marginTop: 10,
                    }}
                  >
                    Available under this client account. Execution controls will
                    be connected to governed runtime in the next phase.
                  </p>
                </div>
              ))
            ) : (
              <div
                style={{
                  padding: 24,
                  borderRadius: 20,
                  background: "rgba(255,255,255,.86)",
                  border: "1px solid rgba(148,163,184,.32)",
                }}
              >
                No active agents are currently assigned to this account.
              </div>
            )}
          </div>
        </div>

        <div
          style={{
            marginTop: 42,
            padding: 24,
            borderRadius: 20,
            background: "#0f172a",
            color: "#e2e8f0",
          }}
        >
          <strong>Governance notice</strong>
          <p style={{ color: "#cbd5e1", lineHeight: 1.7 }}>
            Spending increases, scaling actions, contracts, paid collaborations,
            and authority-sensitive decisions require owner approval before
            execution.
          </p>
        </div>
      </section>
    </main>
  );
}
