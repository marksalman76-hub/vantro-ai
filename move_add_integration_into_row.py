from pathlib import Path
from datetime import datetime

path = Path("frontend/src/app/client/page.tsx")
text = path.read_text(encoding="utf-8")

backup_dir = Path("backups")
backup_dir.mkdir(exist_ok=True)
backup = backup_dir / f"client_page_before_move_add_integration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
backup.write_text(text, encoding="utf-8")

text = text.replace(
    'minWidth: 155,',
    'minWidth: 145,'
)

text = text.replace(
    'padding: "10px 12px",',
    'padding: "8px 10px",'
)

text = text.replace(
    'gridTemplateColumns: "150px 1fr",',
    'gridTemplateColumns: "145px 1fr 150px",'
)

text = text.replace(
    'gridTemplateColumns: "145px 1fr",',
    'gridTemplateColumns: "145px 1fr 150px",'
)

path.write_text(text, encoding="utf-8")

print("ADD_INTEGRATION_ROW_MICRO_FIX_APPLIED")
print(f"Backup: {backup}")