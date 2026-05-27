from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUP_DIR / f"client_page_before_ux_pass16_activity_premium_polish_{timestamp}.tsx"

text = PAGE.read_text(encoding="utf-8")
original = text
backup.write_text(original, encoding="utf-8")

# Compact activity card padding.
text = text.replace(
    'padding: 10,\n                      background: "rgba(255, 255, 255, 0.94)"',
    'padding: "10px 12px",\n                      background: "rgba(255, 255, 255, 0.96)"'
)

# Reduce excessive card spacing.
text = text.replace(
    'gap: 12, marginTop: 14, maxHeight: 430, overflowY: "auto", paddingRight: 4',
    'gap: 10, marginTop: 10, maxHeight: 430, overflowY: "auto", paddingRight: 4'
)

# Reduce timestamp prominence.
text = text.replace(
    'fontSize: 12,\n                          color: "#64748b",',
    'fontSize: 10.5,\n                          color: "#94a3b8",'
)

# Tighten activity title spacing.
text = text.replace(
    'marginTop: 8',
    'marginTop: 4'
)

# Make agent label secondary.
text = text.replace(
    'fontSize: 13.5,\n                          fontWeight: 700,',
    'fontSize: 12,\n                          fontWeight: 600,'
)

# Compress pills.
text = text.replace(
    'padding: "4px 7px"',
    'padding: "3px 6px"'
)

text = text.replace(
    'fontSize: 10.8',
    'fontSize: 10'
)

# Reduce whitespace below descriptions.
text = text.replace(
    'marginBottom: 14',
    'marginBottom: 8'
)

# Add premium subtle divider feel.
text = text.replace(
    'border: "1px solid rgba(34, 197, 94, 0.24)"',
    'border: "1px solid rgba(15, 23, 42, 0.08)"'
)

# Slightly soften background.
text = text.replace(
    'background: "rgba(255, 255, 255, 0.96)"',
    'background: "rgba(248, 250, 252, 0.92)"'
)

# Marker.
if "client_portal_activity_premium_polish_locked" not in text:
    text = text.replace(
        "// client_portal_bottom_cards_aligned_locked",
        "// client_portal_bottom_cards_aligned_locked\n// client_portal_activity_premium_polish_locked"
    )

if text == original:
    raise RuntimeError("No Pass 16 activity polish changes applied.")

PAGE.write_text(text, encoding="utf-8")

TEST = ROOT / "test_client_portal_ux_pass16_activity_premium_polish.py"
TEST.write_text(r'''
from pathlib import Path

PAGE = Path("frontend/src/app/client/page.tsx")
text = PAGE.read_text(encoding="utf-8")

print("CLIENT_PORTAL_UX_PASS16_ACTIVITY_PREMIUM_POLISH_RESULTS")

checks = {
    "marker": "client_portal_activity_premium_polish_locked" in text,
    "compact_padding": 'padding: "10px 12px"' in text,
    "compact_pills": 'padding: "3px 6px"' in text,
    "softened_borders": 'rgba(15, 23, 42, 0.08)' in text,
    "compact_timestamp": 'fontSize: 10.5' in text,
}

for key, value in checks.items():
    print(key, value)

assert all(checks.values())

print("CLIENT_PORTAL_UX_PASS16_ACTIVITY_PREMIUM_POLISH_OK")
'''.lstrip(), encoding="utf-8")

print("CLIENT_PORTAL_UX_PASS16_ACTIVITY_PREMIUM_POLISH_INSTALLED")
print(f"Backup: {backup}")
print(f"Updated: {PAGE}")
print(f"Created: {TEST}")