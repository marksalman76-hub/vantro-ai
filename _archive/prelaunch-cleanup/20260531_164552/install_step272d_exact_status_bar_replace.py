from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
text = PAGE.read_text(encoding="utf-8")

backup = BACKUPS / f"client_page_before_step272d_exact_status_bar_{timestamp}.tsx"
backup.write_text(text, encoding="utf-8")

old = '''        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(4,minmax(0,1fr))",
            gap: 12,
            marginTop: 20,
          }}
        >
          {[
            ["Package", account?.package || account?.package_name || "Not assigned"],
            ["Credits Remaining", String(creditsRemaining)],
            ["Status", account?.status || account?.package_status || "Unknown"],
            ["Active Agents", String(account?.active_agents?.length || 0)],
          ].map(([label, value]) => (
            <div
              key={label}
              style={{
                ...cardStyle,
                padding: "14px 16px",
                minHeight: 82,
                display: "flex",
                flexDirection: "column",
                justifyContent: "center",
              }}
            >
              <div style={{ color: "#94a3b8", fontSize: 12 }}>{label}</div>

              <strong style={{ display: "block", marginTop: 6, fontSize: 21 }}>
                {value}
              </strong>
            </div>
          ))}
        </div>
'''

new = '''        <div
          style={{
            marginTop: 18,
            padding: "12px 16px",
            borderRadius: 999,
            background: "rgba(15,23,42,.48)",
            border: "1px solid rgba(148,163,184,.14)",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            gap: 18,
            flexWrap: "wrap",
          }}
        >
          {[
            ["Package", account?.package || account?.package_name || "Not assigned"],
            ["Credits", String(creditsRemaining)],
            ["Status", account?.status || account?.package_status || "Unknown"],
            ["Agents", String(account?.active_agents?.length || 0)],
          ].map(([label, value]) => (
            <div
              key={label}
              style={{
                display: "flex",
                alignItems: "center",
                gap: 9,
                minWidth: 130,
              }}
            >
              <span
                style={{
                  width: 7,
                  height: 7,
                  borderRadius: 999,
                  background: "#38bdf8",
                  boxShadow: "0 0 16px rgba(56,189,248,.75)",
                }}
              />
              <div>
                <span style={{ color: "#94a3b8", fontSize: 11 }}>
                  {label}
                </span>
                <strong style={{ marginLeft: 8, fontSize: 15 }}>
                  {value}
                </strong>
              </div>
            </div>
          ))}
        </div>
'''

if old not in text:
    raise SystemExit("ERROR: Exact old summary block not found.")

text = text.replace(old, new)

PAGE.write_text(text, encoding="utf-8")

print("STEP_272D_EXACT_STATUS_BAR_REPLACED")
print(f"Backup: {backup}")
print("STEP_272D_OK")