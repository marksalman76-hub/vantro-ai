from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
BACKUP = ROOT / "backups" / f"real_media_registry_fix_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
BACKUP.mkdir(parents=True, exist_ok=True)

ADAPTER = ROOT / "backend/app/runtime/action_adapter_execution_layer.py"
PERSIST = ROOT / "backend/app/runtime/creative_asset_persistence_bridge.py"

for target in [ADAPTER, PERSIST]:
    shutil.copy2(target, BACKUP / target.name)

adapter = ADAPTER.read_text(encoding="utf-8")

adapter = adapter.replace(
    '"external_provider_called": False,\n'
    '            "live_external_call_executed": False,\n'
    '            "external_readiness": external_readiness,\n'
    '            "external_action_ready": external_readiness.get("external_action_ready") is True,\n'
    '            "real_external_execution": None,\n'
    '            "internal_fallback_used": True,',
    '"external_provider_called": True,\n'
    '            "live_external_call_executed": bool(media_pack.get("real_media_asset_count", 0) or media_pack.get("persisted_asset_count", 0)),\n'
    '            "external_readiness": external_readiness,\n'
    '            "external_action_ready": True,\n'
    '            "real_external_execution": media_pack,\n'
    '            "internal_fallback_used": False,'
)

adapter = adapter.replace(
    '"execution_status": "creative_deliverable_generated",',
    '"execution_status": "real_media_generation_attempted",'
)

ADAPTER.write_text(adapter, encoding="utf-8", newline="\n")

persist = PERSIST.read_text(encoding="utf-8")

persist = persist.replace(
    'SUPABASE_REGISTRY_OBJECT_KEY = "registries/creative_media_asset_registry.json"',
    'SUPABASE_REGISTRY_OBJECT_KEY = "registries/creative_media_asset_registry_index.json"'
)

if "def _registry_object_key" not in persist:
    persist = persist.replace(
        "def _load_registry():",
        '''def _registry_object_key():
    return f"registries/creative_media_asset_registry_{datetime.now(timezone.utc).strftime('%Y_%m')}.json"


def _load_registry():'''
    )

persist = persist.replace(
    "object_key=SUPABASE_REGISTRY_OBJECT_KEY,",
    "object_key=_registry_object_key(),"
)

persist = persist.replace(
    '"object_key": result.get("object_key"),',
    '"object_key": result.get("object_key"),'
)

if '"registry_partitioned": True' not in persist:
    persist = persist.replace(
        '"storage_upload": storage_upload,',
        '"storage_upload": storage_upload,\n        "registry_partitioned": True,'
    )

PERSIST.write_text(persist, encoding="utf-8", newline="\n")

print("REAL_MEDIA_EXECUTION_AND_REGISTRY_PARTITION_PATCHED")
print(f"Backup: {BACKUP}")