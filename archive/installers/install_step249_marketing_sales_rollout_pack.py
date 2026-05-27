from pathlib import Path
from datetime import datetime
import json
import py_compile

ROOT = Path.cwd()
DATA = ROOT / "backend" / "app" / "data"
TEST = ROOT / "test_step249_marketing_sales_rollout_pack.py"

DATA.mkdir(parents=True, exist_ok=True)

pack = {
    "success": True,
    "step": 249,
    "status": "marketing_sales_rollout_pack_locked",
    "generated_at": datetime.utcnow().isoformat() + "Z",
    "positioning": {
        "product": "Premium white-label ecommerce AI agent platform",
        "market": "agencies, ecommerce operators, consultants, and businesses wanting governed AI execution",
        "core_offer": "A governed AI workforce for ecommerce growth, content, customer support, operations, analytics, billing, and automation.",
        "differentiators": [
            "25-agent ecommerce-specific catalogue",
            "admin-controlled deployment to clients",
            "multi-agent execution",
            "client portal with active paid agents only",
            "Stripe subscription billing",
            "owner-gated spend/scaling controls",
            "operational recovery and audit visibility",
            "white-label resale readiness",
        ],
    },
    "packages": {
        "starter": "Entry package for small ecommerce brands needing focused AI help.",
        "growth": "Multi-agent growth package for active ecommerce operations.",
        "pro": "Advanced package for higher-volume brands and agencies.",
        "manual_unlimited": "Admin-deployed unlimited-credit account for demos, VIPs, or custom clients.",
    },
    "sales_page_sections": [
        "Hero: Deploy a governed ecommerce AI workforce for your business or clients.",
        "Problem: Ecommerce teams need content, ads, product pages, support, analytics, and automation without hiring a full team.",
        "Solution: 25 specialised ecommerce AI agents working through a secure portal.",
        "Proof: Billing, governance, client activation, admin controls, and operational recovery are built in.",
        "CTA: Book a demo or request access.",
    ],
    "demo_script": [
        "Open admin portal.",
        "Show full 25-agent catalogue.",
        "Run one selected agent.",
        "Run multiple selected agents.",
        "Deploy a client with unlimited credits.",
        "Open client portal.",
        "Show only paid/active agents.",
        "Show billing/governance controls.",
    ],
    "launch_checklist": [
        "Rotate exposed Stripe key.",
        "Set hosted Render env vars.",
        "Set hosted Vercel env vars.",
        "Connect live provider key only after approval.",
        "Run live onboarding test.",
        "Run live checkout test.",
        "Run live customer execution test.",
        "Publish sales page.",
        "Prepare demo account.",
    ],
}

pack_file = DATA / "step249_marketing_sales_rollout_pack.json"
pack_file.write_text(json.dumps(pack, indent=2), encoding="utf-8")

TEST.write_text(r'''
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
'''.lstrip(), encoding="utf-8")

py_compile.compile(str(TEST), doraise=True)

print("STEP_249_MARKETING_SALES_ROLLOUT_PACK_INSTALLED")
print(f"Created/updated: {pack_file}")
print(f"Created/updated: {TEST}")
print("STEP_249_OK")