from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
TARGET = ROOT / "backend" / "app" / "runtime" / "action_adapter_execution_layer.py"

BACKUP = ROOT / "backups" / f"media_plan_return_packet_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
BACKUP.mkdir(parents=True, exist_ok=True)
shutil.copy2(TARGET, BACKUP / "action_adapter_execution_layer.py")

s = TARGET.read_text(encoding="utf-8")

# Ensure media_plan exists by default.
if "media_plan = None" not in s:
    s = s.replace(
        "real_external_result = None",
        "real_external_result = None\n    media_plan = None"
    )

# Ensure the UGC branch assigns the function-scope variable.
s = s.replace(
    '        media_plan = create_media_generation_plan(',
    '        media_plan = create_media_generation_plan('
)

# Add media_generation_plan to the final returned packet near actions_performed.
if '"media_generation_plan": media_plan,' not in s:
    s = s.replace(
        '"actions_performed": actions,',
        '"actions_performed": actions,\n        "media_generation_plan": media_plan,'
    )

TARGET.write_text(s, encoding="utf-8")

print("MEDIA_PLAN_RETURN_PACKET_FIXED")
print("Backup:", BACKUP)