from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
text = PAGE.read_text(encoding="utf-8")

backup = BACKUPS / f"client_page_before_step271_slim_cards_{timestamp}.tsx"
backup.write_text(text, encoding="utf-8")

text = text.replace(
'''gridTemplateColumns: "repeat(4,minmax(0,1fr))",
            gap: 18,
            marginTop: 24,''',
'''gridTemplateColumns: "repeat(4,minmax(0,1fr))",
            gap: 12,
            marginTop: 20,''',
)

text = text.replace(
'''<div key={label} style={{ ...cardStyle, padding: 18 }}>''',
'''<div
              key={label}
              style={{
                ...cardStyle,
                padding: "14px 16px",
                minHeight: 82,
                display: "flex",
                flexDirection: "column",
                justifyContent: "center",
              }}
            >''',
)

text = text.replace(
'''<div style={{ color: "#94a3b8", fontSize: 13 }}>{label}</div>''',
'''<div style={{ color: "#94a3b8", fontSize: 12 }}>{label}</div>''',
)

text = text.replace(
'''<strong style={{ display: "block", marginTop: 10, fontSize: 24 }}>''',
'''<strong style={{ display: "block", marginTop: 6, fontSize: 21 }}>''',
)

PAGE.write_text(text, encoding="utf-8")

print("STEP_271_SLIM_SUMMARY_CARDS_INSTALLED")
print(f"Backup: {backup}")
print("STEP_271_OK")