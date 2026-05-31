from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
text = PAGE.read_text(encoding="utf-8")

backup = BACKUPS / f"client_page_before_step290_spacing_readability_{timestamp}.tsx"
backup.write_text(text, encoding="utf-8")

replacements = [
    ('padding: "28px 34px 56px"', 'padding: "30px 34px 60px"'),
    ('marginBottom: 20,', 'marginBottom: 22,'),
    ('padding: 28,', 'padding: 30,'),
    ('padding: "14px 16px"', 'padding: "16px 18px"'),
    ('padding: "14px 15px"', 'padding: "16px 16px"'),
    ('rows={2}', 'rows={3}'),
    ('fontSize: 13,', 'fontSize: 13.5,'),
    ('lineHeight: 1.45,', 'lineHeight: 1.55,'),
    ('gap: 14,', 'gap: 16,'),
    ('gap: 16,', 'gap: 18,'),
    ('padding: 22,', 'padding: 24,'),
    ('borderRadius: 22,', 'borderRadius: 24,'),
    ('fontSize: 20,', 'fontSize: 21,'),
    ('minHeight: 150,', 'minHeight: 170,'),
    ('minHeight: 170,', 'minHeight: 185,'),
]

for old, new in replacements:
    text = text.replace(old, new)

PAGE.write_text(text, encoding="utf-8")

print("STEP_290_FINAL_SPACING_READABILITY_INSTALLED")
print(f"Backup: {backup}")
print("STEP_290_OK")