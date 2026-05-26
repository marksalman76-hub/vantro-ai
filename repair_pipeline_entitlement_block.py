from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
file = ROOT / "backend" / "app" / "runtime" / "ai_media_end_to_end_pipeline.py"

backup_dir = ROOT / "backups"
backup_dir.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = backup_dir / f"ai_media_end_to_end_pipeline_before_entitlement_block_repair_{timestamp}.py"
backup.write_text(file.read_text(encoding="utf-8"), encoding="utf-8")

text = file.read_text(encoding="utf-8")

start_marker = "    if not entitlement_active:\n"
end_marker = "    base_payload = {\n"

start = text.find(start_marker)
end = text.find(end_marker, start)

if start == -1 or end == -1:
    raise SystemExit("Could not find entitlement block markers")

replacement = """    creative_director_result = None

    if not entitlement_active:
        result = {
            "run_id": run_id,
            "status": "blocked",
            "reason": "entitlement_inactive",
            "execution_allowed": False,
            "governance_preserved": True,
            "layout_changes": False,
            "created_at": _now(),
        }
        _append_jsonl(PIPELINE_RUNS, result)
        return result

"""

text = text[:start] + replacement + text[end:]

file.write_text(text, encoding="utf-8")

print("AI_MEDIA_PIPELINE_ENTITLEMENT_BLOCK_REPAIRED")
print(f"Backup: {backup}")
print(f"Updated: {file}")