from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
text = PAGE.read_text(encoding="utf-8")

backup = BACKUPS / f"client_page_before_step288_expand_width_{timestamp}.tsx"
backup.write_text(text, encoding="utf-8")

replacements = [
    ('maxWidth: 1320, margin: "0 auto", padding: "28px 28px 56px"', 'maxWidth: "none", width: "100%", padding: "28px 34px 56px", boxSizing: "border-box"'),
    ('gridTemplateColumns: "1.05fr .95fr .9fr .85fr"', 'gridTemplateColumns: "1.15fr .95fr .95fr .85fr"'),
    ('gridTemplateColumns: "1fr 1.15fr"', 'gridTemplateColumns: "1fr 1.35fr"'),
]

for old, new in replacements:
    text = text.replace(old, new)

PAGE.write_text(text, encoding="utf-8")

print("STEP_288_EXPAND_DASHBOARD_WIDTH_INSTALLED")
print(f"Backup: {backup}")
print("STEP_288_OK")