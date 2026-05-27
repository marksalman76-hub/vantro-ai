import json
from pathlib import Path

ROOT = Path.cwd()
record = json.loads((ROOT / "backend" / "app" / "data" / "step257_master_launch_handover_pack.json").read_text(encoding="utf-8"))
handover = ROOT / "docs" / "launch" / "master-launch-handover.md"

checks = {
    "record_success": record.get("success") is True,
    "status_locked": record.get("status") == "master_launch_handover_pack_locked",
    "handover_created": handover.exists(),
    "soft_launch_ready": record.get("platform_status") == "commercial_beta_soft_launch_ready",
    "live_urls_present": len(record.get("live_urls", {})) >= 4,
    "final_requirements_present": len(record.get("final_public_launch_requirements", [])) >= 6,
    "no_major_architecture_remaining": record.get("major_architecture_remaining") is False,
}

print("STEP_257_MASTER_LAUNCH_HANDOVER_PACK_RESULTS")
for name, passed in checks.items():
    print(name, passed)

failed = [name for name, passed in checks.items() if not passed]
if failed:
    print("FAILED", failed)
    raise SystemExit(1)

print("STEP_257_MASTER_LAUNCH_HANDOVER_PACK_OK")
