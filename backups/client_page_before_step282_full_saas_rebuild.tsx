\
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
          padding: "56px 40px 80px",
        }}
      >
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "flex-start",
            gap: 40,
            marginBottom: 44,
          }}
        >
          <div style={{ maxWidth: 820 }}>
            <div
              style={{
                color: "#2563eb",
                fontSize: 13,
                fontWeight: 800,
                letterSpacing: 1.4,
                marginBottom: 18,
                textTransform: "uppercase",
              }}
            >
              Client workspace
            </div>

            <h1
              style={{
                fontSize: 66,
                lineHeight: 1,
                margin: 0,
                letterSpacing: -3.2,
                fontWeight: 800,
              }}
            >
              Premium Demo
              <br />
              Ecommerce Store
            </h1>

            <p
              style={{
                marginTop: 26,
                fontSize: 20,
                lineHeight: 1.7,
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
              fontSize: 15,
            }}
          >
            ● Local workspace
          </div>
        </div>

        <div
          style={{
            display: "flex",
            gap: 34,
            alignItems: "center",
            flexWrap: "wrap",
            marginBottom: 50,
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
                  fontSize: 24,
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
            background: "rgba(255,255,255,.7)",
            borderRadius: 38,
            padding: 38,
            backdropFilter: "blur(12px)",
            boxShadow: "0 20px 50px rgba(15,23,42,.05)",
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
                  fontWeight: 800,
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
                  fontSize: 42,
                  letterSpacing: -1.8,
                  lineHeight: 1.05,
                }}
              >
                Store context for smarter agent outputs
              </h2>

              <p
                style={{
                  marginTop: 18,
                  fontSize: 18,
                  color: "#64748b",
                  maxWidth: 820,
                  lineHeight: 1.7,
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
              gridTemplateColumns: "repeat(5,minmax(0,1fr))",
              gap: 18,
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
                    borderRadius: 20,
                    border: "1px solid #e2e8f0",
                    background: "rgba(255,255,255,.9)",
                    padding: "18px 18px",
                    fontSize: 15,
                    lineHeight: 1.7,
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
            gridTemplateColumns: "420px 1fr",
            gap: 34,
            alignItems: "start",
          }}
        >
          <section
            style={{
              background: "rgba(255,255,255,.72)",
              borderRadius: 36,
              padding: 34,
              boxShadow: "0 18px 45px rgba(15,23,42,.05)",
            }}
          >
            <h2
              style={{
                margin: 0,
                fontSize: 42,
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
                      background: active ? "#2563eb" : "white",
                      color: active ? "white" : "#0f172a",
                      padding: "18px 18px",
                      borderRadius: 18,
                      cursor: "pointer",
                      textAlign: "left",
                      fontSize: 16,
                      fontWeight: 600,
                      transition: ".2s",
                      boxShadow: active
                        ? "0 12px 30px rgba(37,99,235,.22)"
                        : "0 4px 14px rgba(15,23,42,.04)",
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
                lineHeight: 1.7,
                boxSizing: "border-box",
                fontFamily: "inherit",
              }}
            />

            <button
              style={{
                marginTop: 26,
                width: "100%",
                border: "none",
                borderRadius: 22,
                background: "linear-gradient(135deg,#2563eb,#06b6d4)",
                color: "white",
                padding: "20px 22px",
                fontWeight: 800,
                fontSize: 17,
                cursor: "pointer",
                boxShadow: "0 18px 40px rgba(37,99,235,.22)",
              }}
            >
              Run Agent
            </button>
          </section>

          <section
            style={{
              background: "rgba(255,255,255,.72)",
              borderRadius: 36,
              padding: 38,
              minHeight: 760,
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
                    fontWeight: 800,
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
                    fontSize: 46,
                    letterSpacing: -2,
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
                minHeight: 560,
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
                    fontSize: 34,
                    fontWeight: 800,
                    letterSpacing: -1.4,
                    marginBottom: 20,
                  }}
                >
                  Premium deliverables will appear here
                </div>

                <div
                  style={{
                    color: "#64748b",
                    fontSize: 19,
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
