from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
text = PAGE.read_text(encoding="utf-8")

backup = BACKUPS / f"client_page_before_step270_density_pass_{timestamp}.tsx"
backup.write_text(text, encoding="utf-8")

replacements = {
    'padding: "34px 22px"': 'padding: "26px 22px"',
    'fontSize: 48, marginTop: 10': 'fontSize: 44, marginTop: 8',
    'lineHeight: 1.7,\n                marginTop: 14': 'lineHeight: 1.55,\n                marginTop: 10',
    'marginTop: 34,': 'marginTop: 24,',
    'gridTemplateColumns: "repeat(auto-fit,minmax(220px,1fr))"': 'gridTemplateColumns: "repeat(4,minmax(0,1fr))"',
    '<div key={label} style={{ ...cardStyle, padding: 20 }}>': '<div key={label} style={{ ...cardStyle, padding: 18 }}>',
    'marginTop: 22 }}>': 'marginTop: 18 }}>',
    'fontSize: 23, marginTop: 6': 'fontSize: 22, marginTop: 5',
    'lineHeight: 1.55,\n                  marginTop: 7': 'lineHeight: 1.45,\n                  marginTop: 5',
    'padding: "9px 13px"': 'padding: "8px 12px"',
    'minHeight: 56,': 'minHeight: 52,',
    'gridTemplateColumns: "minmax(350px,410px) 1fr"': 'gridTemplateColumns: "minmax(340px,400px) 1fr"',
    'marginTop: 22,\n            alignItems: "start"': 'marginTop: 18,\n            alignItems: "start"',
}

for old, new in replacements.items():
    text = text.replace(old, new)

PAGE.write_text(text, encoding="utf-8")

print("STEP_270_CLIENT_UX_DENSITY_PASS_INSTALLED")
print(f"Backup: {backup}")
print("STEP_270_OK")