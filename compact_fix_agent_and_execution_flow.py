from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

src = PAGE.read_text(encoding="utf-8")
backup = BACKUPS / f"client_page_before_compact_agent_execution_flow_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
backup.write_text(src, encoding="utf-8")

src = src.replace(
'''                <div style={{ display: "grid", gap: 7 }}>
                  {(account?.active_agents || DEFAULT_AGENTS).map((agent) => {''',
'''                <div
                  style={{
                    display: "grid",
                    gap: 7,
                    maxHeight: 265,
                    overflowY: "auto",
                    paddingRight: 4,
                  }}
                >
                  {(account?.active_agents || DEFAULT_AGENTS).map((agent) => {'''
)

src = src.replace(
'''            <div style={{ display: "grid", gap: 12, marginTop: 20 }}>
              {[
                ["Execution requested", executionState === "idle" ? "Waiting" : "Started", liveDeliverable?.created_at || "Live"],
                ["Deliverable status", executionState === "completed" ? "Ready" : "Pending", liveDeliverable?.created_at || "Live"],
                ["Client review", reviewStatus === "approved" ? "Approve ✓d" : reviewStatus === "rejected" ? "Revision requested" : "Pending", reviewStatus === "approved" ? "Complete" : "Open"],
                ["Execution ready", "Next", "—"],
              ].map(([title, status, time], index) => (''',
'''            <div style={{ display: "grid", gap: 8, marginTop: 12 }}>
              {[
                ["Execution requested", executionState === "idle" ? "Waiting" : "Started", liveDeliverable?.created_at || "Live"],
                ["Business profile applied", "Context loaded", "Live"],
                ["Deliverable status", executionState === "completed" ? "Ready" : "Pending", liveDeliverable?.created_at || "Live"],
                ["Client review", reviewStatus === "approved" ? "Approved" : reviewStatus === "rejected" ? "Revision requested" : "Pending", reviewStatus === "approved" ? "Complete" : "Open"],
                ["Execution ready", "Next", "—"],
              ].map(([title, status, time], index) => ('''
)

src = src.replace(
'''                <div key={title} style={{ display: "grid", gridTemplateColumns: "34px 1fr auto", gap: 12, alignItems: "center" }}>''',
'''                <div key={title} style={{ display: "grid", gridTemplateColumns: "30px 1fr auto", gap: 9, alignItems: "center" }}>'''
)

src = src.replace(
'''                      width: 30,
                      height: 30,
                      minWidth: 30,
                      minHeight: 30,''',
'''                      width: 26,
                      height: 26,
                      minWidth: 26,
                      minHeight: 26,'''
)

src = src.replace(
'''                </div>
              ))}
            </div>
          </div>''',
'''                </div>
              ))}

              <div
                style={{
                  marginTop: 2,
                  border: "1px solid #dbeafe",
                  borderRadius: 14,
                  background: "linear-gradient(135deg,#eff6ff,#ffffff)",
                  padding: "9px 10px",
                  display: "grid",
                  gridTemplateColumns: "26px 1fr",
                  gap: 9,
                  alignItems: "center",
                }}
              >
                <div
                  style={{
                    width: 26,
                    height: 26,
                    borderRadius: 9,
                    background: "#ffffff",
                    color: "var(--color-brand)",
                    display: "inline-flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontWeight: 900,
                    boxShadow: "0 4px 12px rgba(37,99,235,.08)",
                  }}
                >
                  ✦
                </div>
                <div>
                  <div style={{ fontSize: 12, fontWeight: 900, color: "var(--color-dark)" }}>
                    Governed execution, every time.
                  </div>
                  <div style={{ marginTop: 2, fontSize: 11.5, fontWeight: 700, color: "var(--color-muted)", lineHeight: 1.35 }}>
                    Tracked, logged, quality-checked, and approval-routed.
                  </div>
                </div>
              </div>
            </div>
          </div>''',
1
)

PAGE.write_text(src, encoding="utf-8")

print("COMPACT_AGENT_AND_EXECUTION_FLOW_FIXED")
print(f"Backup: {backup}")
print("Updated: frontend/src/app/client/page.tsx")
print("Kept compact tiny button format.")