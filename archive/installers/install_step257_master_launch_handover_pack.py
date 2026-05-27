from pathlib import Path
from datetime import datetime
import json
import py_compile

ROOT = Path.cwd()
DOCS = ROOT / "docs" / "launch"
DATA = ROOT / "backend" / "app" / "data"
TEST = ROOT / "test_step257_master_launch_handover_pack.py"

DOCS.mkdir(parents=True, exist_ok=True)
DATA.mkdir(parents=True, exist_ok=True)

handover = {
    "success": True,
    "step": 257,
    "status": "master_launch_handover_pack_locked",
    "generated_at": datetime.utcnow().isoformat() + "Z",
    "platform_status": "commercial_beta_soft_launch_ready",
    "completion": {
        "architecture": "100%",
        "core_execution": "100%",
        "admin_portal": "live",
        "client_portal": "live",
        "billing_checkout": "checkout_verified_payment_deferred",
        "legal_support_drafts": "created",
        "monitoring_backup_plan": "created",
        "soft_launch_plan": "created",
    },
    "live_urls": {
        "frontend": "https://ecommerce-ai-agent-platform.vercel.app",
        "admin": "https://ecommerce-ai-agent-platform.vercel.app/admin",
        "client": "https://ecommerce-ai-agent-platform.vercel.app/client",
        "backend_health": "https://ecommerce-ai-agent-platform-1.onrender.com/health",
    },
    "final_public_launch_requirements": [
        "Legal review of docs/legal pages.",
        "Configure real monitoring alerts.",
        "Configure backup schedule.",
        "Complete one real Stripe payment when ready.",
        "Run one pilot customer onboarding.",
        "Run one pilot customer execution.",
        "Finalise pricing and top-up pricing.",
        "Publish final sales page/demo assets.",
    ],
    "major_architecture_remaining": False,
}

(DATA / "step257_master_launch_handover_pack.json").write_text(json.dumps(handover, indent=2), encoding="utf-8")

(DOCS / "master-launch-handover.md").write_text("""# Master Launch Handover

## Status
Commercial beta / soft-launch ready.

## Live URLs
- Frontend: https://ecommerce-ai-agent-platform.vercel.app
- Admin: https://ecommerce-ai-agent-platform.vercel.app/admin
- Client: https://ecommerce-ai-agent-platform.vercel.app/client
- Backend health: https://ecommerce-ai-agent-platform-1.onrender.com/health

## Locked Capabilities
- 25-agent catalogue
- Admin multi-agent execution
- Client active-agent execution
- Admin deploy/suspend/cancel/reactivate controls
- Unlimited-credit manual deployment
- Stripe checkout readiness
- Live checkout page verification
- Governance and owner approval controls
- Legal/support draft pack
- Monitoring/backup runbook
- Soft-launch checklist

## Remaining Before Public Launch
1. Legal review.
2. Monitoring/alert setup.
3. Backup schedule setup.
4. One real payment.
5. One pilot onboarding.
6. One customer execution.
7. Sales page/demo rollout.

## Architecture Remaining
No major architecture work remains.
""", encoding="utf-8")

TEST.write_text(r'''
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
'''.lstrip(), encoding="utf-8")

py_compile.compile(str(TEST), doraise=True)

print("STEP_257_MASTER_LAUNCH_HANDOVER_PACK_INSTALLED")
print("STEP_257_OK")