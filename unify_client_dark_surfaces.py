from pathlib import Path
from datetime import datetime
import shutil

TARGET = Path("frontend/src/app/client/page.tsx")

content = TARGET.read_text(encoding="utf-8")

backup_dir = Path("backups")
backup_dir.mkdir(exist_ok=True)

backup_file = backup_dir / f"client_page_before_dark_surface_unify_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
shutil.copy2(TARGET, backup_file)

replacements = [
    (': "#fff"', ': "rgba(12,24,49,.92)"'),
    (': "#ffffff"', ': "rgba(12,24,49,.92)"'),
    (': "#f8fafc"', ': "rgba(15,23,42,.92)"'),

    ('background: "#fff"', 'background: "rgba(12,24,49,.92)"'),
    ('background:"#fff"', 'background:"rgba(12,24,49,.92)"'),

    ('background: "#ffffff"', 'background: "rgba(12,24,49,.92)"'),
    ('background:"#ffffff"', 'background:"rgba(12,24,49,.92)"'),

    ('background: "#f8fafc"', 'background: "rgba(15,23,42,.92)"'),
    ('background:"#f8fafc"', 'background:"rgba(15,23,42,.92)"'),

    (
        'linear-gradient(135deg, rgba(239, 246, 255, 0.86), rgba(255, 255, 255, 0.96))',
        'linear-gradient(135deg, rgba(79,70,229,.24), rgba(15,23,42,.96))'
    ),

    (
        'linear-gradient(180deg,#ffffff 0%,#f8fafc 100%)',
        'linear-gradient(180deg, rgba(15,23,42,.96), rgba(8,18,40,.98))'
    ),

    (
        'linear-gradient(180deg,#ffffff 0%,var(--color-bg-light) 100%)',
        'linear-gradient(180deg, rgba(15,23,42,.96), rgba(8,18,40,.98))'
    ),
]

for old, new in replacements:
    content = content.replace(old, new)

TARGET.write_text(content, encoding="utf-8")

print("CLIENT_DARK_SURFACES_UNIFIED")
print("Backup:", backup_file)