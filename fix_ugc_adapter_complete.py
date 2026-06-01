from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
TARGET = ROOT / "backend" / "app" / "runtime" / "action_adapter_execution_layer.py"

BACKUP = ROOT / "backups" / f"ugc_adapter_complete_fix_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
BACKUP.mkdir(parents=True, exist_ok=True)
shutil.copy2(TARGET, BACKUP / "action_adapter_execution_layer.py")

s = TARGET.read_text(encoding="utf-8")

# 1. Keep future import first.
s = s.replace("from __future__ import annotations\n", "")
s = "from __future__ import annotations\n" + s.lstrip()

# 2. Ensure UGC classification.
needle = 'def classify_action_adapter(packet: Dict[str, Any]) -> str:\n    text = _text(packet)\n    connected = set(packet.get("connected_integrations") or [])'
replacement = '''def classify_action_adapter(packet: Dict[str, Any]) -> str:
    text = _text(packet)
    connected = set(packet.get("connected_integrations") or [])
    assigned_agent = str(packet.get("assigned_agent") or packet.get("recommended_agent") or "").strip()

    if assigned_agent == "ugc_creative_agent" or "ugc" in text or "shot-by-shot" in text or "creator casting" in text or "video concept" in text:
        return "ugc_creative_deliverable_adapter"'''
if needle in s and "return \"ugc_creative_deliverable_adapter\"" not in s:
    s = s.replace(needle, replacement)

# 3. Add UGC adapter execution branch before CRM branch.
branch = r'''
    elif adapter == "ugc_creative_deliverable_adapter":
        actions = [
            {
                "type": "ugc_campaign_deliverable_created",
                "status": "created",
                "target_system": "creative_deliverable_runtime",
                "record_id": f"ugc_{uuid4().hex[:10]}",
                "deliverable_sections": [
                    "5 UGC concepts",
                    "shot-by-shot breakdowns",
                    "creator casting",
                    "wardrobe direction",
                    "lighting direction",
                    "camera movement",
                    "retention hooks",
                    "CTA structure",
                    "paid ad variations",
                ],
            }
        ]
        output = _generate_ugc_creative_deliverable(str(packet.get("user_requested_task") or action_text))
'''

insert_before = '    elif adapter == "crm_task_creation_adapter":'
if 'elif adapter == "ugc_creative_deliverable_adapter":' not in s:
    if insert_before not in s:
        raise SystemExit("Could not find adapter branch insertion point.")
    s = s.replace(insert_before, branch + "\n" + insert_before)

TARGET.write_text(s, encoding="utf-8")

print("UGC_ADAPTER_COMPLETE_FIX_APPLIED")
print("Backup:", BACKUP)