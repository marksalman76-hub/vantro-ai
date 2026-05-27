from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
text = PAGE.read_text(encoding="utf-8")

backup = BACKUPS / f"client_page_before_step293_feedback_modal_polish_{timestamp}.tsx"
backup.write_text(text, encoding="utf-8")

state_target = '''  const [feedbackText, setFeedbackText] = useState("");
  const [executionState, setExecutionState] = useState<"idle" | "running" | "completed" | "rejected">("idle");'''

state_replacement = '''  const [feedbackText, setFeedbackText] = useState("");
  const [feedbackReason, setFeedbackReason] = useState("");
  const [executionState, setExecutionState] = useState<"idle" | "running" | "completed" | "rejected">("idle");'''

if state_target not in text:
    raise SystemExit("ERROR: state target not found.")

text = text.replace(state_target, state_replacement)

text = text.replace(
'''          style={{
            position: "fixed",
            inset: 0,
            background: "rgba(15,23,42,.28)",
            zIndex: 9999,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: 24,
          }}''',
'''          onClick={() => setShowRejectModal(false)}
          style={{
            position: "fixed",
            inset: 0,
            background: "rgba(15,23,42,.28)",
            zIndex: 9999,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: 24,
          }}'''
)

text = text.replace(
'''          <div
            style={{
              width: 520,
              background: "#fff",
              borderRadius: 26,
              padding: 28,
              boxShadow: "0 30px 80px rgba(15,23,42,.20)",
            }}
          >''',
'''          <div
            onClick={(event) => event.stopPropagation()}
            style={{
              width: 560,
              background: "#fff",
              borderRadius: 26,
              padding: 28,
              boxShadow: "0 30px 80px rgba(15,23,42,.20)",
            }}
          >'''
)

reason_block = '''            <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 16 }}>
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

'''

text = text.replace(
'''            <textarea
              value={feedbackText}''',
reason_block + '''            <textarea
              value={feedbackText}'''
)

text = text.replace(
'''              <button
                onClick={() => {
                  setShowRejectModal(false);
                  setToastMessage("Feedback submitted. The agent will use it to improve the next output.");
                }}
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
              </button>''',
'''              <button
                disabled={!feedbackText.trim() && !feedbackReason}
                onClick={() => {
                  if (!feedbackText.trim() && !feedbackReason) return;
                  setShowRejectModal(false);
                  setToastMessage("Feedback submitted. The agent will use it to improve the next output.");
                }}
                style={{
                  border: "none",
                  background: (!feedbackText.trim() && !feedbackReason) ? "#cbd5e1" : "#dc2626",
                  color: "#fff",
                  borderRadius: 12,
                  padding: "12px 18px",
                  fontWeight: 900,
                  cursor: (!feedbackText.trim() && !feedbackReason) ? "not-allowed" : "pointer",
                }}
              >
                Submit feedback
              </button>'''
)

PAGE.write_text(text, encoding="utf-8")

print("STEP_293_FEEDBACK_MODAL_POLISH_INSTALLED")
print(f"Backup: {backup}")
print("STEP_293_OK")