from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
TARGET = ROOT / "backend/app/runtime/real_action_execution_bridge.py"
BACKUP = ROOT / "backups" / f"portal_creative_execution_bridge_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
BACKUP.mkdir(parents=True, exist_ok=True)
shutil.copy2(TARGET, BACKUP / TARGET.name)

text = TARGET.read_text(encoding="utf-8")
original = text

helper = r'''

def _force_creative_media_pack_persistence(packet: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Final portal bridge:
    when a creative/media agent is run from either portal, force the shared creative
    media runtime to create and persist a real media pack into the creative asset registry.
    This prevents successful portal executions from ending with no new Creative Assets record.
    """
    try:
        agent_id = (
            packet.get("agent_id")
            or packet.get("selected_agent")
            or packet.get("requested_agent")
            or packet.get("agent")
            or result.get("agent_id")
            or result.get("assigned_agent")
            or ""
        )
        task = (
            packet.get("task")
            or packet.get("prompt")
            or packet.get("message")
            or packet.get("instruction")
            or result.get("task")
            or result.get("summary")
            or ""
        )

        if not _is_creative_media_agent_or_request({"agent_id": agent_id, "task": task, **packet}):
            return {
                "success": True,
                "creative_media_pack_forced": False,
                "reason": "not_creative_media_execution",
                "credential_values_exposed": False,
            }

        from backend.app.runtime.shared_creative_media_generation_runtime import generate_creative_media_pack

        media_pack = generate_creative_media_pack(
            task=task or "Create a premium customer-safe creative media asset.",
            agent_id=str(agent_id or "creative_agent"),
            tenant_id=str(packet.get("tenant_id") or packet.get("client_id") or "owner_admin"),
            include_video=True,
            include_audio=True,
            include_avatar=False,
        )

        result["creative_media_pack"] = media_pack
        result["media_assets"] = media_pack.get("media_assets", [])
        result["generation_jobs"] = media_pack.get("generation_jobs", [])
        result["persisted_asset_records"] = [
            asset.get("persistence")
            for asset in media_pack.get("media_assets", [])
            if isinstance(asset, dict) and isinstance(asset.get("persistence"), dict)
        ]
        result["creative_media_pack_forced"] = True
        result["creative_asset_registry_write_attempted"] = True
        result["creative_asset_registry_persisted_count"] = len(result["persisted_asset_records"])
        result["credential_values_exposed"] = False

        return {
            "success": True,
            "creative_media_pack_forced": True,
            "persisted_asset_count": len(result["persisted_asset_records"]),
            "media_asset_count": len(media_pack.get("media_assets", [])),
            "credential_values_exposed": False,
        }
    except Exception as exc:
        result["creative_media_pack_forced"] = False
        result["creative_asset_registry_write_attempted"] = True
        result["creative_asset_registry_error"] = str(exc)[:500]
        result["credential_values_exposed"] = False
        return {
            "success": False,
            "creative_media_pack_forced": False,
            "error": str(exc)[:500],
            "credential_values_exposed": False,
        }

'''

if "_force_creative_media_pack_persistence" not in text:
    marker = "\ndef execute_real_action_packet("
    text = text.replace(marker, helper + marker)

# Insert force call before every successful return payload from execute_real_action_packet.
# This uses broad but safe placement: after result/output dicts are assembled, before final return.
if "creative_media_force_result = _force_creative_media_pack_persistence(packet, result)" not in text:
    text = text.replace(
        'result["credential_values_exposed"] = False\n    return result',
        'result["credential_values_exposed"] = False\n    creative_media_force_result = _force_creative_media_pack_persistence(packet, result)\n    result["creative_media_force_result"] = creative_media_force_result\n    return result'
    )

if text == original:
    print("NO_CHANGE_PORTAL_CREATIVE_EXECUTION_BRIDGE_ALREADY_PATCHED")
else:
    TARGET.write_text(text, encoding="utf-8", newline="\n")
    print("PORTAL_CREATIVE_EXECUTION_PERSISTENCE_BRIDGE_PATCHED")
    print(f"Backup: {BACKUP}")