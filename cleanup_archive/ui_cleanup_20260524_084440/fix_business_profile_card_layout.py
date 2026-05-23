from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

text = PAGE.read_text(encoding="utf-8")
backup = BACKUP_DIR / f"client_page_before_business_profile_layout_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
backup.write_text(text, encoding="utf-8")

text = text.replace(
    'gridTemplateColumns: "repeat(8, minmax(150px, 1fr))",',
    'gridTemplateColumns: "repeat(auto-fit, minmax(190px, 1fr))",'
)

text = text.replace(
    'gap: 12,',
    'gap: 14,',
    1
)

text = text.replace(
    'rows={3}',
    'rows={4}',
    1
)

# Replace stale status label if present.
text = text.replace(
    '✓ Applied to execution',
    '{businessProfileSaved ? "✓ Saved to execution context" : "Not saved yet"}'
)

PAGE.write_text(text, encoding="utf-8")

print("BUSINESS_PROFILE_CARD_LAYOUT_FIXED")
print(f"Backup: {backup}")