from pathlib import Path
from datetime import datetime

path = Path("frontend/src/app/client/page.tsx")
text = path.read_text(encoding="utf-8")

backup_dir = Path("backups")
backup_dir.mkdir(exist_ok=True)
backup = backup_dir / f"client_page_before_force_5_columns_2_rows_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
backup.write_text(text, encoding="utf-8")

# Force exact 5-column Business Profile grid.
text = text.replace(
    'gridTemplateColumns: "repeat(4, minmax(0, 1fr))"',
    'gridTemplateColumns: "repeat(5, minmax(0, 1fr))"',
)

text = text.replace(
    'gridTemplateColumns: "repeat(5, minmax(0, 1fr))"',
    'gridTemplateColumns: "repeat(5, minmax(0, 1fr))"',
)

# Every Business Profile card must occupy exactly one grid cell.
text = text.replace(
    'gridColumn: label === "Key differentiators" ? "span 3" : "span 1",',
    'gridColumn: "span 1",',
)

text = text.replace(
    'gridColumn: size === "wide" ? "span 2" : "span 1",',
    'gridColumn: "span 1",',
)

# Ensure Key differentiators is normal size, not wide.
text = text.replace(
    '["notes", "◌", "Key differentiators", "What makes your business unique? Benefits, values, or competitive advantages.", "textarea", "wide"],',
    '["notes", "◌", "Key differentiators", "What makes your business unique? Benefits, values, or competitive advantages.", "textarea", "normal"],',
)

# Slightly compact cards to support 5 columns cleanly.
text = text.replace("minHeight: 104,", "minHeight: 96,")
text = text.replace("padding: 13,", "padding: 11,")

path.write_text(text, encoding="utf-8")

print("BUSINESS_PROFILE_5_COLUMNS_2_ROWS_FORCED")
print(f"Backup: {backup}")