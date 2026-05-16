from pathlib import Path
from datetime import datetime
import py_compile

ROOT = Path.cwd()
BACKEND = ROOT / "backend" / "app"
BACKUPS = ROOT / "backups"

main_file = BACKEND / "main.py"

if not main_file.exists():
    raise FileNotFoundError("backend/app/main.py not found")

BACKUPS.mkdir(parents=True, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

text = main_file.read_text(encoding="utf-8")

backup = BACKUPS / f"main_before_step207_cleanup_{timestamp}.py"
backup.write_text(text, encoding="utf-8")

marker = "# Step 206 billing execution guard for client /run-agent requests"

occurrences = []

search_pos = 0
while True:
    idx = text.find(marker, search_pos)
    if idx == -1:
        break
    occurrences.append(idx)
    search_pos = idx + 1

if len(occurrences) <= 1:
    print("No duplicate Step 206 middleware blocks found.")
else:
    # Keep ONLY the last occurrence (the safe V4 version).
    blocks_removed = 0

    while len(occurrences) > 1:
        start = occurrences[0]

        decorator_start = text.rfind("@app.middleware", 0, start)
        if decorator_start == -1:
            decorator_start = start

        next_occurrence = occurrences[1]

        text = (
            text[:decorator_start].rstrip()
            + "\n\n"
            + text[next_occurrence:].lstrip()
        )

        blocks_removed += 1

        occurrences = []
        search_pos = 0
        while True:
            idx = text.find(marker, search_pos)
            if idx == -1:
                break
            occurrences.append(idx)
            search_pos = idx + 1

    print(f"Removed duplicate middleware blocks: {blocks_removed}")

main_file.write_text(text, encoding="utf-8")

py_compile.compile(str(main_file), doraise=True)

print("STEP_207_DUPLICATE_BILLING_GUARD_CLEANUP_OK")
print(f"Backup: {backup}")
print(f"Updated: {main_file}")