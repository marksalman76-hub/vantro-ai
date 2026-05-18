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
  const [showRejectModal, setShowRejectModal] = useState(false);
  const [feedbackText, setFeedbackText] = useState("");

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
          maxWidth: 1320,
          margin: "0 auto",
          padding: "20px 28px 48px",
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
    display: "flex",
    gap: 14,
    alignItems: "center",
  }}
>
  <div
    style={{
      background: "white",
      borderRadius: 999,
      padding: "14px 22px",
      border: "1px solid rgba(226,232,240,.9)",
      fontWeight: 700,
      fontSize: 14,
      boxShadow: "0 6px 18px rgba(15,23,42,.04)",
    }}
  >
    ● Local workspace
  </div>

  <div
    style={{
      background: "#2563eb",
      color: "white",
      borderRadius: 18,
      padding: "14px 18px",
      minWidth: 110,
      boxShadow: "0 10px 24px rgba(37,99,235,.18)",
    }}
  >
    <div
      style={{
        fontSize: 11,
        opacity: 0.82,
        marginBottom: 4,
      }}
    >
      Workflows
    </div>

    <div
      style={{
        fontSize: 22,
        fontWeight: 800,
        lineHeight: 1,
      }}
    >
      12
    </div>
  </div>

  <div
    style={{
      background: "white",
      borderRadius: 18,
      padding: "14px 18px",
      minWidth: 110,
      border: "1px solid rgba(226,232,240,.8)",
    }}
  >
    <div
      style={{
        fontSize: 11,
        color: "#64748b",
        marginBottom: 4,
      }}
    >
      Approval queue
    </div>

    <div
      style={{
        fontSize: 22,
        fontWeight: 800,
        lineHeight: 1,
      }}
    >
      3
    </div>
  </div>
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
              alignItems: "center",
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
            alignItems: "stretch",
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
              height: "100%",
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
                minHeight: 320,
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
    

<div
  style={{
    marginTop: 26,
    display: "grid",
    gridTemplateColumns: "1fr 1.3fr",
    gap: 24,
    alignItems: "start",
  }}
