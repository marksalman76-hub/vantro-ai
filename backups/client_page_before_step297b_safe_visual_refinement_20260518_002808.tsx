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
  const [feedbackReason, setFeedbackReason] = useState("");
  const [reviewStatus, setReviewStatus] = useState<"pending" | "approved" | "rejected">("pending");
  const [reviewActionLoading, setReviewActionLoading] = useState(false);
  const [liveDeliverable, setLiveDeliverable] = useState<any>(null);
  const [executionState, setExecutionState] = useState<"idle" | "running" | "completed" | "rejected">("idle");
  const [toastMessage, setToastMessage] = useState("");

  useEffect(() => {
    fetch("/api/client-me")
      .then((r) => r.json())
      .then((data) => setAccount(data?.account || data))
      .catch(() => {});
  }, []);

  const creditsRemaining = 500;

  useEffect(() => {
    if (!toastMessage) return;

    const timer = window.setTimeout(() => {
      setToastMessage("");
    }, 3200);

    return () => window.clearTimeout(timer);
  }, [toastMessage]);

  async function recordClientReviewAction(action: "approved" | "rejected", feedback = "", reason = "") {
    setReviewActionLoading(true);

    try {
      const response = await fetch("/api/client-review-action", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify({
          action,
          feedback,
          reason,
          selected_agents: selectedAgents,
          reviewed_item: "Luxury skincare launch campaign",
          source: "client_workspace",
        }),
      });

      if (!response.ok) {
        throw new Error("Review action failed");
      }

      const data = await response.json();

      if (!data?.success) {
        throw new Error("Review action was not accepted");
      }

      return true;
    } catch {
      setToastMessage("Review action could not be saved. Please try again.");
      return false;
    } finally {
      setReviewActionLoading(false);
    }
  }

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
      <div style={{ maxWidth: "none", width: "100%", padding: "30px 34px 60px", boxSizing: "border-box" }}>
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
            marginBottom: 22,
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
                padding: "16px 18px",
                boxShadow: "0 8px 22px rgba(15,23,42,.035)",
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                gap: 18,
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
            padding: 30,
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
                fontSize: 13.5,
              }}
            >
              ✓ Applied to execution
            </div>
          </div>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit,minmax(210px,1fr))",
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
              <label key={label}>
                <div style={{ color: "#64748b", fontSize: 12, fontWeight: 700, marginBottom: 7 }}>
                  {label}
                </div>
                <textarea
                  defaultValue={value}
                  rows={3}
                  style={{
                    width: "100%",
                    resize: "none",
                    borderRadius: 14,
                    border: "1px solid #e2e8f0",
                    background: "#fff",
                    padding: "16px 16px",
                    fontSize: 13.5,
                    lineHeight: 1.55,
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
            gap: 18,
            alignItems: "stretch",
            marginBottom: 16,
          }}
        >
          <div style={cardStyle}>
            <StepHeader number="01" title="Run AI Agent" />
            <h3 style={cardTitle}>Select agents, define task, and execute.</h3>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 18, marginTop: 18 }}>
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
                    minHeight: 185,
                    resize: "none",
                    borderRadius: 14,
                    border: "1px solid #dbe3ee",
                    background: "#fff",
                    padding: 14,
                    fontSize: 13.5,
                    lineHeight: 1.55,
                    boxSizing: "border-box",
                    fontFamily: "inherit",
                  }}
                />

                <button
                  onClick={async () => {
                    setExecutionState("running");
                    setToastMessage("Execution started. Generating premium deliverables...");

                    try {
                      const response = await fetch("/api/run-agent", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        credentials: "include",
                        body: JSON.stringify({
                          selected_agents: selectedAgents,
                          task: "Create premium ecommerce campaign assets for a luxury skincare product launch.",
                          business_profile: {
                            niche: "Luxury skincare",
                            target_audience: "Premium ecommerce buyers",
                            positioning: "Commercial-grade premium launch campaign",
                          },
                        }),
                      });

                      const data = await response.json();

                      if (!response.ok || !data?.success) {
                        throw new Error("Execution failed");
                      }

                      setLiveDeliverable(data.deliverable);
                      setExecutionState("completed");
                      setToastMessage("Premium deliverable generated and ready for review.");
                    } catch {
                      setExecutionState("idle");
                      setToastMessage("Execution could not be completed. Please try again.");
                    }
                  }}
                  style={{
                    marginTop: 12,
                    width: "100%",
                    border: "none",
                    borderRadius: 13,
                    background:
                      executionState === "running"
                        ? "linear-gradient(135deg,#64748b,#475569)"
                        : "linear-gradient(135deg,#2563eb,#06b6d4)",
                    color: "#fff",
                    padding: "13px 16px",
                    fontWeight: 900,
                    cursor: "pointer",
                    boxShadow: "0 12px 26px rgba(37,99,235,.18)",
                  }}
                >
                  {executionState === "running" ? "Generating..." : "✨ Run Agent"}
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
                      fontSize: 13.5,
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
                minHeight: 185,
                borderRadius: 18,
                background:
                  executionState === "running"
                    ? "linear-gradient(135deg,#eff6ff,#ffffff)"
                    : executionState === "completed"
                      ? "linear-gradient(135deg,#ecfdf5,#ffffff)"
                      : "linear-gradient(135deg,#eff6ff,#f8fafc)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color:
                  executionState === "completed"
                    ? "#16a34a"
                    : "#2563eb",
                fontWeight: 900,
                textAlign: "center",
                padding: 20,
              }}
            >
              {executionState === "running" ? (
                <div>
                  <div style={{ fontSize: 28, marginBottom: 10 }}>⏳</div>
                  <div>Generating premium deliverables...</div>
                  <div
                    style={{
                      marginTop: 14,
                      height: 8,
                      width: 240,
                      borderRadius: 999,
                      background: "#dbeafe",
                      overflow: "hidden",
                    }}
                  >
                    <div
                      style={{
                        width: "72%",
                        height: "100%",
                        borderRadius: 999,
                        background: "linear-gradient(135deg,#2563eb,#06b6d4)",
                      }}
                    />
                  </div>
                </div>
              ) : executionState === "completed" ? (
                <div>
                  <div style={{ fontSize: 28, marginBottom: 10 }}>✅</div>
                  <div>Deliverable ready for review</div>
                  <div style={{ marginTop: 6, color: "#64748b", fontSize: 12 }}>
                    Approval or feedback required
                  </div>
                </div>
              ) : (
                "Run an agent to generate deliverables"
              )}
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
            gap: 18,
            alignItems: "stretch",
          }}
        >
          <div style={cardStyle}>
            <StepHeader number="05" title="Execution timeline" />
            <h3 style={cardTitle}>Real-time execution timeline</h3>

            <div style={{ display: "grid", gap: 18, marginTop: 22 }}>
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
                    gap: 18,
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
                  fontSize: 13.5,
                  height: "fit-content",
                }}
              >
                {reviewStatus === "approved" ? "Approved" : reviewStatus === "rejected" ? "Revision requested" : "Completed"}
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
                  minHeight: 185,
                  borderRadius: 18,
                  background:
                    "radial-gradient(circle at 28% 24%, rgba(255,255,255,.95), rgba(255,255,255,0) 26%), linear-gradient(135deg,#f8ead8 0%,#d7aa70 38%,#9b6a3c 70%,#f6dfbd 100%)",
                  position: "relative",
                  overflow: "hidden",
                  boxShadow: "inset 0 0 0 1px rgba(255,255,255,.45)",
                }}
              >
                <div
                  style={{
                    position: "absolute",
                    inset: 18,
                    borderRadius: 16,
                    border: "1px solid rgba(255,255,255,.48)",
                    background:
                      "linear-gradient(135deg,rgba(255,255,255,.22),rgba(255,255,255,.04))",
                  }}
                />

                <div
                  style={{
                    position: "absolute",
                    left: "50%",
                    top: "50%",
                    transform: "translate(-50%,-43%)",
                    width: 112,
                    height: 112,
                    borderRadius: 28,
                    background:
                      "linear-gradient(145deg,rgba(255,255,255,.92),rgba(241,211,170,.92))",
                    boxShadow: "0 22px 55px rgba(91,54,24,.22)",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    textAlign: "center",
                    color: "#7c4a1f",
                    fontWeight: 900,
                    letterSpacing: 1.2,
                    fontSize: 15,
                  }}
                >
                  LUXE
                  <br />
                  LAUNCH
                </div>

                <div
                  style={{
                    position: "absolute",
                    left: 22,
                    bottom: 20,
                    right: 22,
                    color: "#fffaf0",
                    fontWeight: 900,
                    textShadow: "0 2px 12px rgba(0,0,0,.22)",
                    fontSize: 14,
                    lineHeight: 1.35,
                  }}
                >
                  Premium campaign preview
                </div>
              </div>

              <div>
                <div style={{ display: "flex", justifyContent: "space-between", gap: 10 }}>
                  <h4 style={{ margin: 0, fontSize: 20 }}>
                    {liveDeliverable?.title || "Luxury skincare launch campaign"}
                  </h4>
                  <div style={{ color: "#64748b", fontSize: 12 }}>
                    {liveDeliverable?.created_at || "17 May 2026 · 4:21 PM"}
                  </div>
                </div>

                <p style={{ color: "#475569", lineHeight: 1.6 }}>
                  {liveDeliverable?.summary ||
                    "Premium ecommerce campaign assets generated with positioning, emotional hooks, conversion-focused messaging, and launch-ready creative direction for luxury skincare buyers."}
                </p>

                <div style={{ display: "flex", gap: 10, flexWrap: "wrap", marginBottom: 16 }}>
                  {(liveDeliverable?.tags || ["Campaign copy", "Creative assets", "Execution flow", "Workflow automation"]).map((tag: string) => (
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
                    onClick={async () => {
                      const saved = await recordClientReviewAction("approved");
                      if (!saved) return;

                      setReviewStatus("approved");
                      setExecutionState("completed");
                      setToastMessage("Deliverable approved and saved to the client review log.");
                    }}
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
                    {reviewActionLoading ? "Saving..." : "👍 Approve"}
                  </button>

                  <button
                    onClick={() => {
                      setToastMessage("");
                      setShowRejectModal(true);
                      setExecutionState("rejected");
                    }}
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


      {toastMessage && !showRejectModal ? (
        <div
          style={{
            position: "fixed",
            right: 24,
            bottom: 24,
            zIndex: 9998,
            background: "#0f172a",
            color: "#ffffff",
            borderRadius: 16,
            padding: "14px 18px",
            boxShadow: "0 18px 45px rgba(15,23,42,.22)",
            fontWeight: 800,
            maxWidth: 360,
          }}
        >
          {toastMessage}
        </div>
      ) : null}

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
              padding: 30,
              boxShadow: "0 30px 80px rgba(15,23,42,.20)",
            }}
          >
            <h2 style={{ margin: 0, fontSize: 26 }}>Provide rejection feedback</h2>
            <p style={{ color: "#64748b", lineHeight: 1.6 }}>
              Explain what needs to change so the agent can improve the next output.
            </p>

            <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 16 }}>
              {["Not relevant", "Wrong tone", "Needs more detail", "Off brand", "Incorrect information"].map((reason) => (
                <button
                  key={reason}
                  onClick={() => setFeedbackReason(reason)}
                  style={{
                    border: feedbackReason === reason ? "1px solid #dc2626" : "1px solid #e5eaf2",
                    background: feedbackReason === reason ? "#fef2f2" : "#fff",
                    color: feedbackReason === reason ? "#dc2626" : "#334155",
                    borderRadius: 999,
                    padding: "8px 11px",
                    fontWeight: 800,
                    fontSize: 12,
                    cursor: "pointer",
                  }}
                >
                  {reason}
                </button>
              ))}
            </div>

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
                onClick={() => {
                  setShowRejectModal(false);
                  setToastMessage("Feedback submitted. The agent will use it to improve the next output.");
                }}
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
                {reviewActionLoading ? "Saving..." : "Submit feedback"}
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
  borderRadius: 24,
  padding: 24,
  boxShadow: "0 14px 34px rgba(15,23,42,.045)",
  border: "1px solid #edf1f6",
};

const labelStyle = {
  color: "#64748b",
  fontSize: 13.5,
  fontWeight: 700,
  marginBottom: 8,
};

const mutedText = {
  color: "#64748b",
  lineHeight: 1.55,
  fontSize: 13.5,
};

const cardTitle = {
  margin: 0,
  fontSize: 21,
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
