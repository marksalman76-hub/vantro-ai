from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
TARGET = ROOT / "backend" / "app" / "runtime" / "action_adapter_execution_layer.py"

BACKUP = ROOT / "backups" / f"force_ugc_media_plan_return_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
BACKUP.mkdir(parents=True, exist_ok=True)
shutil.copy2(TARGET, BACKUP / "action_adapter_execution_layer.py")

s = TARGET.read_text(encoding="utf-8")

if "from backend.app.runtime.media_generation_orchestrator import create_media_generation_plan" not in s:
    s = s.replace(
        "from backend.app.runtime.react_website_generation_runtime import generate_react_website_project",
        "from backend.app.runtime.react_website_generation_runtime import generate_react_website_project\nfrom backend.app.runtime.media_generation_orchestrator import create_media_generation_plan"
    )

early = r'''
    if adapter == "ugc_creative_deliverable_adapter":
        media_plan = create_media_generation_plan(
            "ugc_creative_agent",
            str(packet.get("user_requested_task") or action_text),
            tenant_id=tenant_id,
        )
        ugc_output = _generate_ugc_creative_deliverable(str(packet.get("user_requested_task") or action_text))

        return {
            "success": True,
            "execution_id": execution_id,
            "adapter": "ugc_creative_deliverable_adapter",
            "tenant_id": tenant_id,
            "performed_actual_action": True,
            "execution_status": "creative_deliverable_generated",
            "owner_approval_required": False,
            "customer_safe": True,
            "credential_values_exposed": False,
            "external_provider_called": False,
            "live_external_call_executed": False,
            "external_readiness": external_readiness,
            "external_action_ready": external_readiness.get("external_action_ready") is True,
            "real_external_execution": None,
            "internal_fallback_used": True,
            "missing_connections": external_readiness.get("missing_connections", []),
            "actions_performed": [
                {
                    "type": "ugc_campaign_deliverable_created",
                    "status": "created",
                    "target_system": "creative_deliverable_runtime",
                    "record_id": f"ugc_{uuid4().hex[:10]}",
                    "deliverable_sections": [
                        "storyboard",
                        "shot_list",
                        "creator_brief",
                        "voiceover_script",
                        "video_generation_prompt",
                        "avatar_video_prompt",
                        "paid_social_variants",
                    ],
                }
            ],
            "media_generation_plan": media_plan,
            "output": ugc_output,
            "asset": {
                "asset_id": asset_id,
                "task_id": task_id,
                "status": "created",
                "preview_ready": True,
                "download_ready": False,
                "customer_safe": True,
            },
            "created_at": _now(),
        }

'''

needle = '    real_external_result = None'
if early not in s:
    s = s.replace(needle, early + "\n" + needle)

TARGET.write_text(s, encoding="utf-8")

print("UGC_MEDIA_PLAN_FORCE_RETURN_INSTALLED")
print("Backup:", BACKUP)