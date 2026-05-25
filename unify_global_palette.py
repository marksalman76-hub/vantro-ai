from pathlib import Path
from datetime import datetime

root = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")

targets = [
    root / "frontend/src/app/activate/page.tsx",
    root / "frontend/src/app/client/billing/cancel/page.tsx",
    root / "frontend/src/app/client/billing/cancelled/page.tsx",
    root / "frontend/src/app/client/billing/success/page.tsx",
]

backup_dir = root / "backups"
backup_dir.mkdir(exist_ok=True)

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

for file in targets:
    original = file.read_text(encoding="utf-8")

    backup = backup_dir / f"{file.stem}_before_global_palette_{stamp}.tsx"
    backup.write_text(original, encoding="utf-8")

    updated = original

    replacements = {
        '#f8fafc': '#e2e8f0',
        '#101828': '#f8fafc',
        'background: "#fff"': 'background: "rgba(15,23,42,.92)"',
        'background:"#fff"': 'background:"rgba(15,23,42,.92)"',
        'background: "#ffffff"': 'background: "rgba(15,23,42,.92)"',
        'background:"#ffffff"': 'background:"rgba(15,23,42,.92)"',
        'background: "#020617"': 'background: "linear-gradient(135deg, #050816 0%, #0b1020 55%, #050816 100%)"',
        'background:"#020617"': 'background:"linear-gradient(135deg, #050816 0%, #0b1020 55%, #050816 100%)"',
        '#2563eb': '#8b5cf6',
        '#16a34a': '#8b5cf6',
        '#f59e0b': '#a78bfa',
    }

    for old, new in replacements.items():
        updated = updated.replace(old, new)

    file.write_text(updated, encoding="utf-8")

print("GLOBAL_PALETTE_UNIFIED")
print("Updated:")
for t in targets:
    print("-", t)

print("Backup folder:", backup_dir)