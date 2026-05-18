from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
text = PAGE.read_text(encoding="utf-8")

backup = BACKUPS / f"client_page_before_step274_balance_execution_{timestamp}.tsx"
backup.write_text(text, encoding="utf-8")

replacements = {
    'gridTemplateColumns: "minmax(620px,1.15fr) minmax(420px,.85fr)"': 'gridTemplateColumns: "minmax(500px,.92fr) minmax(520px,1.08fr)"',
    'maxHeight: 240,': 'maxHeight: 210,',
    'padding: 10,': 'padding: 8,',
    'gap: 10,': 'gap: 8,',
    'rows={7}': 'rows={5}',
    'minHeight: 300,': 'minHeight: 230,',
    'padding: 34,': 'padding: 26,',
    'fontSize: 20, fontWeight: 800, marginBottom: 8': 'fontSize: 18, fontWeight: 800, marginBottom: 6',
    'padding: "16px 20px"': 'padding: "14px 18px"',
    'marginTop: 22,': 'marginTop: 18,',
}

for old, new in replacements.items():
    text = text.replace(old, new)

PAGE.write_text(text, encoding="utf-8")

print("STEP_274_EXECUTION_WORKSPACE_BALANCED")
print(f"Backup: {backup}")
print("STEP_274_OK")