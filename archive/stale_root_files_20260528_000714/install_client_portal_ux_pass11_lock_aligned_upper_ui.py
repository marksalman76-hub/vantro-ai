from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUP_DIR / f"client_page_before_ux_pass11_lock_aligned_upper_ui_{timestamp}.tsx"

text = PAGE.read_text(encoding="utf-8")
original = text
backup.write_text(original, encoding="utf-8")

text = text.replace(
    "Store business context for tailored AI execution",
    "Business context for tailored AI execution"
)

if "client_portal_aligned_upper_ui_locked" not in text:
    text = text.replace(
        "// client_portal_ux_pass10_business_context_refine",
        "// client_portal_ux_pass10_business_context_refine\n// client_portal_aligned_upper_ui_locked"
    )

if text == original:
    raise RuntimeError("No Pass 11 changes applied.")

PAGE.write_text(text, encoding="utf-8")

TEST = ROOT / "test_client_portal_ux_pass11_lock_aligned_upper_ui.py"
TEST.write_text(r'''
from pathlib import Path

PAGE = Path("frontend/src/app/client/page.tsx")
text = PAGE.read_text(encoding="utf-8")

print("CLIENT_PORTAL_UX_PASS11_LOCK_ALIGNED_UPPER_UI_RESULTS")

checks = {
    "lock_marker": "client_portal_aligned_upper_ui_locked" in text,
    "new_heading": "Business context for tailored AI execution" in text,
    "old_heading_removed": "Store business context for tailored AI execution" not in text,
}

for key, value in checks.items():
    print(key, value)

assert all(checks.values())

print("CLIENT_PORTAL_UX_PASS11_LOCK_ALIGNED_UPPER_UI_OK")
'''.lstrip(), encoding="utf-8")

print("CLIENT_PORTAL_UX_PASS11_LOCK_ALIGNED_UPPER_UI_INSTALLED")
print(f"Backup: {backup}")
print(f"Updated: {PAGE}")
print(f"Created: {TEST}")