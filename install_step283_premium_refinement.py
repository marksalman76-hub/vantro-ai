from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

text = PAGE.read_text(encoding="utf-8")

backup = BACKUPS / f"client_page_before_step283_apply_{timestamp}.tsx"
backup.write_text(text, encoding="utf-8")

replacements = [
    (
        'padding: "56px 40px 80px"',
        'padding: "34px 40px 72px"',
    ),
    (
        'marginBottom: 44,',
        'marginBottom: 28,',
    ),
    (
        'fontSize: 66,',
        'fontSize: 58,',
    ),
    (
        'lineHeight: 1.7,',
        'lineHeight: 1.55,',
    ),
    (
        'fontSize: 20,',
        'fontSize: 18,',
    ),
    (
        'marginBottom: 50,',
        'marginBottom: 34,',
    ),
    (
        'padding: 38,',
        'padding: 34,',
    ),
    (
        'borderRadius: 38,',
        'borderRadius: 34,',
    ),
    (
        'boxShadow: "0 20px 50px rgba(15,23,42,.05)"',
        'boxShadow: "0 14px 36px rgba(15,23,42,.045)"',
    ),
    (
        'border: "1px solid #e2e8f0"',
        'border: "1px solid rgba(226,232,240,.7)"',
    ),
    (
        'background: "rgba(255,255,255,.9)"',
        'background: "rgba(255,255,255,.82)"',
    ),
    (
        'padding: "18px 18px"',
        'padding: "17px 18px"',
    ),
    (
        'fontSize: 15,',
        'fontSize: 14.5,',
    ),
    (
        'borderRadius: 20,',
        'borderRadius: 18,',
    ),
    (
        'background: active ? "#2563eb" : "white"',
        'background: active ? "#2563eb" : "rgba(255,255,255,.72)"',
    ),
    (
        'boxShadow: active\n                        ? "0 12px 30px rgba(37,99,235,.22)"\n                        : "0 4px 14px rgba(15,23,42,.04)"',
        'boxShadow: active\n                        ? "0 10px 24px rgba(37,99,235,.18)"\n                        : "0 2px 10px rgba(15,23,42,.03)"',
    ),
    (
        'padding: "20px 22px"',
        'padding: "18px 22px"',
    ),
    (
        'fontSize: 17,',
        'fontSize: 16,',
    ),
    (
        'boxShadow: "0 18px 40px rgba(37,99,235,.22)"',
        'boxShadow: "0 12px 28px rgba(37,99,235,.18)"',
    ),
]

for old, new in replacements:
    text = text.replace(old, new)

PAGE.write_text(text, encoding="utf-8")

print("STEP_283_PREMIUM_REFINEMENT_INSTALLED")
print(f"Backup: {backup}")
print("STEP_283_OK")