from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

src = PAGE.read_text(encoding="utf-8")
backup = BACKUPS / f"client_page_before_activity_snapshot_graph_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
backup.write_text(src, encoding="utf-8")

anchor = '''            </div>
          </div>

          <div style={{ ...cardStyle, minHeight: 355, overflow: "hidden" }}>
            <div style={{ display: "flex", justifyContent: "space-between", gap: 16, flexWrap: "wrap" }}>'''

snapshot = r'''            </div>

            <div
              style={{
                marginTop: 16,
                border: "1px solid #e5eaf2",
                borderRadius: 18,
                background: "linear-gradient(180deg,#ffffff 0%,#f8fafc 100%)",
                padding: 14,
              }}
            >
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 12 }}>
                <div>
                  <div style={{ fontSize: 13, fontWeight: 950, color: "var(--color-dark)" }}>Execution snapshot</div>
                  <div style={{ marginTop: 3, fontSize: 11.5, fontWeight: 700, color: "var(--color-muted)" }}>
                    Live progress across the latest client workflow.
                  </div>
                </div>
                <span
                  style={{
                    background: "#eef2ff",
                    color: "var(--color-brand)",
                    borderRadius: 999,
                    padding: "6px 9px",
                    fontSize: 11.5,
                    fontWeight: 900,
                    whiteSpace: "nowrap",
                  }}
                >
                  Updated now
                </span>
              </div>

              <div style={{ display: "grid", gap: 9, marginTop: 13 }}>
                {[
                  ["Generated", liveDeliverable ? 100 : 35, "#22c55e"],
                  ["Reviewed", reviewStatus === "approved" || reviewStatus === "rejected" ? 100 : 55, "var(--color-brand)"],
                  ["Approved", reviewStatus === "approved" ? 100 : 25, "var(--color-teal)"],
                  ["Pending", reviewStatus === "pending" ? 65 : 20, "#f59e0b"],
                ].map(([label, value, color]) => (
                  <div key={label} style={{ display: "grid", gridTemplateColumns: "86px 1fr 42px", gap: 10, alignItems: "center" }}>
                    <div style={{ fontSize: 11.5, fontWeight: 900, color: "var(--color-dark)" }}>{label}</div>
                    <div style={{ height: 9, borderRadius: 999, background: "#eef2f7", overflow: "hidden" }}>
                      <div
                        style={{
                          width: `${value}%`,
                          height: "100%",
                          borderRadius: 999,
                          background: String(color),
                        }}
                      />
                    </div>
                    <div style={{ textAlign: "right", fontSize: 11.5, fontWeight: 900, color: "var(--color-muted)" }}>
                      {value}%
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div style={{ ...cardStyle, minHeight: 355, overflow: "hidden" }}>
            <div style={{ display: "flex", justifyContent: "space-between", gap: 16, flexWrap: "wrap" }}>'''

if anchor not in src:
    raise SystemExit("ERROR: Activity-to-output boundary not found. No changes made.")

src = src.replace(anchor, snapshot, 1)

PAGE.write_text(src, encoding="utf-8")

print("ACTIVITY_SNAPSHOT_BAR_GRAPH_ADDED")
print(f"Backup: {backup}")
print("Snapshot installed:", "Execution snapshot" in src and "Updated now" in src)
print("Activity preserved:", src.count("Latest governed activity"))
print("Output viewer preserved:", src.count("Execution output viewer"))
print("Enterprise modal preserved:", "showEnterpriseCatalogueModal" in src)
print("Right execution column locked:", src.count("Live execution flow") == 1 and src.count("Business profile applied") == 1 and src.count("Governed execution, every time.") == 1)
print("Old mutations:", src.count("applyHorizontalExecutionLayout") + src.count("applyPremiumExecutionSectionLayout"))