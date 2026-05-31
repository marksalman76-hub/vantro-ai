from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
text = PAGE.read_text(encoding="utf-8")

backup = BACKUPS / f"client_page_before_step289_header_insight_strip_{timestamp}.tsx"
backup.write_text(text, encoding="utf-8")

old = '''        <section
          style={{
            display: "flex",
            gap: 28,
            alignItems: "center",
            flexWrap: "wrap",
            marginBottom: 20,
          }}
        >
          {[
            ["Package", account?.package || account?.package_name || "Premium Demo"],
            ["Credits", String(creditsRemaining)],
            ["Status", account?.status || account?.package_status || "active"],
            ["Agents", String(account?.active_agents?.length || 7)],
          ].map(([label, value]) => (
            <div key={label} style={{ display: "flex", alignItems: "center", gap: 10 }}>
              <span
                style={{
                  width: 9,
                  height: 9,
                  borderRadius: 999,
                  background: "#2563eb",
                }}
              />
              <span style={{ color: "#64748b", fontSize: 13 }}>{label}</span>
              <strong style={{ fontSize: 18 }}>{value}</strong>
            </div>
          ))}
        </section>'''

new = '''        <section
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
        </section>'''

if old not in text:
    raise SystemExit("ERROR: Metrics row block not found. Do not continue.")

text = text.replace(old, new)

PAGE.write_text(text, encoding="utf-8")

print("STEP_289_HEADER_INSIGHT_STRIP_INSTALLED")
print(f"Backup: {backup}")
print("STEP_289_OK")