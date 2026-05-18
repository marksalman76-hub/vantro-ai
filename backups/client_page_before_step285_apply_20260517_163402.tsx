"use client";

import { useEffect, useState } from "react";

type Account = {
  package?: string;
  package_name?: string;
  status?: string;
  package_status?: string;
  active_agents?: string[];
};

const AGENTS = [
  "Product Copywriting Agent",
  "UGC Creative Agent",
  "Product Image Agent",
  "Influencer Collaboration Agent",
  "Analytics Optimisation Agent",
  "General Ecommerce Agent",
  "Competitor Intelligence Agent",
];

export default function ClientPage() {
  const [account, setAccount] = useState<Account | null>(null);
  const [selectedAgents, setSelectedAgents] = useState<string[]>([
    "Product Copywriting Agent",
  ]);

  useEffect(() => {
    fetch("/api/client-me")
      .then((r) => r.json())
      .then((data) => setAccount(data))
      .catch(() => {});
  }, []);

  const creditsRemaining = 500;

  const toggleAgent = (agent: string) => {
    setSelectedAgents((prev) =>
      prev.includes(agent)
        ? prev.filter((a) => a !== agent)
        : [...prev, agent]
    );
  };

  return (
    <main
      style={{
        minHeight: "100vh",
        background: "#f4f7fb",
        color: "#0f172a",
        fontFamily:
          'Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
      }}
    >
      <div
        style={{
          maxWidth: 1450,
          margin: "0 auto",
          padding: "28px 40px 64px",
        }}
      >
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "flex-start",
            gap: 40,
            marginBottom: 28,
          }}
        >
          <div style={{ maxWidth: 820 }}>
            <div
              style={{
                color: "#2563eb",
                fontSize: 13,
                fontWeight: 760,
                letterSpacing: 1.4,
                marginBottom: 18,
                textTransform: "uppercase",
              }}
            >
              Client workspace
            </div>

            <h1
              style={{
                fontSize: 50,
                lineHeight: 1,
                margin: 0,
                letterSpacing: -2.4,
                fontWeight: 760,
              }}
            >
              Premium Demo
              <br />
              Ecommerce Store
            </h1>

            <p
              style={{
                marginTop: 18,
                fontSize: 16,
                lineHeight: 1.5,
                color: "#475569",
                maxWidth: 840,
              }}
            >
              Run premium ecommerce AI agents, generate governed outputs,
              manage execution workflows, and produce commercial-grade
              deliverables.
            </p>
          </div>

          <div
            style={{
              background: "white",
              borderRadius: 999,
              padding: "18px 28px",
              boxShadow: "0 8px 30px rgba(15,23,42,.06)",
              border: "1px solid rgba(226,232,240,.9)",
              fontWeight: 700,
              fontSize: 14.5,
            }}
          >
            ● Local workspace
          </div>
        </div>

        <div
          style={{
            display: "flex",
            gap: 24,
            alignItems: "center",
            flexWrap: "wrap",
            marginBottom: 26,
            color: "#0f172a",
          }}
        >
          {[
            ["Package", "Premium Demo"],
            ["Credits", String(creditsRemaining)],
            ["Status", "active"],
            ["Agents", String(account?.active_agents?.length || 7)],
          ].map(([label, value]) => (
            <div
              key={label}
              style={{
                display: "flex",
                alignItems: "center",
                gap: 12,
              }}
            >
              <div
                style={{
                  width: 9,
                  height: 9,
                  borderRadius: 999,
                  background: "#2563eb",
                }}
              />

              <div
                style={{
                  color: "#64748b",
                  fontSize: 14,
                }}
              >
                {label}
              </div>

              <div
                style={{
                  fontWeight: 700,
                  fontSize: 21,
                  letterSpacing: -0.5,
                }}
              >
                {value}
              </div>
            </div>
          ))}
        </div>

        <section
          style={{
            background: "rgba(255,255,255,.82)",
            borderRadius: 30,
            padding: 30,
            backdropFilter: "blur(12px)",
            boxShadow: "0 10px 28px rgba(15,23,42,.04)",
            marginBottom: 36,
          }}
        >
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "flex-start",
              gap: 30,
              marginBottom: 28,
            }}
          >
            <div>
              <div
                style={{
                  color: "#2563eb",
                  fontSize: 13,
                  fontWeight: 760,
                  letterSpacing: 1.3,
                  marginBottom: 14,
                  textTransform: "uppercase",
                }}
              >
                Business profile intelligence
              </div>

              <h2
                style={{
                  margin: 0,
                  fontSize: 26,
                  letterSpacing: -1.2,
                  lineHeight: 1.05,
                }}
              >
                Store context for smarter agent outputs
              </h2>

              <p
                style={{
                  marginTop: 18,
                  fontSize: 16,
                  color: "#64748b",
                  maxWidth: 820,
                  lineHeight: 1.5,
                }}
              >
                Add business context once so every active AI agent can produce
                more accurate campaigns, creative assets, copy, positioning, and
                execution recommendations.
              </p>
            </div>

            <div
              style={{
                background: "#eff6ff",
                color: "#2563eb",
                padding: "14px 20px",
                borderRadius: 999,
                fontWeight: 700,
                fontSize: 14,
                whiteSpace: "nowrap",
              }}
            >
              ✓ Applied to execution
            </div>
          </div>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit,minmax(220px,1fr))",
              gap: 14,
            }}
          >
            {[
              ["Business niche", "Luxury skincare, supplements, fashion, pet products"],
              ["Products & services", "Main products, bundles, offers"],
              ["Target audience", "Customer type, location, needs"],
              ["Competitors", "Competitor names, websites, market examples"],
              ["Offers", "Current promotions, bundles, guarantees"],
              ["Brand voice", "Premium, playful, clinical, bold, friendly"],
              ["Positioning", "Why customers should choose you"],
              ["Goals", "Sales, launches, retention, growth"],
            ].map(([label, value]) => (
              <div key={label}>
                <div
                  style={{
                    fontSize: 13,
                    color: "#64748b",
                    marginBottom: 10,
                    fontWeight: 600,
                  }}
                >
                  {label}
                </div>

                <textarea
                  defaultValue={value}
                  rows={3}
                  style={{
                    width: "100%",
                    resize: "none",
                    borderRadius: 16,
                    border: "1px solid rgba(226,232,240,.7)",
                    background: "rgba(255,255,255,.82)",
                    padding: "15px 16px",
                    fontSize: 14.5,
                    lineHeight: 1.5,
                    color: "#0f172a",
                    outline: "none",
                    boxSizing: "border-box",
                    fontFamily: "inherit",
                  }}
                />
              </div>
            ))}
          </div>
        </section>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "minmax(390px,.9fr) minmax(520px,1.1fr)",
            gap: 24,
            alignItems: "start",
          }}
        >
          <section
            style={{
              background: "rgba(255,255,255,.72)",
              borderRadius: 36,
              padding: 30,
              boxShadow: "0 18px 45px rgba(15,23,42,.05)",
            }}
          >
            <h2
              style={{
                margin: 0,
                fontSize: 26,
                letterSpacing: -1.7,
                marginBottom: 26,
              }}
            >
              Run AI Agent
            </h2>

            <div
              style={{
                color: "#64748b",
                fontWeight: 600,
                marginBottom: 18,
                fontSize: 14,
              }}
            >
              Active agents
            </div>

            <div
              style={{
                display: "flex",
                flexDirection: "column",
                gap: 12,
                maxHeight: 340,
                overflowY: "auto",
                paddingRight: 6,
              }}
            >
              {AGENTS.map((agent) => {
                const active = selectedAgents.includes(agent);

                return (
                  <button
                    key={agent}
                    onClick={() => toggleAgent(agent)}
                    style={{
                      border: "none",
                      background: active ? "#2563eb" : "rgba(255,255,255,.72)",
                      color: active ? "white" : "#0f172a",
                      padding: "15px 16px",
                      borderRadius: 16,
                      cursor: "pointer",
                      textAlign: "left",
                      fontSize: 16,
                      fontWeight: 600,
                      transition: ".2s",
                      boxShadow: active
                        ? "0 10px 24px rgba(37,99,235,.18)"
                        : "0 2px 10px rgba(15,23,42,.03)",
                    }}
                  >
                    {agent}
                  </button>
                );
              })}
            </div>

            <div
              style={{
                marginTop: 28,
                color: "#64748b",
                fontSize: 14,
                fontWeight: 600,
                marginBottom: 14,
              }}
            >
              Task
            </div>

            <textarea
              defaultValue="Create premium ecommerce campaign assets for a luxury skincare product launch."
              style={{
                width: "100%",
                minHeight: 160,
                resize: "none",
                borderRadius: 24,
                border: "1px solid #dbe3ee",
                background: "white",
                padding: "22px",
                fontSize: 16,
                lineHeight: 1.5,
                boxSizing: "border-box",
                fontFamily: "inherit",
              }}
            />

            <button
              style={{
                marginTop: 18,
                width: "100%",
                border: "none",
                borderRadius: 22,
                background: "linear-gradient(135deg,#2563eb,#06b6d4)",
                color: "white",
                padding: "18px 22px",
                fontWeight: 760,
                fontSize: 16,
                cursor: "pointer",
                boxShadow: "0 12px 28px rgba(37,99,235,.18)",
              }}
            >
              Run Agent
            </button>
          </section>

          <section
            style={{
              background: "rgba(255,255,255,.72)",
              borderRadius: 36,
              padding: 30,
              minHeight: 620,
              boxShadow: "0 18px 45px rgba(15,23,42,.05)",
            }}
          >
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                marginBottom: 28,
              }}
            >
              <div>
                <div
                  style={{
                    color: "#2563eb",
                    fontWeight: 760,
                    fontSize: 13,
                    letterSpacing: 1.3,
                    textTransform: "uppercase",
                    marginBottom: 12,
                  }}
                >
                  Execution output viewer
                </div>

                <h2
                  style={{
                    margin: 0,
                    fontSize: 36,
                    letterSpacing: -1.4,
                    lineHeight: 1,
                  }}
                >
                  Ready for premium execution
                </h2>
              </div>

              <div
                style={{
                  background: "white",
                  borderRadius: 999,
                  padding: "14px 18px",
                  fontWeight: 700,
                  fontSize: 14,
                  color: "#64748b",
                }}
              >
                Live workspace
              </div>
            </div>

            <div
              style={{
                minHeight: 430,
                borderRadius: 32,
                background:
                  "linear-gradient(180deg,rgba(255,255,255,.96),rgba(248,250,252,.9))",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                textAlign: "center",
                padding: 40,
              }}
            >
              <div style={{ maxWidth: 620 }}>
                <div
                  style={{
                    fontSize: 26,
                    fontWeight: 760,
                    letterSpacing: -1.4,
                    marginBottom: 20,
                  }}
                >
                  Premium deliverables will appear here
                </div>

                <div
                  style={{
                    color: "#64748b",
                    fontSize: 16,
                    lineHeight: 1.8,
                  }}
                >
                  Campaign outputs, approvals, execution flows, workflow
                  results, creative assets, billing events, and governed
                  automation actions will appear in this workspace after
                  execution.
                </div>
              </div>
            </div>
          </section>
        </div>
      </div>
    </main>
  );
}
