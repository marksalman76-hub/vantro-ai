from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

src = PAGE.read_text(encoding="utf-8")
backup = BACKUPS / f"client_page_before_tighten_lower_cards_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
backup.write_text(src, encoding="utf-8")

replacements = [
    ('<div style={{ ...cardStyle, minHeight: 430, overflow: "hidden" }}>\n            <StepHeader number="05" title="Activity" />',
     '<div style={{ ...cardStyle, minHeight: 355, overflow: "hidden" }}>\n            <StepHeader number="05" title="Activity" />'),

    ('<div style={{ ...cardStyle, height: 560, overflow: "hidden" }}>\n            <div style={{ display: "flex", justifyContent: "space-between", gap: 16, flexWrap: "wrap" }}>',
     '<div style={{ ...cardStyle, minHeight: 355, overflow: "hidden" }}>\n            <div style={{ display: "flex", justifyContent: "space-between", gap: 16, flexWrap: "wrap" }}>'),

    ('minHeight: 150,\n                  borderRadius: 16,',
     'minHeight: 118,\n                  borderRadius: 16,'),

    ('padding: 16,\n                      background: "linear-gradient(180deg,#ffffff 0%,var(--color-bg-light) 100%)",',
     'padding: 12,\n                      background: "linear-gradient(180deg,#ffffff 0%,var(--color-bg-light) 100%)",'),
]

changed = 0
for old, new in replacements:
    if old in src:
        src = src.replace(old, new, 1)
        changed += 1

if changed < 2:
    raise SystemExit(f"ERROR: Only {changed} replacements applied. No safe write completed.")

PAGE.write_text(src, encoding="utf-8")

print("LOWER_CARDS_HEIGHT_TIGHTENED")
print(f"Backup: {backup}")
print("Replacements applied:", changed)
print("Activity tightened:", 'minHeight: 355, overflow: "hidden" }}>\n            <StepHeader number="05" title="Activity"' in src)
print("Output viewer tightened:", 'minHeight: 355, overflow: "hidden" }}>\n            <div style={{ display: "flex", justifyContent: "space-between"' in src)
print("Enterprise modal preserved:", "showEnterpriseCatalogueModal" in src)
print("Right execution column locked:", src.count("Live execution flow") == 1 and src.count("Business profile applied") == 1 and src.count("Governed execution, every time.") == 1)
print("Old mutations:", src.count("applyHorizontalExecutionLayout") + src.count("applyPremiumExecutionSectionLayout"))