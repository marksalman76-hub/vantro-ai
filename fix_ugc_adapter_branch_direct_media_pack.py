from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
TARGET = ROOT / "backend/app/runtime/action_adapter_execution_layer.py"
BACKUP = ROOT / "backups" / f"ugc_adapter_direct_media_pack_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
BACKUP.mkdir(parents=True, exist_ok=True)
shutil.copy2(TARGET, BACKUP / TARGET.name)

text = TARGET.read_text(encoding="utf-8")
original = text

needle = '''        media_plan = create_media_generation_plan(
            "ugc_creative_agent",'''

insert = '''        media_pack = generate_creative_media_pack(
            task=str(packet.get("user_requested_task") or action_text),
            agent_id="ugc_creative_agent",
            tenant_id=tenant_id,
            include_image=True,
            include_audio=True,
            include_video=True,
            include_avatar=True,
        )
        visual_asset = (media_pack.get("image_assets") or [{}])[0]

'''

if 'media_pack = generate_creative_media_pack(\n            task=str(packet.get("user_requested_task") or action_text),\n            agent_id="ugc_creative_agent",' not in text:
    text = text.replace(needle, insert + needle)

text = text.replace(
    '''            "media_generation_plan": media_plan,''',
    '''            "media_generation_plan": media_plan,
            "creative_media_pack": media_pack,
            "media_assets": media_pack.get("media_assets", []),
            "persisted_asset_count": media_pack.get("persisted_asset_count", 0),
            "real_media_asset_count": media_pack.get("real_media_asset_count", 0),'''
)

if text == original:
    print("NO_CHANGE_UGC_ADAPTER_ALREADY_PATCHED")
else:
    TARGET.write_text(text, encoding="utf-8", newline="\n")
    print("UGC_ADAPTER_BRANCH_DIRECT_MEDIA_PACK_PATCHED")
    print(f"Backup: {BACKUP}")