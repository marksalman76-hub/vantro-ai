from pathlib import Path
from datetime import datetime
import re

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
text = PAGE.read_text(encoding="utf-8")

backup = BACKUPS / f"client_page_before_step272_status_bar_{timestamp}.tsx"
backup.write_text(text, encoding="utf-8")

start = text.find('{[\n            ["Package", account?.package || account?.package_name || "Not assigned"],')
if start == -1:
    raise SystemExit("ERROR: Summary card map start not found.")

container_start = text.rfind('<div', 0, start)
container_end_marker = '</div>\n\n        <div style={{ ...cardStyle'
container_end = text.find(container_end_marker, start)

if container_start == -1 or container_end == -1:
    raise SystemExit("ERROR: Summary card container boundaries not found.")

container_end += len('</div>\n\n')

replacement = '''        <div
          style={{
            marginTop: 20,
            padding: "14px 18px",
            borderRadius: 22,
            background: "rgba(15,23,42,.52)",
            border: "1px solid rgba(148,163,184,.14)",
            boxShadow: "0 18px 50px rgba(0,0,0,.18)",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            gap: 16,
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
                gap: 10,
                minWidth: 150,
              }}
            >
              <span
                style={{
                  width: 8,
                  height: 8,
                  borderRadius: 999,
                  background: "#38bdf8",
                  boxShadow: "0 0 18px rgba(56,189,248,.7)",
                }}
              />
              <div>
                <div style={{ color: "#94a3b8", fontSize: 11, lineHeight: 1 }}>
                  {label}
                </div>
                <strong style={{ display: "block", marginTop: 5, fontSize: 17 }}>
                  {value}
                </strong>
              </div>
            </div>
          ))}
        </div>

'''

text = text[:container_start] + replacement + text[container_end:]

PAGE.write_text(text, encoding="utf-8")

print("STEP_272_PREMIUM_STATUS_BAR_INSTALLED")
print(f"Backup: {backup}")
print("STEP_272_OK")