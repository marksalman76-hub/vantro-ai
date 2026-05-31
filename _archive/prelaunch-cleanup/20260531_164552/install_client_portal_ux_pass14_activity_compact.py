from pathlib import Path
from datetime import datetime
import re

ROOT = Path.cwd()
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUP_DIR / f"client_page_before_ux_pass14_activity_compact_{timestamp}.tsx"

text = PAGE.read_text(encoding="utf-8")
original = text
backup.write_text(original, encoding="utf-8")

# Limit the rendered activity feed preview to latest 2 items.
text = text.replace(
    ']).map((event) => {',
    ']).slice(0, 2).map((event) => {',
    1
)

# Compact activity event cards.
text = text.replace(
    'padding: 16,\n                      background: "rgba(255, 255, 255, 0.94)"',
    'padding: 12,\n                      background: "rgba(255, 255, 255, 0.94)"'
)

text = text.replace(
    'gap: 14, flexWrap: "wrap", alignItems: "flex-start"',
    'gap: 10, flexWrap: "wrap", alignItems: "flex-start"'
)

text = text.replace(
    'marginTop: 14',
    'marginTop: 10'
)

# Make tags less tall.
text = text.replace(
    'padding: "6px 9px"',
    'padding: "4px 7px"'
)

text = text.replace(
    'fontSize: 11.5',
    'fontSize: 10.8'
)

# Add activity lock marker.
if "client_portal_activity_feed_compact_locked" not in text:
    text = text.replace(
        "// client_portal_bottom_section_rebuild_locked",
        "// client_portal_bottom_section_rebuild_locked\n// client_portal_activity_feed_compact_locked"
    )

if text == original:
    raise RuntimeError("No Pass 14 activity compact changes applied.")

PAGE.write_text(text, encoding="utf-8")

TEST = ROOT / "test_client_portal_ux_pass14_activity_compact.py"
TEST.write_text(r'''
from pathlib import Path

PAGE = Path("frontend/src/app/client/page.tsx")
text = PAGE.read_text(encoding="utf-8")

print("CLIENT_PORTAL_UX_PASS14_ACTIVITY_COMPACT_RESULTS")

checks = {
    "marker": "client_portal_activity_feed_compact_locked" in text,
    "slice_latest_2": "]).slice(0, 2).map((event) => {" in text,
    "compact_padding": "padding: 12" in text,
    "compact_tag_padding": 'padding: "4px 7px"' in text,
}

for key, value in checks.items():
    print(key, value)

assert all(checks.values())

print("CLIENT_PORTAL_UX_PASS14_ACTIVITY_COMPACT_OK")
'''.lstrip(), encoding="utf-8")

print("CLIENT_PORTAL_UX_PASS14_ACTIVITY_COMPACT_INSTALLED")
print(f"Backup: {backup}")
print(f"Updated: {PAGE}")
print(f"Created: {TEST}")