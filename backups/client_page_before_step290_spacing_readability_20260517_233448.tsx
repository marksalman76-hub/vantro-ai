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
  const [showRejectModal, setShowRejectModal] = useState(false);
  const [feedbackText, setFeedbackText] = useState("");

  useEffect(() => {
    fetch("/api/client-me")
      .then((r) => r.json())
      .then((data) => setAccount(data?.account || data))
      .catch(() => {});
  }, []);

  const creditsRemaining = 500;

  const toggleAgent = (agent: string) => {
    setSelectedAgents((prev) =>
      prev.includes(agent) ? prev.filter((a) => a !== agent) : [...prev, agent]
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
      <div style={{ maxWidth: "none", width: "100%", padding: "28px 34px 56px", boxSizing: "border-box" }}>
        <header
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "flex-start",
            gap: 28,
            marginBottom: 24,
          }}
        >
          <div>
            <div
              style={{
                color: "#2563eb",
                fontSize: 12,
                fontWeight: 900,
                letterSpacing: 1.4,
                textTransform: "uppercase",
                marginBottom: 10,
              }}
            >
              Client workspace
            </div>

            <h1
              style={{
                margin: 0,
                fontSize: 40,
                lineHeight: 1.04,
                letterSpacing: -1.8,
                fontWeight: 850,
              }}
            >
              Premium Demo Ecommerce Store
            </h1>

            <p
              style={{
                margin: "12px 0 0",
                maxWidth: 700,
                color: "#64748b",
                lineHeight: 1.55,
                fontSize: 15,
              }}
            >
              Run premium ecommerce AI agents, generate governed outputs, manage
              execution workflows, and produce commercial-grade deliverables.
            </p>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <button
              style={{
                border: "none",
                borderRadius: 14,
                padding: "12px 16px",
                background: "#0f172a",
                color: "#fff",
                fontWeight: 800,
                cursor: "pointer",
                boxShadow: "0 10px 24px rgba(15,23,42,.12)",
              }}
            >
              + New execution
            </button>

            <div
              style={{
                background: "#fff",
                borderRadius: 999,
                padding: "12px 16px",
                border: "1px solid #e5eaf2",
                fontWeight: 800,
                boxShadow: "0 8px 22px rgba(15,23,42,.045)",
              }}
            >
              <span style={{ color: "#2563eb", marginRight: 8 }}>●</span>
              Local workspace
            </div>

            <button
              aria-label="Notifications"
              style={{
                width: 44,
                height: 44,
                borderRadius: 999,
                border: "1px solid #e5eaf2",
                background: "#fff",
                boxShadow: "0 8px 22px rgba(15,23,42,.045)",
                cursor: "pointer",
                position: "relative",
              }}
            >
              🔔
              <span
                style={{
                  position: "absolute",
                  top: 7,
                  right: 8,
                  width: 8,
                  height: 8,
                  borderRadius: 999,
                  background: "#2563eb",
                  border: "2px solid #fff",
                }}
              />
            </button>

            <div
              style={{
                width: 44,
                height: 44,
                borderRadius: 999,
                background: "#0f172a",
                color: "#fff",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontWeight: 900,
              }}
            >
              PD
            </div>
          </div>
        </header>

        <section
          style={{
            display: "grid",
            gridTemplateColumns: "1.2fr .8fr .8fr .8fr",
            gap: 12,
            alignItems: "stretch",
            marginBottom: 20,
          }}
        >
          {[
            ["Workspace status", "Ready for execution", "Live client environment"],
            ["Approvals", "3 pending", "Requires client review"],
            ["Workflows", "12 tracked", "Governed automation"],
            ["Credits", String(creditsRemaining), "Available balance"],
          ].map(([label, value, note]) => (
            <div
              key={label}
              style={{
                background: "rgba(255,255,255,.72)",
                border: "1px solid #edf1f6",
                borderRadius: 18,
                padding: "14px 16px",
                boxShadow: "0 8px 22px rgba(15,23,42,.035)",
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                gap: 14,
              }}
            >
              <div>
                <div
                  style={{
                    color: "#64748b",
                    fontSize: 11,
                    fontWeight: 800,
                    letterSpacing: .4,
                    textTransform: "uppercase",
                    marginBottom: 5,
                  }}
                >
                  {label}
                </div>

                <strong
                  style={{
                    display: "block",
                    fontSize: 17,
                    letterSpacing: -.2,
                    color: "#0f172a",
                  }}
                >
                  {value}
                </strong>

                <div
                  style={{
                    color: "#94a3b8",
                    fontSize: 12,
                    marginTop: 3,
                  }}
                >
                  {note}
                </div>
              </div>

              <span
                style={{
                  width: 10,
                  height: 10,
                  borderRadius: 999,
                  background: label === "Approvals" ? "#f59e0b" : "#2563eb",
                  boxShadow:
                    label === "Approvals"
                      ? "0 0 0 5px rgba(245,158,11,.10)"
                      : "0 0 0 5px rgba(37,99,235,.08)",
                }}
              />
            </div>
          ))}
        </section>

        <section
          style={{
            background: "#fff",
            borderRadius: 26,
            padding: 28,
            boxShadow: "0 14px 34px rgba(15,23,42,.045)",
            marginBottom: 18,
          }}
        >
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              gap: 18,
              alignItems: "flex-start",
              marginBottom: 22,
            }}
          >
            <div>
              <div
                style={{
                  color: "#2563eb",
                  fontSize: 12,
                  fontWeight: 900,
                  letterSpacing: 1.4,
                  textTransform: "uppercase",
                  marginBottom: 8,
                }}
              >
                Business profile intelligence
              </div>

              <h2 style={{ margin: 0, fontSize: 26, letterSpacing: -0.8 }}>
                Store context for smarter agent outputs
              </h2>

              <p style={{ marginTop: 10, color: "#64748b", maxWidth: 760, lineHeight: 1.55 }}>
                Add business context once so every active AI agent can produce more accurate
                campaigns, creative assets, copy, positioning, and execution recommendations.
              </p>
            </div>

            <div
              style={{
                background: "#eff6ff",
                color: "#2563eb",
                padding: "10px 14px",
                borderRadius: 999,
                fontWeight: 800,
                fontSize: 13,
              }}
            >
              ✓ Applied to execution
            </div>
          </div>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit,minmax(210px,1fr))",
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
              <label key={label}>
                <div style={{ color: "#64748b", fontSize: 12, fontWeight: 700, marginBottom: 7 }}>
                  {label}
                </div>
                <textarea
                  defaultValue={value}
                  rows={2}
                  style={{
                    width: "100%",
                    resize: "none",
                    borderRadius: 14,
                    border: "1px solid #e2e8f0",
                    background: "#fff",
                    padding: "14px 15px",
                    fontSize: 13,
                    lineHeight: 1.45,
                    color: "#0f172a",
                    outline: "none",
                    boxSizing: "border-box",
                    fontFamily: "inherit",
                  }}
                />
              </label>
            ))}
          </div>
        </section>

        <section
          style={{
            display: "grid",
            gridTemplateColumns: "1.15fr .95fr .95fr .85fr",
            gap: 16,
            alignItems: "stretch",
            marginBottom: 16,
          }}
        >
          <div style={cardStyle}>
            <StepHeader number="01" title="Run AI Agent" />
            <h3 style={cardTitle}>Select agents, define task, and execute.</h3>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14, marginTop: 18 }}>
              <div>
                <div style={labelStyle}>Active agents</div>
                <div style={{ display: "grid", gap: 7 }}>
                  {AGENTS.map((agent) => {
                    const active = selectedAgents.includes(agent);
                    return (
                      <button
                        key={agent}
                        onClick={() => toggleAgent(agent)}
                        style={{
                          border: active ? "1px solid #bfdbfe" : "1px solid #e5eaf2",
                          background: active ? "#eff6ff" : "#fff",
                          color: active ? "#2563eb" : "#0f172a",
                          padding: "9px 10px",
                          borderRadius: 11,
                          cursor: "pointer",
                          textAlign: "left",
                          fontSize: 12,
                          fontWeight: 800,
                        }}
                      >
                        {active ? "● " : "○ "}
                        {agent}
                      </button>
                    );
                  })}
                </div>
              </div>

              <div>
                <div style={labelStyle}>Task</div>
                <textarea
                  defaultValue="Create premium ecommerce campaign assets for a luxury skincare product launch."
                  style={{
                    width: "100%",
                    minHeight: 150,
                    resize: "none",
                    borderRadius: 14,
                    border: "1px solid #dbe3ee",
                    background: "#fff",
                    padding: 14,
                    fontSize: 13,
                    lineHeight: 1.55,
                    boxSizing: "border-box",
                    fontFamily: "inherit",
                  }}
                />

                <button
                  style={{
                    marginTop: 12,
                    width: "100%",
                    border: "none",
                    borderRadius: 13,
                    background: "linear-gradient(135deg,#2563eb,#06b6d4)",
                    color: "#fff",
                    padding: "13px 16px",
                    fontWeight: 900,
                    cursor: "pointer",
                    boxShadow: "0 12px 26px rgba(37,99,235,.18)",
                  }}
                >
                  ✨ Run Agent
                </button>
              </div>
            </div>

            <div style={{ marginTop: 12, color: "#64748b", fontSize: 12 }}>
              ⓘ All agents will use the business profile context above.
            </div>
          </div>

          <div style={cardStyle}>
            <StepHeader number="02" title="Live execution flow" />
            <h3 style={cardTitle}>Governed execution pipeline</h3>
            <p style={mutedText}>
              Every AI deliverable flows through approval, optimisation, workflow validation,
              and governed execution before deployment.
            </p>

            <div style={{ display: "grid", gap: 12, marginTop: 20 }}>
              {[
                ["Campaign drafted", "Done", "4:18 PM"],
                ["Review pending", "In progress", "4:19 PM"],
                ["Approval required", "Pending", "4:20 PM"],
                ["Execution ready", "Next", "—"],
              ].map(([title, status, time], index) => (
                <div key={title} style={{ display: "grid", gridTemplateColumns: "34px 1fr auto", gap: 12, alignItems: "center" }}>
                  <div
                    style={{
                      width: 28,
                      height: 28,
                      borderRadius: 10,
                      background: index === 3 ? "#06b6d4" : "#2563eb",
                      color: "#fff",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      fontSize: 13,
                    }}
                  >
                    {index + 1}
                  </div>
                  <div>
                    <div style={{ fontWeight: 850, fontSize: 13 }}>{title}</div>
                    <div style={{ color: "#64748b", fontSize: 12 }}>{status}</div>
                  </div>
                  <div style={{ color: "#64748b", fontSize: 12 }}>{time}</div>
                </div>
              ))}
            </div>
          </div>

          <div style={cardStyle}>
            <StepHeader number="03" title="Execution workspace" />
            <h3 style={cardTitle}>Premium deliverables will appear here</h3>
            <p style={mutedText}>
              Campaign outputs, approvals, execution flows, creative assets, billing events,
              and governed automation actions will appear after execution.
            </p>

            <div
              style={{
                marginTop: 24,
                minHeight: 150,
                borderRadius: 18,
                background: "linear-gradient(135deg,#eff6ff,#f8fafc)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color: "#2563eb",
                fontWeight: 900,
              }}
            >
              Run an agent to generate deliverables
            </div>
          </div>

          <div style={cardStyle}>
            <StepHeader number="04" title="Quick actions" />
            <h3 style={cardTitle}>Common workspace actions</h3>

            <div style={{ display: "grid", gap: 11, marginTop: 20 }}>
              {["View execution history", "Manage workflows", "Agent performance", "Workspace settings"].map((item) => (
                <button
                  key={item}
                  style={{
                    border: "1px solid #e5eaf2",
                    background: "#fff",
                    borderRadius: 13,
                    padding: "13px 14px",
                    textAlign: "left",
                    fontWeight: 800,
                    cursor: "pointer",
                  }}
                >
                  {item} →
                </button>
              ))}
            </div>
          </div>
        </section>

        <section
          style={{
            display: "grid",
            gridTemplateColumns: "1fr 1.35fr",
            gap: 16,
            alignItems: "stretch",
          }}
        >
          <div style={cardStyle}>
            <StepHeader number="05" title="Execution timeline" />
            <h3 style={cardTitle}>Real-time execution timeline</h3>

            <div style={{ display: "grid", gap: 16, marginTop: 22 }}>
              {[
                ["4:18 PM", "Workflow initiated", "System"],
                ["4:19 PM", "Product copy generated", "Product Copywriting Agent"],
                ["4:20 PM", "Execution review ready", "General Ecommerce Agent"],
              ].map(([time, event, actor]) => (
                <div
                  key={event}
                  style={{
                    display: "grid",
                    gridTemplateColumns: "90px 1fr auto",
                    gap: 14,
                    alignItems: "center",
                    borderBottom: "1px solid #eef2f7",
                    paddingBottom: 13,
                  }}
                >
                  <div style={{ color: "#64748b", fontSize: 13 }}>● {time}</div>
                  <div style={{ fontWeight: 850 }}>{event}</div>
                  <div style={{ color: "#64748b", fontSize: 13 }}>{actor}</div>
                </div>
              ))}
            </div>
          </div>

          <div style={cardStyle}>
            <div style={{ display: "flex", justifyContent: "space-between", gap: 16 }}>
              <div>
                <StepHeader number="06" title="Execution output viewer" />
                <h3 style={cardTitle}>Premium deliverables</h3>
              </div>
              <div
                style={{
                  background: "#dcfce7",
                  color: "#16a34a",
                  padding: "10px 14px",
                  borderRadius: 999,
                  fontWeight: 900,
                  fontSize: 13,
                  height: "fit-content",
                }}
              >
                Completed
              </div>
            </div>

            <div
              style={{
                marginTop: 18,
                display: "grid",
                gridTemplateColumns: "220px 1fr",
                gap: 20,
                padding: 18,
                borderRadius: 20,
                border: "1px solid #e5eaf2",
                background: "#fff",
              }}
            >
              <div
                style={{
                  minHeight: 170,
                  borderRadius: 16,
                  background: "linear-gradient(135deg,#e8d5bd,#b9874f,#fff4df)",
                }}
              />

              <div>
                <div style={{ display: "flex", justifyContent: "space-between", gap: 10 }}>
                  <h4 style={{ margin: 0, fontSize: 20 }}>Luxury skincare launch campaign</h4>
                  <div style={{ color: "#64748b", fontSize: 12 }}>17 May 2026 · 4:21 PM</div>
                </div>

                <p style={{ color: "#475569", lineHeight: 1.6 }}>
                  Premium ecommerce campaign assets generated with positioning, emotional hooks,
                  conversion-focused messaging, and launch-ready creative direction for luxury
                  skincare buyers.
                </p>

                <div style={{ display: "flex", gap: 10, flexWrap: "wrap", marginBottom: 16 }}>
                  {["Campaign copy", "Creative assets", "Execution flow", "Workflow automation"].map((tag) => (
                    <span
                      key={tag}
                      style={{
                        border: "1px solid #e5eaf2",
                        borderRadius: 999,
                        padding: "8px 11px",
                        fontSize: 12,
                        fontWeight: 800,
                      }}
                    >
                      {tag}
                    </span>
                  ))}
                </div>

                <div style={{ display: "flex", gap: 12 }}>
                  <button
                    style={{
                      border: "none",
                      background: "#22c55e",
                      color: "#fff",
                      borderRadius: 12,
                      padding: "12px 18px",
                      fontWeight: 900,
                      cursor: "pointer",
                    }}
                  >
                    👍 Approve
                  </button>

                  <button
                    onClick={() => setShowRejectModal(true)}
                    style={{
                      border: "1px solid #fecaca",
                      background: "#fff",
                      color: "#dc2626",
                      borderRadius: 12,
                      padding: "12px 18px",
                      fontWeight: 900,
                      cursor: "pointer",
                    }}
                  >
                    👎 Reject
                  </button>
                </div>
              </div>
            </div>
          </div>
        </section>
      </div>

      {showRejectModal ? (
        <div
          style={{
            position: "fixed",
            inset: 0,
            background: "rgba(15,23,42,.28)",
            zIndex: 9999,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: 24,
          }}
        >
          <div
            style={{
              width: 520,
              background: "#fff",
              borderRadius: 26,
              padding: 28,
              boxShadow: "0 30px 80px rgba(15,23,42,.20)",
            }}
          >
            <h2 style={{ margin: 0, fontSize: 26 }}>Provide rejection feedback</h2>
            <p style={{ color: "#64748b", lineHeight: 1.6 }}>
              Explain what needs to change so the agent can improve the next output.
            </p>

            <textarea
              value={feedbackText}
              onChange={(e) => setFeedbackText(e.target.value)}
              placeholder="Describe what should be improved..."
              style={{
                width: "100%",
                minHeight: 140,
                borderRadius: 16,
                border: "1px solid #e5eaf2",
                padding: 16,
                fontSize: 14,
                resize: "none",
                boxSizing: "border-box",
                outline: "none",
              }}
            />

            <div style={{ display: "flex", justifyContent: "flex-end", gap: 12, marginTop: 18 }}>
              <button
                onClick={() => setShowRejectModal(false)}
                style={{
                  border: "1px solid #e5eaf2",
                  background: "#fff",
                  borderRadius: 12,
                  padding: "12px 16px",
                  fontWeight: 800,
                  cursor: "pointer",
                }}
              >
                Cancel
              </button>

              <button
                onClick={() => setShowRejectModal(false)}
                style={{
                  border: "none",
                  background: "#dc2626",
                  color: "#fff",
                  borderRadius: 12,
                  padding: "12px 18px",
                  fontWeight: 900,
                  cursor: "pointer",
                }}
              >
                Submit feedback
              </button>
            </div>
          </div>
        </div>
      ) : null}
    </main>
  );
}

const cardStyle = {
  background: "#fff",
  borderRadius: 22,
  padding: 22,
  boxShadow: "0 14px 34px rgba(15,23,42,.045)",
  border: "1px solid #edf1f6",
};

const labelStyle = {
  color: "#64748b",
  fontSize: 13,
  fontWeight: 700,
  marginBottom: 8,
};

const mutedText = {
  color: "#64748b",
  lineHeight: 1.55,
  fontSize: 13,
};

const cardTitle = {
  margin: 0,
  fontSize: 20,
  letterSpacing: -0.4,
};

function StepHeader({ number, title }: { number: string; title: string }) {
  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        gap: 10,
        color: "#2563eb",
        fontSize: 12,
        fontWeight: 900,
        letterSpacing: 0.9,
        textTransform: "uppercase",
        marginBottom: 8,
      }}
    >
      <span
        style={{
          width: 28,
          height: 28,
          borderRadius: 999,
          background: "#eff6ff",
          color: "#2563eb",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        {number}
      </span>
      {title}
    </div>
  );
}
