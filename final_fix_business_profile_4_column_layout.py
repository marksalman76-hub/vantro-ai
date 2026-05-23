from pathlib import Path
from datetime import datetime

path = Path("frontend/src/app/client/page.tsx")
text = path.read_text(encoding="utf-8")

backup_dir = Path("backups")
backup_dir.mkdir(exist_ok=True)
backup = backup_dir / f"client_page_before_final_4_column_business_profile_layout_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
backup.write_text(text, encoding="utf-8")

text = text.replace(
    'gridTemplateColumns: "repeat(5, minmax(0, 1fr))"',
    'gridTemplateColumns: "repeat(4, minmax(0, 1fr))"',
    1,
)

text = text.replace(
    'gridColumn: "span 1",',
    'gridColumn: label === "Key differentiators" ? "span 3" : "span 1",',
    1,
)

text = text.replace(
    '["notes", "◌", "Key differentiators", "What makes your business unique? Benefits, values, or competitive advantages.", "textarea", "normal"],',
    '["notes", "◌", "Key differentiators", "What makes your business unique? Benefits, values, or competitive advantages.", "textarea", "wide"],',
    1,
)

path.write_text(text, encoding="utf-8")

print("FINAL_4_COLUMN_BUSINESS_PROFILE_LAYOUT_FIXED")
print(f"Backup: {backup}")