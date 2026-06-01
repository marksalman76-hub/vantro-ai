from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
TARGET = ROOT / "backend" / "app" / "runtime" / "action_adapter_execution_layer.py"

BACKUP = ROOT / "backups" / f"wire_media_plan_into_ugc_adapter_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
BACKUP.mkdir(parents=True, exist_ok=True)
shutil.copy2(TARGET, BACKUP / "action_adapter_execution_layer.py")

s = TARGET.read_text(encoding="utf-8")

if "from backend.app.runtime.media_generation_orchestrator import create_media_generation_plan" not in s:
    s = s.replace(
        "from backend.app.runtime.react_website_generation_runtime import generate_react_website_project",
        "from backend.app.runtime.react_website_generation_runtime import generate_react_website_project\nfrom backend.app.runtime.media_generation_orchestrator import create_media_generation_plan"
    )

s = s.replace(
'''        output = _generate_ugc_creative_deliverable(str(packet.get("user_requested_task") or action_text))''',
'''        media_plan = create_media_generation_plan(
            "ugc_creative_agent",
            str(packet.get("user_requested_task") or action_text),
            tenant_id=tenant_id,
        )
        output = _generate_ugc_creative_deliverable(str(packet.get("user_requested_task") or action_text))'''
)

s = s.replace(
'''"actions_performed": actions,''',
'''"actions_performed": actions,
        "media_generation_plan": media_plan if adapter == "ugc_creative_deliverable_adapter" else None,'''
)

TARGET.write_text(s, encoding="utf-8")

print("MEDIA_PLAN_WIRED_INTO_UGC_ADAPTER")
print("Backup:", BACKUP)