>
  <div
    style={{
      background: "#ffffff",
      borderRadius: 28,
      padding: 28,
      boxShadow: "0 10px 30px rgba(15,23,42,.05)",
      border: "1px solid rgba(15,23,42,.04)",
    }}
  >
    <div
      style={{
        fontSize: 13,
        fontWeight: 800,
        letterSpacing: 1,
        color: "#2563eb",
        marginBottom: 8,
      }}
    >
      LIVE EXECUTION FLOW
    </div>

    <div
      style={{
        fontSize: 34,
        fontWeight: 800,
        letterSpacing: -1.2,
        color: "#0f172a",
        marginBottom: 10,
      }}
    >
      Governed execution pipeline
    </div>

    <div
      style={{
        color: "#64748b",
        fontSize: 16,
        lineHeight: 1.6,
        marginBottom: 28,
      }}
    >
      Every AI deliverable flows through approval, optimisation,
      workflow validation, and governed execution before deployment.
    </div>

    <div
      style={{
        display: "flex",
        gap: 12,
        flexWrap: "wrap",
        marginBottom: 26,
      }}
    >
      {[
        "Campaign drafted",
        "Review pending",
        "Approval required",
        "Execution ready",
      ].map((item, index) => (
        <div
          key={item}
          style={{
            padding: "12px 16px",
            borderRadius: 999,
            background:
              index === 3
                ? "linear-gradient(135deg,#2563eb,#06b6d4)"
                : "rgba(37,99,235,.08)",
            color: index === 3 ? "#fff" : "#2563eb",
            fontWeight: 700,
            fontSize: 13,
          }}
        >
          {item}
        </div>
      ))}
    </div>

    <div
      style={{
        display: "grid",
        gap: 14,
      }}
    >
      {[
        ["Workflow initiated", "4:18 PM"],
        ["Product copy generated", "4:19 PM"],
        ["Execution review ready", "4:20 PM"],
      ].map(([label, time]) => (
        <div
          key={label}
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            paddingBottom: 12,
            borderBottom: "1px solid rgba(15,23,42,.06)",
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 10,
            }}
          >
            <div
              style={{
                width: 10,
                height: 10,
                borderRadius: 999,
                background: "#22c55e",
              }}
            />

            <div
              style={{
                fontWeight: 600,
                color: "#0f172a",
              }}
            >
              {label}
            </div>
          </div>

          <div
            style={{
              color: "#64748b",
              fontSize: 13,
            }}
          >
            {time}
          </div>
        </div>
      ))}
    </div>
  </div>

  <div
    style={{
      background: "#ffffff",
      borderRadius: 28,
      padding: 28,
      boxShadow: "0 10px 30px rgba(15,23,42,.05)",
      border: "1px solid rgba(15,23,42,.04)",
      position: "relative",
    }}
  >
    <div
      style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        marginBottom: 18,
      }}
    >
      <div>
        <div
          style={{
            fontSize: 13,
            fontWeight: 800,
            letterSpacing: 1,
            color: "#2563eb",
            marginBottom: 6,
          }}
        >
          EXECUTION OUTPUT VIEWER
        </div>

        <div
          style={{
            fontSize: 34,
            fontWeight: 800,
            letterSpacing: -1,
            color: "#0f172a",
          }}
        >
          Premium deliverables
        </div>
      </div>

      <div
        style={{
          padding: "12px 18px",
          borderRadius: 999,
          background: "rgba(34,197,94,.08)",
          color: "#16a34a",
          fontWeight: 700,
          fontSize: 13,
        }}
      >
        Completed
      </div>
    </div>

    <div
      style={{
        borderRadius: 24,
        background: "#f8fafc",
        padding: 22,
        border: "1px solid rgba(15,23,42,.05)",
      }}
    >
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "240px 1fr",
          gap: 22,
          alignItems: "start",
        }}
      >
        <div
          style={{
            borderRadius: 20,
            overflow: "hidden",
            minHeight: 260,
            background:
              "linear-gradient(135deg,#d6c3aa,#f6efe5,#b9936c)",
          }}
        />

        <div>
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              marginBottom: 14,
            }}
          >
            <div
              style={{
                fontWeight: 800,
                fontSize: 24,
                color: "#0f172a",
              }}
            >
              Luxury skincare launch campaign
            </div>

            <div
              style={{
                color: "#64748b",
                fontSize: 13,
              }}
            >
              17 May 2026 · 4:21 PM
            </div>
          </div>

          <div
            style={{
              color: "#475569",
              fontSize: 16,
              lineHeight: 1.7,
              marginBottom: 24,
            }}
          >
            Premium ecommerce campaign assets generated with positioning,
            emotional hooks, conversion-focused messaging, and launch-ready
            creative direction for luxury skincare buyers.
          </div>

          <div
            style={{
              display: "flex",
              gap: 14,
              marginBottom: 26,
              flexWrap: "wrap",
            }}
          >
            {[
              "Campaign copy",
              "Creative assets",
              "Execution flow",
              "Workflow automation",
            ].map((item) => (
              <div
                key={item}
                style={{
                  padding: "10px 14px",
                  borderRadius: 999,
                  background: "#ffffff",
                  border: "1px solid rgba(15,23,42,.06)",
                  fontWeight: 600,
                  fontSize: 13,
                  color: "#334155",
                }}
              >
                {item}
              </div>
            ))}
          </div>

          <div
            style={{
              display: "flex",
              gap: 14,
              alignItems: "center",
            }}
          >
            <button
              style={{
                padding: "14px 22px",
                borderRadius: 16,
                border: "none",
                background: "linear-gradient(135deg,#16a34a,#22c55e)",
                color: "#ffffff",
                fontWeight: 800,
                cursor: "pointer",
                fontSize: 14,
              }}
            >
              👍 Approve
            </button>

            <button
              onClick={() => setShowRejectModal(true)}
              style={{
                padding: "14px 22px",
                borderRadius: 16,
                border: "1px solid rgba(239,68,68,.15)",
                background: "#ffffff",
                color: "#dc2626",
                fontWeight: 800,
                cursor: "pointer",
                fontSize: 14,
              }}
            >
              👎 Reject
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>

{
  showRejectModal && (
    <div
      style={{
        position: "fixed",
        inset: 0,
        background: "rgba(15,23,42,.28)",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        zIndex: 9999,
      }}
    >
      <div
        style={{
          width: 520,
          background: "#ffffff",
          borderRadius: 28,
          padding: 30,
          boxShadow: "0 30px 80px rgba(15,23,42,.18)",
        }}
      >
        <div
          style={{
            fontSize: 28,
            fontWeight: 800,
            marginBottom: 12,
            color: "#0f172a",
          }}
        >
          Provide rejection feedback
        </div>

        <div
          style={{
            color: "#64748b",
            lineHeight: 1.6,
            marginBottom: 20,
          }}
        >
          Help the AI improve future outputs by explaining what should
          change before approval.
        </div>

        <textarea
          value={feedbackText}
          onChange={(e) => setFeedbackText(e.target.value)}
          placeholder="Describe what needs improvement..."
          style={{
            width: "100%",
            minHeight: 140,
            borderRadius: 18,
            border: "1px solid rgba(15,23,42,.08)",
            padding: 18,
            fontSize: 15,
            resize: "none",
            outline: "none",
            marginBottom: 22,
          }}
        />

        <div
          style={{
            display: "flex",
            justifyContent: "flex-end",
            gap: 12,
          }}
        >
          <button
            onClick={() => setShowRejectModal(false)}
            style={{
              padding: "14px 18px",
              borderRadius: 14,
              border: "1px solid rgba(15,23,42,.08)",
              background: "#ffffff",
              fontWeight: 700,
              cursor: "pointer",
            }}
          >
            Cancel
          </button>

          <button
            onClick={() => setShowRejectModal(false)}
            style={{
              padding: "14px 22px",
              borderRadius: 14,
              border: "none",
              background: "linear-gradient(135deg,#ef4444,#dc2626)",
              color: "#ffffff",
              fontWeight: 800,
              cursor: "pointer",
            }}
          >
            Submit feedback
          </button>
        </div>
      </div>
    </div>
  )
}

</main>
  );
}
