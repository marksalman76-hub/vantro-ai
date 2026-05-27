from pathlib import Path
from datetime import datetime
import re

ROOT = Path.cwd()

PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

backup = BACKUPS / f"client_page_before_ux_pass13_bottom_section_rebuild_{timestamp}.tsx"

text = PAGE.read_text(encoding="utf-8")
original = text

backup.write_text(original, encoding="utf-8")

# -------------------------------------------------------------------
# Compact execution pipeline bubbles
# -------------------------------------------------------------------

text = text.replace(
    'height: 138,',
    'height: 92,'
)

text = text.replace(
    'padding: "24px 22px"',
    'padding: "18px 18px"'
)

text = text.replace(
    'padding: "22px 22px"',
    'padding: "16px 16px"'
)

# -------------------------------------------------------------------
# Compress activity cards
# -------------------------------------------------------------------

text = text.replace(
    'borderRadius: 26,',
    'borderRadius: 20,'
)

text = text.replace(
    'padding: "22px 22px 20px"',
    'padding: "16px 16px 14px"'
)

# -------------------------------------------------------------------
# Tighten deliverable viewer
# -------------------------------------------------------------------

text = text.replace(
    'padding: 22,',
    'padding: 16,'
)

text = text.replace(
    'gap: 20,',
    'gap: 14,'
)

text = text.replace(
    'borderRadius: 20,',
    'borderRadius: 18,'
)

# -------------------------------------------------------------------
# Reduce oversized modal
# -------------------------------------------------------------------

text = text.replace(
    'borderRadius: 28,',
    'borderRadius: 22,'
)

text = text.replace(
    'padding: "clamp(20px,2.4vw,28px)"',
    'padding: "clamp(16px,2vw,22px)"'
)

# -------------------------------------------------------------------
# Tighten action buttons
# -------------------------------------------------------------------

text = text.replace(
    'padding: "12px 18px"',
    'padding: "10px 14px"'
)

text = text.replace(
    'padding: "10px 13px"',
    'padding: "8px 11px"'
)

# -------------------------------------------------------------------
# Reduce duplicated action controls
# -------------------------------------------------------------------

text = text.replace(
    'Expand preview',
    'Preview'
)

text = text.replace(
    'View full deliverable',
    'Open deliverable'
)

# -------------------------------------------------------------------
# Compress media preview zone
# -------------------------------------------------------------------

text = text.replace(
    'minHeight: 280,',
    'minHeight: 190,'
)

text = text.replace(
    'padding: "28px 24px"',
    'padding: "18px 16px"'
)

# -------------------------------------------------------------------
# Reduce oversized typography
# -------------------------------------------------------------------

text = text.replace(
    'fontSize: "clamp(22px,2.4vw,28px)"',
    'fontSize: "clamp(20px,2vw,24px)"'
)

text = text.replace(
    'fontSize: 12.2,',
    'fontSize: 11.8,'
)

# -------------------------------------------------------------------
# Lock marker
# -------------------------------------------------------------------

if "client_portal_bottom_section_rebuild_locked" not in text:
    text = text.replace(
        "// client_portal_business_context_subscription_governance",
        "// client_portal_business_context_subscription_governance\n// client_portal_bottom_section_rebuild_locked"
    )

if text == original:
    raise RuntimeError("No Pass 13 changes applied.")

PAGE.write_text(text, encoding="utf-8")

TEST = ROOT / "test_client_portal_ux_pass13_bottom_section_rebuild.py"

TEST.write_text(r'''
from pathlib import Path

PAGE = Path("frontend/src/app/client/page.tsx")

text = PAGE.read_text(encoding="utf-8")

print("CLIENT_PORTAL_UX_PASS13_BOTTOM_SECTION_REBUILD_RESULTS")

checks = {
    "marker": "client_portal_bottom_section_rebuild_locked" in text,
    "preview_button": "Preview" in text,
    "open_deliverable_button": "Open deliverable" in text,
    "compressed_padding": 'padding: "10px 14px"' in text,
    "compressed_modal_radius": 'borderRadius: 22' in text,
}

for key, value in checks.items():
    print(key, value)

assert all(checks.values())

print("CLIENT_PORTAL_UX_PASS13_BOTTOM_SECTION_REBUILD_OK")
'''.lstrip(), encoding="utf-8")

print("CLIENT_PORTAL_UX_PASS13_BOTTOM_SECTION_REBUILD_INSTALLED")
print(f"Backup: {backup}")
print(f"Updated: {PAGE}")
print(f"Created: {TEST}")