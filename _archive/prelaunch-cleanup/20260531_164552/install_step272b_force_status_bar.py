from pathlib import Path
from datetime import datetime
import re

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
text = PAGE.read_text(encoding="utf-8")

backup = BACKUPS / f"client_page_before_step272b_force_status_bar_{timestamp}.tsx"
backup.write_text(text, encoding="utf-8")

pattern = r'''
        <div
          style=\{\{
            display: "grid",
            gridTemplateColumns: "repeat\(4,minmax\(0,1fr\)\)",
[\s\S]*?
          \}\)}
        </div>

        <div style=\{\{ \.\.\.cardStyle, padding: 22, marginTop: 18 \}\}>
'''

replacement = '''
        <div
          style={{
            marginTop: 18,
            padding: "13px 16px",
            borderRadius: 22,
            background: "rgba(15,23,42,.50)",
            border: "1px solid rgba(148,163,184,.14)",
            boxShadow: "0 18px 50px rgba(0,0,0,.16)",
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
                minWidth: 145,
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
                <div style={{ color: "#94a3b8", fontSize: 11 }}>
                  {label}
                </div>
                <strong style={{ display: "block", marginTop: 3, fontSize: 16 }}>
                  {value}
                </strong>
              </div>
            </div>
          ))}
        </div>

        <div style={{ ...cardStyle, padding: 22, marginTop: 18 }}>
'''

new_text, count = re.subn(pattern, replacement, text, count=1, flags=re.VERBOSE)

if count != 1:
    raise SystemExit("ERROR: Summary card block was not replaced.")

PAGE.write_text(new_text, encoding="utf-8")

print("STEP_272B_FORCE_STATUS_BAR_INSTALLED")
print(f"Backup: {backup}")
print("STEP_272B_OK")