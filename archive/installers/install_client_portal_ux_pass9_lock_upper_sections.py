from pathlib import Path
from datetime import datetime
import re

ROOT = Path.cwd()
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUP_DIR / f"client_page_before_ux_pass9_lock_upper_sections_{timestamp}.tsx"

text = PAGE.read_text(encoding="utf-8")
original = text
backup.write_text(original, encoding="utf-8")

# Lock marker for completed sections.
if "client_portal_upper_sections_locked_pre_bottom_rebuild" not in text:
    text = text.replace(
        "// client_portal_ux_pass8_compact_workspace_pills",
        "// client_portal_ux_pass8_compact_workspace_pills\n// client_portal_upper_sections_locked_pre_bottom_rebuild"
    )

# Business profile grid: force one-line horizontal row with compact cards.
text = text.replace(
    'gridTemplateColumns: "repeat(auto-fit,minmax(210px,1fr))"',
    'gridTemplateColumns: "repeat(8, minmax(130px, 1fr))"'
)

# Make business profile inputs smaller so all 8 fit on one row.
text = text.replace(
    'rows={3}',
    'rows={2}'
)

# Compact the specific business profile field styling.
text = text.replace(
    'padding: "16px 18px"',
    'padding: "11px 12px"'
)

text = text.replace(
    'fontSize: 13.5,',
    'fontSize: 12,'
)

text = text.replace(
    'lineHeight: 1.55,',
    'lineHeight: 1.35,'
)

# Remove excessive min heights from compact business profile cards.
text = re.sub(r'\n\s*minHeight:\s*120,', '', text)

# Slightly reduce section vertical whitespace.
text = text.replace(
    'gap: 18,\n            }}\n          >\n            {[\n              ["Business niche"',
    'gap: 12,\n            }}\n          >\n            {[\n              ["Business niche"'
)

if text == original:
    raise RuntimeError("No Pass 9 changes applied.")

PAGE.write_text(text, encoding="utf-8")

TEST = ROOT / "test_client_portal_ux_pass9_lock_upper_sections.py"
TEST.write_text(r'''
from pathlib import Path

PAGE = Path("frontend/src/app/client/page.tsx")
text = PAGE.read_text(encoding="utf-8")

print("CLIENT_PORTAL_UX_PASS9_LOCK_UPPER_SECTIONS_RESULTS")

checks = {
    "lock_marker": "client_portal_upper_sections_locked_pre_bottom_rebuild" in text,
    "business_one_line_grid": 'gridTemplateColumns: "repeat(8, minmax(130px, 1fr))"' in text,
    "compact_rows": "rows={2}" in text,
    "compact_padding": 'padding: "11px 12px"' in text,
    "no_window_innerwidth": "window.innerWidth" not in text,
}

for key, value in checks.items():
    print(key, value)

assert all(checks.values())

print("CLIENT_PORTAL_UX_PASS9_LOCK_UPPER_SECTIONS_OK")
'''.lstrip(), encoding="utf-8")

print("CLIENT_PORTAL_UX_PASS9_LOCK_UPPER_SECTIONS_INSTALLED")
print(f"Backup: {backup}")
print(f"Updated: {PAGE}")
print(f"Created: {TEST}")