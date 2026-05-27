from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

content = PAGE.read_text(encoding="utf-8")

backup = BACKUPS / f"client_page_before_step285_apply_{timestamp}.tsx"
backup.write_text(content, encoding="utf-8")

inject = """

const [showRejectModal, setShowRejectModal] = useState(false);
const [feedbackText, setFeedbackText] = useState("");

"""

content = content.replace(
'import { useEffect, useState } from "react";',
'import { useEffect, useState } from "react";\'
)

content = content.replace(
"const [task, setTask] = useState(",
inject + "\\nconst [task, setTask] = useState("
)

workflow_ui = """

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

"""

content = content.replace(
"</main>",
workflow_ui + "\\n</main>"
)

PAGE.write_text(content, encoding="utf-8")

print("STEP_285_REAL_WORKFLOW_UX_INSTALLED")
print(f"Backup: {backup}")
print("STEP_285_OK")