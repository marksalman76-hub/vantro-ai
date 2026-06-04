from pathlib import Path
from datetime import datetime

root = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
path = root / "backend" / "app" / "main.py"

backup_dir = root / "backups" / f"main_before_import_syntax_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)
backup = backup_dir / "main.py"
backup.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")

lines = path.read_text(encoding="utf-8").splitlines()

fixed = []
balance = 0
removed = []

for idx, line in enumerate(lines, start=1):
    stripped = line.strip()

    # Remove stray unmatched closing parenthesis in the top import/bootstrap area only.
    if idx <= 160 and stripped == ")" and balance <= 0:
        removed.append(idx)
        continue

    balance += line.count("(") - line.count(")")
    fixed.append(line)

path.write_text("\n".join(fixed) + "\n", encoding="utf-8")

print("MAIN_IMPORT_SYNTAX_FIX_APPLIED")
print("Backup:", backup)
print("Removed stray top-level parenthesis lines:", removed)