import json
from pathlib import Path

ROOT = Path.cwd()
record = json.loads((ROOT / "backend" / "app" / "data" / "step263_ugc_human_realism_sync.json").read_text(encoding="utf-8"))
doc = ROOT / "docs" / "operations" / "ugc-human-realism-synchronisation.md"

checks = {
    "record_success": record.get("success") is True,
    "status_locked": record.get("status") == "ugc_human_realism_synchronisation_locked",
    "human_realism_layers_all_true": all(record.get("human_realism_layers", {}).values()),
    "quality_rules_all_true": all(record.get("quality_rules", {}).values()),
    "platform_rules_present": len(record.get("platform_rules", {})) >= 5,
    "governance_avatar_approval": record.get("governance", {}).get("paid_avatar_or_voice_generation_requires_owner_approval") is True,
    "governance_no_impersonation": record.get("governance", {}).get("creator_identity_must_not_impersonate_real_people_without_permission") is True,
    "doc_created": doc.exists(),
}

print("STEP_263_UGC_HUMAN_REALISM_SYNC_RESULTS")
for name, passed in checks.items():
    print(name, passed)

failed = [name for name, passed in checks.items() if not passed]
if failed:
    print("FAILED", failed)
    raise SystemExit(1)

print("STEP_263_UGC_HUMAN_REALISM_SYNC_OK")
