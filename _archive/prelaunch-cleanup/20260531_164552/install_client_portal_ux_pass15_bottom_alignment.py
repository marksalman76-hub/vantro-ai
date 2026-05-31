from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUP_DIR / f"client_page_before_ux_pass15_bottom_alignment_{timestamp}.tsx"

text = PAGE.read_text(encoding="utf-8")
original = text
backup.write_text(original, encoding="utf-8")

# Make lower grid cards align visually.
text = text.replace(
    '<section style={responsiveSecondaryGridStyle}>',
    '<section style={{ ...responsiveSecondaryGridStyle, alignItems: "stretch" }}>',
    1
)

# Apply equal lower-card height to the first two bottom cards by upgrading first two cardStyle usages after secondary section.
marker = '<section style={{ ...responsiveSecondaryGridStyle, alignItems: "stretch" }}>'
idx = text.find(marker)
if idx == -1:
    raise RuntimeError("Bottom secondary grid marker not found")

after = text[idx:]
after = after.replace(
    '<div style={cardStyle}>',
    '<div style={{ ...cardStyle, height: 560, overflow: "hidden" }}>',
    2
)
text = text[:idx] + after

# Make activity inner event list scrollable within fixed panel.
text = text.replace(
    '<div style={{ display: "grid", gap: 18, marginTop: 22 }}>',
    '<div style={{ display: "grid", gap: 12, marginTop: 14, maxHeight: 430, overflowY: "auto", paddingRight: 4 }}>',
    1
)

# Tighten event cards further.
text = text.replace(
    'padding: 12,\n                      background: "rgba(255, 255, 255, 0.94)"',
    'padding: 10,\n                      background: "rgba(255, 255, 255, 0.94)"'
)

# Tighten deliverable panel content.
text = text.replace(
    'marginTop: 18,\n    display: "grid"',
    'marginTop: 12,\n    display: "grid"'
)

# Marker.
if "client_portal_bottom_cards_aligned_locked" not in text:
    text = text.replace(
        "// client_portal_activity_feed_compact_locked",
        "// client_portal_activity_feed_compact_locked\n// client_portal_bottom_cards_aligned_locked"
    )

if text == original:
    raise RuntimeError("No Pass 15 bottom alignment changes applied.")

PAGE.write_text(text, encoding="utf-8")

TEST = ROOT / "test_client_portal_ux_pass15_bottom_alignment.py"
TEST.write_text(r'''
from pathlib import Path

PAGE = Path("frontend/src/app/client/page.tsx")
text = PAGE.read_text(encoding="utf-8")

print("CLIENT_PORTAL_UX_PASS15_BOTTOM_ALIGNMENT_RESULTS")

checks = {
    "marker": "client_portal_bottom_cards_aligned_locked" in text,
    "stretch_grid": 'alignItems: "stretch"' in text,
    "fixed_lower_height": 'height: 560' in text,
    "inner_scroll": 'maxHeight: 430' in text and 'overflowY: "auto"' in text,
}

for key, value in checks.items():
    print(key, value)

assert all(checks.values())

print("CLIENT_PORTAL_UX_PASS15_BOTTOM_ALIGNMENT_OK")
'''.lstrip(), encoding="utf-8")

print("CLIENT_PORTAL_UX_PASS15_BOTTOM_ALIGNMENT_INSTALLED")
print(f"Backup: {backup}")
print(f"Updated: {PAGE}")
print(f"Created: {TEST}")