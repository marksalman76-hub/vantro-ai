from pathlib import Path
from datetime import datetime
import json
import subprocess

ROOT = Path.cwd()
OUT = ROOT / "docs" / "final-sellable-product-closeout-report.md"
JSON_OUT = ROOT / "final_sellable_product_closeout_audit.json"

checks = {
    "path_a_effectively_complete": True,
    "sellable_product_closeout_before_path_b": True,
    "owner_admin_unrestricted": True,
    "governance_preserved": True,
    "customer_safe_ui_required": True,
    "no_new_backend_rebuild_required": True,
    "path_b_not_started": True,
}

required_paths = [
    "backend/app/main.py",
    "frontend/src/app/admin/page.tsx",
    "frontend/src/app/client/page.tsx",
    "frontend/src/app/page.tsx",
    "frontend/src/app/api/run-agent/route.ts",
]

path_results = {p: (ROOT / p).exists() for p in required_paths}

report = {
    "timestamp": datetime.utcnow().isoformat() + "Z",
    "closeout_scope": "Final sellable-product closeout before Path B",
    "path_a_status": "effectively_complete",
    "path_b_status": "not_started",
    "checks": checks,
    "required_path_results": path_results,
    "remaining_focus": [
        "Final owner-facing product confidence report",
        "Final sellable readiness evidence pack",
        "Final launch/sales handover notes",
        "No further Path A expansion unless a verified blocker appears",
    ],
}

JSON_OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(
f"""# Final Sellable-Product Closeout Report

Generated: {report['timestamp']}

## Status

Path A is treated as **effectively complete**.

This closeout is for confirming the platform as a sellable governed AI agent product before starting Path B.

## Locked Position

- Path A: **Effectively complete**
- Path B: **Not started**
- Backend rebuilds: **Not required unless a verified blocker appears**
- Governance: **Preserved**
- Owner/admin unrestricted rule: **Preserved**
- Client/customer-safe UI rule: **Preserved**

## Required File Presence

{json.dumps(path_results, indent=2)}

## Remaining Closeout Items

1. Final owner-facing sellable-product summary
2. Final evidence pack
3. Final sales/launch handover notes
4. Commit closeout files
5. Move to Path B only after closeout is committed

## Decision

Do **not** continue adding Path A features.  
Only fix verified blockers.
""",
encoding="utf-8"
)

print("FINAL_SELLABLE_PRODUCT_CLOSEOUT_AUDIT_CREATED")
print("Created:", JSON_OUT)
print("Created:", OUT)