import json
from pathlib import Path

ROOT = Path.cwd()
pack = json.loads((ROOT / "backend" / "app" / "data" / "step249_marketing_sales_rollout_pack.json").read_text(encoding="utf-8"))

checks = {
    "pack_success": pack.get("success") is True,
    "status_locked": pack.get("status") == "marketing_sales_rollout_pack_locked",
    "positioning_present": bool(pack.get("positioning")),
    "packages_present": len(pack.get("packages", {})) >= 4,
    "sales_sections_present": len(pack.get("sales_page_sections", [])) >= 5,
    "demo_script_present": len(pack.get("demo_script", [])) >= 5,
    "launch_checklist_present": len(pack.get("launch_checklist", [])) >= 5,
}

print("STEP_249_MARKETING_SALES_ROLLOUT_PACK_RESULTS")
for name, passed in checks.items():
    print(name, passed)

failed = [name for name, passed in checks.items() if not passed]
if failed:
    print("FAILED", failed)
    raise SystemExit(1)

print("STEP_249_MARKETING_SALES_ROLLOUT_PACK_OK")
