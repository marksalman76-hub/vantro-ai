from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

src = PAGE.read_text(encoding="utf-8")
backup = BACKUPS / f"client_page_before_activity_next_actions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
backup.write_text(src, encoding="utf-8")

anchor = '''              </div>
            </div>
          </div>

          <div style={{ ...cardStyle, minHeight: 355, overflow: "hidden" }}>'''

insert = r'''              </div>

              <div
                style={{
                  marginTop: 13,
                  borderTop: "1px solid #edf1f6",
                  paddingTop: 12,
                  display: "grid",
                  gridTemplateColumns: "repeat(3, minmax(0, 1fr))",
                  gap: 8,
                }}
              >
                {[
                  ["Review latest output", liveDeliverable ? "Ready" : "Waiting", liveDeliverable ? "✓" : "○"],
                  ["Approve or request changes", reviewStatus === "pending" ? "Next" : reviewStatus === "approved" ? "Done" : "Revision", reviewStatus === "approved" ? "✓" : "→"],
                  ["Run next optimisation", reviewStatus === "approved" ? "Available" : "After review", "↗"],
                ].map(([title, status, icon]) => (
                  <div
                    key={title}
                    style={{
                      border: "1px solid #e5eaf2",
                      background: "#fff",
                      borderRadius: 14,
                      padding: "9px 10px",
                      minHeight: 58,
                    }}
                  >
                    <div style={{ display: "flex", alignItems: "center", gap: 7 }}>
                      <span style={{ color: "var(--color-brand)", fontWeight: 950 }}>{icon}</span>
                      <span style={{ fontSize: 11.5, fontWeight: 950, color: "var(--color-dark)", lineHeight: 1.2 }}>
                        {title}
                      </span>
                    </div>
                    <div style={{ marginTop: 5, fontSize: 11, fontWeight: 850, color: "var(--color-muted)" }}>
                      {status}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div style={{ ...cardStyle, minHeight: 355, overflow: "hidden" }}>'''

if anchor not in src:
    raise SystemExit("ERROR: Snapshot-to-output boundary not found. No changes made.")

src = src.replace(anchor, insert, 1)

PAGE.write_text(src, encoding="utf-8")

print("ACTIVITY_NEXT_ACTIONS_ADDED")
print(f"Backup: {backup}")
print("Next actions installed:", "Review latest output" in src and "Run next optimisation" in src)
print("Snapshot preserved:", "Execution snapshot" in src)
print("Output viewer preserved:", src.count("Execution output viewer"))
print("Enterprise modal preserved:", "showEnterpriseCatalogueModal" in src)
print("Right execution column locked:", src.count("Live execution flow") == 1 and src.count("Business profile applied") == 1 and src.count("Governed execution, every time.") == 1)
print("Old mutations:", src.count("applyHorizontalExecutionLayout") + src.count("applyPremiumExecutionSectionLayout"))