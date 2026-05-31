from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent
MAIN = ROOT / "backend" / "app" / "main.py"
BACKUP = ROOT / "backups" / f"owner_admin_live_provider_test_rule_v2_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

NEEDLE = '''        execution_event_ledger.record(
            tenant_id=request.tenant_id,
            project_id=request.project_id,
            agent_id=requested_agent,
            actor_role=request.actor_role,
            workflow_stage=request.workflow_stage,
            action_type=request.action_type,
            execution_action=None,
            event_type="approval_gate_blocked",
            event_status=approval_decision.status,
            title=f"{requested_agent} action paused by approval gateway",
            summary="Action paused or rejected by owner approval gateway.",
            workflow=workflow_summary(workflow_packet),
            approval=approval_summary(approval_decision),
            owner_approved=request.owner_approved,
            client_visible=True,
        )

        return {
            "success": False,
            "status": approval_decision.status,
            "workflow": workflow_summary(workflow_packet),
            "approval": approval_summary(approval_decision),
            "message": "Action paused or rejected by owner approval gateway.",
        }
'''

REPLACEMENT = '''        owner_admin_live_provider_test_allowed = (
            (request.actor_role or "").strip().lower() in {"owner", "admin", "owner_admin", "system"}
            and (request.workflow_stage or "").strip().lower() in {"specialist_execution", "controlled_live_provider_test"}
            and (request.action_type or "").strip().lower() in {"run_agent", "provider_verification"}
            and requested_agent in {"marketing_specialist_agent"}
        )

        if not owner_admin_live_provider_test_allowed:
            execution_event_ledger.record(
                tenant_id=request.tenant_id,
                project_id=request.project_id,
                agent_id=requested_agent,
                actor_role=request.actor_role,
                workflow_stage=request.workflow_stage,
                action_type=request.action_type,
                execution_action=None,
                event_type="approval_gate_blocked",
                event_status=approval_decision.status,
                title=f"{requested_agent} action paused by approval gateway",
                summary="Action paused or rejected by owner approval gateway.",
                workflow=workflow_summary(workflow_packet),
                approval=approval_summary(approval_decision),
                owner_approved=request.owner_approved,
                client_visible=True,
            )

            return {
                "success": False,
                "status": approval_decision.status,
                "workflow": workflow_summary(workflow_packet),
                "approval": approval_summary(approval_decision),
                "message": "Action paused or rejected by owner approval gateway.",
            }
'''

def main():
    text = MAIN.read_text(encoding="utf-8", errors="replace")

    if "owner_admin_live_provider_test_allowed" in text:
        print("OWNER_ADMIN_LIVE_PROVIDER_TEST_RULE_ALREADY_PRESENT")
        return

    if NEEDLE not in text:
        raise RuntimeError("Actual approval gate block not found")

    BACKUP.mkdir(parents=True, exist_ok=True)
    (BACKUP / "main.py").write_text(text, encoding="utf-8")

    MAIN.write_text(text.replace(NEEDLE, REPLACEMENT, 1), encoding="utf-8")

    print("OWNER_ADMIN_LIVE_PROVIDER_TEST_RULE_V2_INSTALLED")
    print("Backup:", BACKUP)
    print("Updated:", MAIN)

if __name__ == "__main__":
    main()