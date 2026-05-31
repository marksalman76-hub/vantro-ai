from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent
MAIN = ROOT / "backend" / "app" / "main.py"
BACKUP = ROOT / "backups" / f"owner_admin_live_provider_test_rule_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

OLD = '''    if not approval_result.get("approved"):
        return {
            "success": False,
            "status": approval_result.get("status"),
            "workflow": workflow_summary(workflow_packet),
            "approval": approval_result,
            "message": "Action paused or rejected by owner approval gateway.",
        }
'''

NEW = '''    owner_admin_live_provider_test_allowed = (
        (request.actor_role or "").strip().lower() in {"owner", "admin", "owner_admin", "system"}
        and (request.workflow_stage or "").strip().lower() in {"specialist_execution", "controlled_live_provider_test"}
        and (request.action_type or "").strip().lower() in {"run_agent", "provider_verification"}
        and requested_agent in {"marketing_specialist_agent"}
    )

    if not approval_result.get("approved") and not owner_admin_live_provider_test_allowed:
        return {
            "success": False,
            "status": approval_result.get("status"),
            "workflow": workflow_summary(workflow_packet),
            "approval": approval_result,
            "message": "Action paused or rejected by owner approval gateway.",
        }
'''

def main():
    text = MAIN.read_text(encoding="utf-8", errors="replace")

    if "owner_admin_live_provider_test_allowed" in text:
        print("OWNER_ADMIN_LIVE_PROVIDER_TEST_RULE_ALREADY_PRESENT")
        return

    if OLD not in text:
        raise RuntimeError("Approval rejection block not found")

    BACKUP.mkdir(parents=True, exist_ok=True)
    (BACKUP / "main.py").write_text(text, encoding="utf-8")

    MAIN.write_text(text.replace(OLD, NEW, 1), encoding="utf-8")

    print("OWNER_ADMIN_LIVE_PROVIDER_TEST_RULE_INSTALLED")
    print("Backup:", BACKUP)
    print("Updated:", MAIN)

if __name__ == "__main__":
    main()