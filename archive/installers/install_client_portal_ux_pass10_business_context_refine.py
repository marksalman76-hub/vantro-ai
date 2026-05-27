from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUP_DIR / f"client_page_before_ux_pass10_business_context_refine_{timestamp}.tsx"

text = PAGE.read_text(encoding="utf-8")
original = text
backup.write_text(original, encoding="utf-8")

text = text.replace(
    "Store business context for client-specific outputs",
    "Store business context for tailored AI execution"
)

text = text.replace(
    "Add business context once so every active AI agent can produce more accurate deliverables, assets, copy, positioning, and execution recommendations.",
    "Add business context once so every active AI agent can adapt outputs, recommendations, workflows, and execution to the client’s business, market, goals, and operating style."
)

# Make all 8 fields consistent and remove scroll feel.
text = text.replace(
    'gridTemplateColumns: "repeat(8, minmax(130px, 1fr))"',
    'gridTemplateColumns: "repeat(8, minmax(150px, 1fr))"'
)

text = text.replace(
    'rows={2}',
    'rows={3}'
)

text = text.replace(
    'padding: "11px 12px"',
    'padding: "12px 13px"'
)

text = text.replace(
    'fontSize: 12,',
    'fontSize: 12.2,'
)

text = text.replace(
    'lineHeight: 1.35,',
    'lineHeight: 1.42,'
)

if "client_portal_ux_pass10_business_context_refine" not in text:
    text = text.replace(
        "// client_portal_upper_sections_locked_pre_bottom_rebuild",
        "// client_portal_upper_sections_locked_pre_bottom_rebuild\n// client_portal_ux_pass10_business_context_refine"
    )

if text == original:
    raise RuntimeError("No Pass 10 changes applied.")

PAGE.write_text(text, encoding="utf-8")

TEST = ROOT / "test_client_portal_ux_pass10_business_context_refine.py"
TEST.write_text(r'''
from pathlib import Path

PAGE = Path("frontend/src/app/client/page.tsx")
text = PAGE.read_text(encoding="utf-8")

print("CLIENT_PORTAL_UX_PASS10_BUSINESS_CONTEXT_REFINE_RESULTS")

checks = {
    "marker": "client_portal_ux_pass10_business_context_refine" in text,
    "neutral_heading": "Store business context for tailored AI execution" in text,
    "neutral_description": "market, goals, and operating style" in text,
    "wider_grid": 'gridTemplateColumns: "repeat(8, minmax(150px, 1fr))"' in text,
    "rows_3": "rows={3}" in text,
}

for key, value in checks.items():
    print(key, value)

assert all(checks.values())

print("CLIENT_PORTAL_UX_PASS10_BUSINESS_CONTEXT_REFINE_OK")
'''.lstrip(), encoding="utf-8")

print("CLIENT_PORTAL_UX_PASS10_BUSINESS_CONTEXT_REFINE_INSTALLED")
print(f"Backup: {backup}")
print(f"Updated: {PAGE}")
print(f"Created: {TEST}")