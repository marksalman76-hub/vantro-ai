from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
text = PAGE.read_text(encoding="utf-8")

backup = BACKUPS / f"client_page_before_step284_premium_restraint_{timestamp}.tsx"
backup.write_text(text, encoding="utf-8")

replacements = [
    ('padding: "34px 40px 72px"', 'padding: "28px 40px 64px"'),
    ('fontSize: 58,', 'fontSize: 50,'),
    ('letterSpacing: -3.2,', 'letterSpacing: -2.4,'),
    ('fontWeight: 800,', 'fontWeight: 760,'),
    ('marginTop: 26,', 'marginTop: 18,'),
    ('fontSize: 18,', 'fontSize: 16,'),
    ('lineHeight: 1.55,', 'lineHeight: 1.5,'),
    ('marginBottom: 34,', 'marginBottom: 26,'),
    ('fontSize: 24,', 'fontSize: 21,'),
    ('fontSize: 42,', 'fontSize: 34,'),
    ('letterSpacing: -1.8,', 'letterSpacing: -1.2,'),
    ('padding: 34,', 'padding: 30,'),
    ('borderRadius: 34,', 'borderRadius: 30,'),
    ('background: "rgba(255,255,255,.7)"', 'background: "rgba(255,255,255,.82)"'),
    ('boxShadow: "0 14px 36px rgba(15,23,42,.045)"', 'boxShadow: "0 10px 28px rgba(15,23,42,.04)"'),
    ('gridTemplateColumns: "repeat(5,minmax(0,1fr))"', 'gridTemplateColumns: "repeat(auto-fit,minmax(220px,1fr))"'),
    ('gap: 18,', 'gap: 14,'),
    ('fontSize: 15,', 'fontSize: 14,'),
    ('padding: "17px 18px"', 'padding: "15px 16px"'),
    ('borderRadius: 18,', 'borderRadius: 16,'),
    ('gridTemplateColumns: "420px 1fr"', 'gridTemplateColumns: "minmax(390px,.9fr) minmax(520px,1.1fr)"'),
    ('gap: 34,', 'gap: 24,'),
    ('padding: 38,', 'padding: 30,'),
    ('minHeight: 760,', 'minHeight: 620,'),
    ('fontSize: 46,', 'fontSize: 36,'),
    ('letterSpacing: -2,', 'letterSpacing: -1.4,'),
    ('minHeight: 560,', 'minHeight: 430,'),
    ('fontSize: 34,', 'fontSize: 26,'),
    ('fontSize: 19,', 'fontSize: 16,'),
]

for old, new in replacements:
    text = text.replace(old, new)

PAGE.write_text(text, encoding="utf-8")

print("STEP_284_PREMIUM_RESTRAINT_REFINEMENT_INSTALLED")
print(f"Backup: {backup}")
print("STEP_284_OK")