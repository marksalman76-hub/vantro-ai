from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
file = ROOT / "backend" / "app" / "runtime" / "ai_media_end_to_end_pipeline.py"

backup_dir = ROOT / "backups"
backup_dir.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = backup_dir / f"ai_media_end_to_end_pipeline_before_bad_line_242_fix_{timestamp}.py"
backup.write_text(file.read_text(encoding="utf-8"), encoding="utf-8")

lines = file.read_text(encoding="utf-8").splitlines()

fixed = []
removed = 0

for line in lines:
    if line.strip() == "creative_director_result = None":
        removed += 1
        continue
    fixed.append(line)

# Ensure default is inserted correctly after full function signature.
for i, line in enumerate(fixed):
    if line.startswith("def run_ai_media_end_to_end_pipeline("):
        for j in range(i, len(fixed)):
            if fixed[j].strip().endswith("):"):
                if fixed[j + 1].strip() != "creative_director_result = None":
                    fixed.insert(j + 1, "    creative_director_result = None")
                break
        break

file.write_text("\n".join(fixed) + "\n", encoding="utf-8")

print("PIPELINE_BAD_CREATIVE_DIRECTOR_LINE_FIXED")
print(f"Removed: {removed}")
print(f"Backup: {backup}")
print(f"Updated: {file}")