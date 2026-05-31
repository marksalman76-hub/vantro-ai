from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
pipeline_file = ROOT / "backend" / "app" / "runtime" / "ai_media_end_to_end_pipeline.py"

if not pipeline_file.exists():
    raise SystemExit("ai_media_end_to_end_pipeline.py not found")

backups = ROOT / "backups"
backups.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_file = backups / f"ai_media_end_to_end_pipeline_before_future_import_fix_{timestamp}.py"
backup_file.write_text(pipeline_file.read_text(encoding="utf-8"), encoding="utf-8")

content = pipeline_file.read_text(encoding="utf-8")

creative_import = """from backend.app.runtime.ai_media_creative_director import (
    run_shared_ai_media_creative_director,
    is_ai_media_relevant_agent,
)
"""

content = content.replace(creative_import + "\n", "")
content = content.replace(creative_import, "")

future_line = "from __future__ import annotations"

if future_line not in content:
    content = future_line + "\n\n" + content.lstrip()

content = content.replace(
    future_line,
    future_line + "\n\n" + creative_import.strip(),
    1,
)

pipeline_file.write_text(content, encoding="utf-8")

print("AI_MEDIA_PIPELINE_FUTURE_IMPORT_ORDER_FIXED")
print(f"Backup: {backup_file}")
print(f"Updated: {pipeline_file}")