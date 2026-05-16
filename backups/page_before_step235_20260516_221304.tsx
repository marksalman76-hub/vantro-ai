"use client";

import { useEffect, useMemo, useState } from "react";

type RuntimePayload = {
  success?: boolean;
  generated_at?: string;
  runtime?: any;
  execution_summary?: any;
  billing_summary?: any;
  deployment_summary?: any;
  security_summary?: any;
  health?: any;
};

function StatCard({
  label,
  value,
}: {
  label: string;
  value: string | number;
}) {
  return (
    <div
      style={{
        background: "rgba(15,23,42,.86)",
        border: "1px solid rgba(148,163,184,.16)",
        borderRadius: 20,
        padding: 22,
      }}
    >
      <div
        style={{
          color: "#94a3b8",
          fontSize: 13,
        }}
      >
        {label}
      </div>

      <strong
        style={{
          display: "block",
          marginTop: 10,
          fontSize: 28,
        }}
      >
        {value}
      </strong>
    </div>
  );
}

function JsonBlock({ value }: { value: any }) {
  return (
    <pre
      style={{
        background: "#020617",
        borderRadius: 18,
        padding: 20,
        overflow: "auto",
        border: "1px solid rgba(148,163,184,.12)",
        color: "#cbd5e1",
        fontSize: 13,
        lineHeight: 1.6,
        whiteSpace: "pre-wrap",
      }}
    >
      {JSON.stringify(value, null, 2)}
    </pre>
  );
}

export default function AdminPage() {
  const [runtime, setRuntime] = useState<RuntimePayload | null>(null);
  const [loading, setLoading] = useState(true);

  async function loadRuntime() {
    try {
      const response = await fetch("/api/admin-runtime", {
        cache: "no-store",
      });

      const data = await response.json();

      setRuntime(data);
    } catch {
      setRuntime(null);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadRuntime();
  }, []);

  const runtimeStatus = useMemo(() => {
    return runtime?.runtime?.platform_status || "offline";
  }, [runtime]);

  return (
    <main
      style={{
        minHeight: "100vh",
        background:
          "linear-gradient(135deg,#020617 0%,#0f172a 45%,#111827 100%)",
        color: "#f8fafc",
        padding: "42px 24px",
        fontFamily:
          "Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif",
      }}
    >
      <section
        style={{
          maxWidth: 1440,
          margin: "0 auto",
        }}
      >
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            gap: 20,
            flexWrap: "wrap",
            alignItems: "center",
          }}
        >
          <div>
            <div
              style={{
                color: "#38bdf8",
                fontWeight: 800,
                letterSpacing: 1,
              }}
            >
              OWNER COMMAND CENTRE
            </div>

            <h1
              style={{
                fontSize: 56,
                lineHeight: 1.02,
                marginTop: 12,
              }}
            >
              Ecommerce AI Agent Platform
            </h1>

            <p
              style={{
                color: "#94a3b8",
                marginTop: 14,
                maxWidth: 900,
                lineHeight: 1.7,
              }}
            >
              Live operational command centre for governed execution,
              premium output monitoring, Stripe billing runtime,
              client activity, workflow visibility, and deployment readiness.
            </p>
          </div>

          <div
            style={{
              padding: "14px 18px",
              borderRadius: 999,
              background:
                runtimeStatus === "online"
                  ? "rgba(34,197,94,.12)"
                  : "rgba(239,68,68,.12)",
              border:
                runtimeStatus === "online"
                  ? "1px solid rgba(34,197,94,.3)"
                  : "1px solid rgba(239,68,68,.3)",
              fontWeight: 800,
            }}
          >
            Runtime: {runtimeStatus}
          </div>
        </div>

        {loading ? (
          <div
            style={{
              marginTop: 40,
              color: "#94a3b8",
            }}
          >
            Loading admin runtime...
          </div>
        ) : null}

        {runtime ? (
          <>
            <div
              style={{
                display: "grid",
                gridTemplateColumns:
                  "repeat(auto-fit,minmax(240px,1fr))",
                gap: 18,
                marginTop: 34,
              }}
            >
              <StatCard
                label="Successful Executions"
                value={
                  runtime.execution_summary?.successful_executions || 0
                }
              />

              <StatCard
                label="Pending Approvals"
                value={
                  runtime.execution_summary?.pending_approvals || 0
                }
              />

              <StatCard
                label="Blocked Executions"
                value={
                  runtime.execution_summary?.blocked_executions || 0
                }
              />

              <StatCard
                label="Premium Outputs"
                value={
                  runtime.execution_summary
                    ?.premium_outputs_generated || 0
                }
              />

              <StatCard
                label="Active Subscriptions"
                value={
                  runtime.billing_summary?.subscriptions_active || 0
                }
              />

              <StatCard
                label="Credits Remaining"
                value={
                  runtime.billing_summary?.credits_remaining || 0
                }
              />
            </div>

            <div
              style={{
                display: "grid",
                gridTemplateColumns:
                  "repeat(auto-fit,minmax(460px,1fr))",
                gap: 24,
                marginTop: 34,
              }}
            >
              <div
                style={{
                  background: "rgba(15,23,42,.82)",
                  border: "1px solid rgba(148,163,184,.14)",
                  borderRadius: 22,
                  padding: 24,
                }}
              >
                <h2 style={{ fontSize: 28 }}>
                  Runtime Summary
                </h2>

                <div
                  style={{
                    marginTop: 18,
                  }}
                >
                  <JsonBlock value={runtime.runtime} />
                </div>
              </div>

              <div
                style={{
                  background: "rgba(15,23,42,.82)",
                  border: "1px solid rgba(148,163,184,.14)",
                  borderRadius: 22,
                  padding: 24,
                }}
              >
                <h2 style={{ fontSize: 28 }}>
                  Billing Runtime
                </h2>

                <div
                  style={{
                    marginTop: 18,
                  }}
                >
                  <JsonBlock value={runtime.billing_summary} />
                </div>
              </div>

              <div
                style={{
                  background: "rgba(15,23,42,.82)",
                  border: "1px solid rgba(148,163,184,.14)",
                  borderRadius: 22,
                  padding: 24,
                }}
              >
                <h2 style={{ fontSize: 28 }}>
                  Deployment Runtime
                </h2>

                <div
                  style={{
                    marginTop: 18,
                  }}
                >
                  <JsonBlock value={runtime.deployment_summary} />
                </div>
              </div>

              <div
                style={{
                  background: "rgba(15,23,42,.82)",
                  border: "1px solid rgba(148,163,184,.14)",
                  borderRadius: 22,
                  padding: 24,
                }}
              >
                <h2 style={{ fontSize: 28 }}>
                  Security Runtime
                </h2>

                <div
                  style={{
                    marginTop: 18,
                  }}
                >
                  <JsonBlock value={runtime.security_summary} />
                </div>
              </div>
            </div>

            <div
              style={{
                marginTop: 34,
                background: "rgba(15,23,42,.82)",
                border: "1px solid rgba(148,163,184,.14)",
                borderRadius: 22,
                padding: 24,
              }}
            >
              <h2 style={{ fontSize: 28 }}>
                Backend Health Payload
              </h2>

              <div
                style={{
                  marginTop: 18,
                }}
              >
                <JsonBlock value={runtime.health} />
              </div>
            </div>
          </>
        ) : (
          <div
            style={{
              marginTop: 40,
              padding: 24,
              borderRadius: 18,
              background: "rgba(239,68,68,.12)",
              border: "1px solid rgba(239,68,68,.22)",
              color: "#fecaca",
            }}
          >
            Admin runtime unavailable.
          </div>
        )}
      </section>
    </main>
  );
}
