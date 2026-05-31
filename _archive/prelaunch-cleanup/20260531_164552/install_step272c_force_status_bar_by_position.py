from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
text = PAGE.read_text(encoding="utf-8")

backup = BACKUPS / f"client_page_before_step272c_force_status_bar_{timestamp}.tsx"
backup.write_text(text, encoding="utf-8")

package_pos = text.find('["Package", account?.package || account?.package_name || "Not assigned"]')
business_pos = text.find("BUSINESS PROFILE INTELLIGENCE")

if package_pos == -1:
    raise SystemExit("ERROR: Package summary marker not found.")

if business_pos == -1:
    raise SystemExit("ERROR: Business profile marker not found.")

start = text.rfind("\n        <div", 0, package_pos)
end = text.rfind("\n        <div style={{ ...cardStyle", package_pos, business_pos)

if start == -1 or end == -1 or end <= start:
    raise SystemExit("ERROR: Could not locate summary card block boundaries.")

replacement = '''
        <div
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

text = text[:start] + replacement + text[end:]

PAGE.write_text(text, encoding="utf-8")

print("STEP_272C_FORCE_STATUS_BAR_BY_POSITION_INSTALLED")
print(f"Backup: {backup}")
print("STEP_272C_OK")