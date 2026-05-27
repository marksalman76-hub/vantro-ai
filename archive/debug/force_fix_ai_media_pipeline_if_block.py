from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
file = ROOT / "backend" / "app" / "runtime" / "ai_media_end_to_end_pipeline.py"

backup_dir = ROOT / "backups"
backup_dir.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = backup_dir / f"ai_media_end_to_end_pipeline_before_force_if_block_fix_{timestamp}.py"
backup.write_text(file.read_text(encoding="utf-8"), encoding="utf-8")

text = file.read_text(encoding="utf-8")

bad_block = """    if not quality.get("provider_execution_allowed"):
    creative_director_result = None
        status = "blocked_by_quality_gate"
"""

good_block = """    if not quality.get("provider_execution_allowed"):
        status = "blocked_by_quality_gate"
"""

if bad_block in text:
    text = text.replace(bad_block, good_block)
else:
    text = text.replace("    creative_director_result = None\n        status = \"blocked_by_quality_gate\"\n", "        status = \"blocked_by_quality_gate\"\n")

# Put the default safely immediately before the result uses it.
needle = """    result = {
"""
if "    creative_director_result = None\n    result = {" not in text:
    text = text.replace(needle, "    creative_director_result = None\n\n" + needle, 1)

file.write_text(text, encoding="utf-8")

print("AI_MEDIA_PIPELINE_IF_BLOCK_FORCE_FIXED")
print(f"Backup: {backup}")
print(f"Updated: {file}")