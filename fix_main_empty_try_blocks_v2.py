from pathlib import Path
from datetime import datetime

root = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
path = root / "backend" / "app" / "main.py"

text = path.read_text(encoding="utf-8")
backup_dir = root / "backups" / f"main_before_empty_try_v2_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)
(backup_dir / "main.py").write_text(text, encoding="utf-8")

lines = text.splitlines()
fixed = []
insertions = []

i = 0
while i < len(lines):
    line = lines[i]
    fixed.append(line)

    if line.strip() == "try:":
        indent = len(line) - len(line.lstrip(" "))
        j = i + 1

        while j < len(lines) and lines[j].strip() == "":
            fixed.append(lines[j])
            j += 1

        if j < len(lines):
            next_line = lines[j]
            next_indent = len(next_line) - len(next_line.lstrip(" "))
            if next_line.strip().startswith("except ") and next_indent == indent:
                fixed.append(" " * (indent + 4) + "pass")
                insertions.append(i + 1)

        i = j
        continue

    i += 1

path.write_text("\n".join(fixed) + "\n", encoding="utf-8")

print("MAIN_EMPTY_TRY_BLOCKS_V2_FIXED")
print("Backup:", backup_dir)
print("Inserted pass after try lines:", insertions)