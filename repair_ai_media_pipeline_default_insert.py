from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
file = ROOT / "backend" / "app" / "runtime" / "ai_media_end_to_end_pipeline.py"

backup_dir = ROOT / "backups"
backup_dir.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = backup_dir / f"ai_media_end_to_end_pipeline_before_default_insert_repair_{timestamp}.py"
backup.write_text(file.read_text(encoding="utf-8"), encoding="utf-8")

lines = file.read_text(encoding="utf-8").splitlines()

# Remove every previous bad insertion.
lines = [line for line in lines if line.strip() != "creative_director_result = None"]

# Find the function and the real end of its multi-line signature.
def_index = None
for i, line in enumerate(lines):
    if line.startswith("def run_ai_media_end_to_end_pipeline("):
        def_index = i
        break

if def_index is None:
    raise SystemExit("run_ai_media_end_to_end_pipeline function not found")

signature_end = None
for i in range(def_index, len(lines)):
    if lines[i].strip().endswith("):"):
        signature_end = i
        break

if signature_end is None:
    raise SystemExit("function signature end not found")

# Insert inside the function body, after the full signature.
insert_at = signature_end + 1
lines.insert(insert_at, "    creative_director_result = None")

file.write_text("\n".join(lines) + "\n", encoding="utf-8")

print("AI_MEDIA_PIPELINE_DEFAULT_INSERT_REPAIRED")
print(f"Backup: {backup}")
print(f"Updated: {file}")