from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

src = PAGE.read_text(encoding="utf-8")
backup = BACKUPS / f"client_page_before_activity_only_polish_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
backup.write_text(src, encoding="utf-8")

start_marker = '          <div style={{ ...cardStyle, height: 560, overflow: "hidden" }}>\n            <StepHeader number="05" title="Activity" />'
end_marker = '\n\n          <div style={{ ...cardStyle, height: 560, overflow: "hidden" }}>\n            <div style={{ display: "flex", justifyContent: "space-between", gap: 16, flexWrap: "wrap" }}>'

start = src.find(start_marker)
end = src.find(end_marker, start)

if start == -1:
    raise SystemExit("ERROR: Activity block start not found.")
if end == -1:
    raise SystemExit("ERROR: Activity block end not found.")

new_activity = r'''          <div style={{ ...cardStyle, minHeight: 430, overflow: "hidden" }}>
            <StepHeader number="05" title="Activity" />
            <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", gap: 14 }}>
              <div>
                <h3 style={cardTitle}>Activity</h3>
                <p style={{ ...mutedText, margin: "5px 0 0", color: "var(--color-brand)", fontWeight: 800 }}>
                  Latest governed activity
                </p>
              </div>
              <span
                style={{
                  background: "#ecfdf5",
                  color: "var(--color-teal)",
                  border: "1px solid #bbf7d0",
                  borderRadius: 999,
                  padding: "7px 10px",
                  fontSize: 11.5,
                  fontWeight: 900,
                  whiteSpace: "nowrap",
                }}
              >
                Live tracking
              </span>
            </div>

            <div style={{ display: "grid", gap: 10, marginTop: 16 }}>
              {[
                {
                  title: liveDeliverable ? "Deliverable generated" : "Ready for execution",
                  detail: liveDeliverable
                    ? "Latest client deliverable is ready for review."
                    : "Run selected agents to generate a new client deliverable.",
                  status: liveDeliverable ? "Ready" : "Waiting",
                  tone: liveDeliverable ? "#22c55e" : "var(--color-brand)",
                  icon: liveDeliverable ? "✓" : "→",
                },
                {
                  title: executionState === "completed" ? "Execution completed" : executionState === "running" ? "Execution running" : "Execution prepared",
                  detail: executionState === "running"
                    ? "Agent workflow is processing the current request."
                    : "Governed execution is prepared for the selected agents.",
                  status: executionState === "completed" ? "Complete" : executionState === "running" ? "Running" : "Prepared",
                  tone: executionState === "running" ? "#f59e0b" : "#06b6d4",
                  icon: executionState === "running" ? "…" : "⚡",
                },
                {
                  title: reviewStatus === "approved" ? "Client approved" : reviewStatus === "rejected" ? "Changes requested" : "Client review",
                  detail: reviewStatus === "approved"
                    ? "The deliverable has been approved."
                    : reviewStatus === "rejected"
                      ? "Feedback has been submitted for revision."
                      : "Approval controls are ready when the output is reviewed.",
                  status: reviewStatus === "approved" ? "Approved" : reviewStatus === "rejected" ? "Revision" : "Pending",
                  tone: reviewStatus === "rejected" ? "#ef4444" : "var(--color-brand)",
                  icon: reviewStatus === "approved" ? "✓" : reviewStatus === "rejected" ? "!" : "○",
                },
              ].map((item) => (
                <div
                  key={item.title}
                  style={{
                    border: "1px solid #e5eaf2",
                    borderRadius: 16,
                    background: "#fff",
                    padding: "12px 14px",
                    display: "grid",
                    gridTemplateColumns: "34px minmax(0,1fr) auto",
                    gap: 12,
                    alignItems: "center",
                    boxShadow: "0 8px 22px rgba(15,23,42,.035)",
                  }}
                >
                  <div
                    style={{
                      width: 32,
                      height: 32,
                      borderRadius: 12,
                      background: `${item.tone}18`,
                      color: item.tone,
                      display: "inline-flex",
                      alignItems: "center",
                      justifyContent: "center",
                      fontWeight: 950,
                    }}
                  >
                    {item.icon}
                  </div>

                  <div style={{ minWidth: 0 }}>
                    <div style={{ fontSize: 13, fontWeight: 950, color: "var(--color-dark)" }}>{item.title}</div>
                    <div style={{ marginTop: 3, fontSize: 12, fontWeight: 700, color: "var(--color-muted)", lineHeight: 1.35 }}>
                      {item.detail}
                    </div>
                  </div>

                  <span
                    style={{
                      border: "1px solid #e5eaf2",
                      background: "#f8fafc",
                      borderRadius: 999,
                      padding: "6px 9px",
                      color: item.tone,
                      fontSize: 11.5,
                      fontWeight: 900,
                      whiteSpace: "nowrap",
                    }}
                  >
                    {item.status}
                  </span>
                </div>
              ))}
            </div>
          </div>'''

src = src[:start] + new_activity + src[end:]

PAGE.write_text(src, encoding="utf-8")

print("ACTIVITY_BLOCK_ONLY_POLISHED")
print(f"Backup: {backup}")
print("Activity block count:", src.count("Latest governed activity"))
print("Output viewer preserved:", src.count("Execution output viewer"))
print("Enterprise modal preserved:", "showEnterpriseCatalogueModal" in src)
print("Right execution column locked:", src.count("Live execution flow") == 1 and src.count("Business profile applied") == 1 and src.count("Governed execution, every time.") == 1)
print("Old mutations:", src.count("applyHorizontalExecutionLayout") + src.count("applyPremiumExecutionSectionLayout"))