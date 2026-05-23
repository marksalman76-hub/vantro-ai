from pathlib import Path
from datetime import datetime

path = Path("frontend/src/app/client/page.tsx")
text = path.read_text(encoding="utf-8")

backup_dir = Path("backups")
backup_dir.mkdir(exist_ok=True)
backup = backup_dir / f"client_page_before_business_profile_grid_alignment_final_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
backup.write_text(text, encoding="utf-8")

old_grid = 'gridTemplateColumns: "repeat(5, minmax(0, 1fr))"'
new_grid = 'gridTemplateColumns: "repeat(4, minmax(0, 1fr))"'

old_span = 'gridColumn: size === "wide" ? "span 2" : "span 1",'
new_span = 'gridColumn: label === "Key differentiators" ? "span 3" : "span 1",'

if old_grid not in text:
    raise SystemExit("Could not find 5-column business profile grid marker.")

if old_span not in text:
    raise SystemExit("Could not find wide-card gridColumn marker.")

text = text.replace(old_grid, new_grid, 1)
text = text.replace(old_span, new_span, 1)

path.write_text(text, encoding="utf-8")

print("BUSINESS_PROFILE_GRID_ALIGNMENT_FINAL_FIXED")
print(f"Backup: {backup}")