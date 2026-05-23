from pathlib import Path
from datetime import datetime

path = Path("frontend/src/app/client/page.tsx")
text = path.read_text(encoding="utf-8")

backup_dir = Path("backups")
backup_dir.mkdir(exist_ok=True)
backup = backup_dir / f"client_page_before_compact_key_diff_layout_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
backup.write_text(text, encoding="utf-8")

# Restore compact 5-column business profile grid.
text = text.replace(
    'gridTemplateColumns: "repeat(4, minmax(0, 1fr))"',
    'gridTemplateColumns: "repeat(5, minmax(0, 1fr))"',
    1,
)

# Stop Key differentiators from forcing Goals onto a separate row.
text = text.replace(
    'gridColumn: label === "Key differentiators" ? "span 3" : "span 1",',
    'gridColumn: "span 1",',
    1,
)

# Make cards slightly more compact so the section height stays tight.
text = text.replace(
    'padding: 13,',
    'padding: 12,',
    1,
)

text = text.replace(
    'minHeight: 104,',
    'minHeight: 98,',
    1,
)

# Keep the textarea height compact if this marker exists.
text = text.replace(
    'minHeight: 52,',
    'minHeight: 48,',
)

# Make Key differentiators label shorter only in the card title if needed.
# Placeholder remains descriptive.
text = text.replace(
    '["notes", "◌", "Key differentiators", "What makes your business unique? Benefits, values, or competitive advantages.", "textarea", "wide"],',
    '["notes", "◌", "Key differentiators", "What makes your business unique? Benefits, values, or competitive advantages.", "textarea", "normal"],',
    1,
)

path.write_text(text, encoding="utf-8")

print("BUSINESS_PROFILE_COMPACT_KEY_DIFF_LAYOUT_FIXED")
print(f"Backup: {backup}")