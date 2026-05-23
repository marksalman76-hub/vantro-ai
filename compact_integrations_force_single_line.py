from pathlib import Path
from datetime import datetime

path = Path("frontend/src/app/client/page.tsx")
text = path.read_text(encoding="utf-8")

backup_dir = Path("backups")
backup_dir.mkdir(exist_ok=True)

backup = backup_dir / f"client_page_before_compact_integrations_single_line_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
backup.write_text(text, encoding="utf-8")

replacements = [
    (
        'display: "grid",\n            gridTemplateColumns: "repeat(auto-fit,minmax(220px,1fr))",',
        'display: "flex",\n            flexWrap: "nowrap",\n            overflowX: "auto",\n            gap: 10,'
    ),
    (
        'minWidth: 220,',
        'minWidth: 155,'
    ),
    (
        'padding: "16px 18px",',
        'padding: "10px 12px",'
    ),
    (
        'fontSize: 14,',
        'fontSize: 13,'
    ),
]

for old, new in replacements:
    if old in text:
        text = text.replace(old, new)

path.write_text(text, encoding="utf-8")

print("COMPACT_INTEGRATIONS_SINGLE_LINE_FIXED")
print(f"Backup: {backup}")