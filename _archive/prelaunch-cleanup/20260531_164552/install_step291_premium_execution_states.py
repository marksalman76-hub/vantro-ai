from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
text = PAGE.read_text(encoding="utf-8")

backup = BACKUPS / f"client_page_before_step291_execution_states_{timestamp}.tsx"
backup.write_text(text, encoding="utf-8")

# Add execution UI states after selectedAgents state
target = '''  const [showRejectModal, setShowRejectModal] = useState(false);
  const [feedbackText, setFeedbackText] = useState("");'''

replacement = '''  const [showRejectModal, setShowRejectModal] = useState(false);
  const [feedbackText, setFeedbackText] = useState("");
  const [executionState, setExecutionState] = useState<"idle" | "running" | "completed" | "rejected">("idle");
  const [toastMessage, setToastMessage] = useState("");'''

if target not in text:
    raise SystemExit("ERROR: State block not found.")

text = text.replace(target, replacement)

# Make Run Agent button trigger running then completed state
old_run_button = '''                <button
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
                </button>'''

new_run_button = '''                <button
                  onClick={() => {
                    setExecutionState("running");
                    setToastMessage("Execution started. Generating premium deliverables...");
                    window.setTimeout(() => {
                      setExecutionState("completed");
                      setToastMessage("Premium deliverable generated and ready for review.");
                    }, 1200);
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
                </button>'''

if old_run_button not in text:
    raise SystemExit("ERROR: Run button block not found.")

text = text.replace(old_run_button, new_run_button)

# Replace execution workspace empty panel with state-aware content
old_workspace_panel = '''            <div
              style={{
                marginTop: 24,
                minHeight: 185,
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
            </div>'''

new_workspace_panel = '''            <div
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
            </div>'''

if old_workspace_panel not in text:
    raise SystemExit("ERROR: Execution workspace panel not found.")

text = text.replace(old_workspace_panel, new_workspace_panel)

# Wire Approve button
text = text.replace(
'''                  <button
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
                  </button>''',
'''                  <button
                    onClick={() => {
                      setExecutionState("completed");
                      setToastMessage("Deliverable approved. Execution is ready to continue.");
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
                    👍 Approve
                  </button>'''
)

# Wire reject button state
text = text.replace(
'''                    onClick={() => setShowRejectModal(true)}''',
'''                    onClick={() => {
                      setShowRejectModal(true);
                      setExecutionState("rejected");
                    }}'''
)

# Wire feedback submit toast
text = text.replace(
'''                onClick={() => setShowRejectModal(false)}''',
'''                onClick={() => {
                  setShowRejectModal(false);
                  setToastMessage("Feedback submitted. The agent will use it to improve the next output.");
                }}''',
1
)

# Add toast before closing main
toast = '''
      {toastMessage ? (
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
'''

text = text.replace("      {showRejectModal ? (", toast + "\n      {showRejectModal ? (")

PAGE.write_text(text, encoding="utf-8")

print("STEP_291_PREMIUM_EXECUTION_STATES_INSTALLED")
print(f"Backup: {backup}")
print("STEP_291_OK")