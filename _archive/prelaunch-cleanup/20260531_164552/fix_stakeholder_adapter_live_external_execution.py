from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
target = ROOT / "backend" / "app" / "runtime" / "action_adapter_execution_layer.py"

backup_dir = ROOT / "backups" / f"stakeholder_adapter_live_external_execution_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)
shutil.copy2(target, backup_dir / target.name)

text = target.read_text(encoding="utf-8")

old = '''    if adapter == "stakeholder_interview_outreach_adapter":
        actions = [
            {
                "type": "email_draft_created",
                "status": "created",
                "subject": "Healthcare technology positioning research interview",
                "body_preview": "Drafted outreach asking healthcare technology decision-makers for a short market validation interview.",
            },
            {
                "type": "crm_task_created",
                "status": "created",
                "task_title": "Book 5 healthcare stakeholder validation interviews",
                "priority": "high",
            },
            {
                "type": "calendar_placeholder_created",
                "status": "draft_created",
                "title": "Healthcare stakeholder interview slot",
            },
        ]
        output = "Created interview outreach draft, CRM follow-up task, and calendar placeholder draft."
'''

new = '''    if adapter == "stakeholder_interview_outreach_adapter":
        if real_external_result and real_external_result.get("success") and real_external_result.get("external_action_executed"):
            actions = real_external_result.get("actions_performed", [])
            output = real_external_result.get("summary") or "Real external integration actions executed."
        elif real_external_result and real_external_result.get("success") is False:
            actions = real_external_result.get("actions_performed", []) or [
                {
                    "type": "live_external_execution_failed",
                    "status": "failed",
                    "provider": "connected_integration_runtime",
                    "message": real_external_result.get("message") or real_external_result.get("error") or "Live external execution failed.",
                    "credential_exposed": False,
                }
            ]
            output = real_external_result.get("message") or real_external_result.get("error") or "Live external execution failed."
        else:
            actions = [
                {
                    "type": "email_draft_created",
                    "status": "created",
                    "subject": "Healthcare technology positioning research interview",
                    "body_preview": "Drafted outreach asking healthcare technology decision-makers for a short market validation interview.",
                },
                {
                    "type": "crm_task_created",
                    "status": "created",
                    "task_title": "Book 5 healthcare stakeholder validation interviews",
                    "priority": "high",
                },
                {
                    "type": "calendar_placeholder_created",
                    "status": "draft_created",
                    "title": "Healthcare stakeholder interview slot",
                },
            ]
            output = "Created interview outreach draft, CRM follow-up task, and calendar placeholder draft."
'''

if old not in text:
    raise SystemExit("STAKEHOLDER_ADAPTER_BLOCK_NOT_FOUND")

text = text.replace(old, new, 1)

old_return_marker = '''        "actions_performed": actions,
'''

new_return_marker = '''        "actions_performed": actions,
        "real_external_result": real_external_result,
        "external_action_performed": bool(real_external_result and real_external_result.get("external_action_executed")),
        "live_external_call_executed": bool(real_external_result and real_external_result.get("live_external_call_executed")),
'''

if old_return_marker not in text:
    raise SystemExit("RETURN_ACTIONS_MARKER_NOT_FOUND")

text = text.replace(old_return_marker, new_return_marker, 1)

target.write_text(text, encoding="utf-8")

test_file = ROOT / "test_stakeholder_adapter_live_external_execution.py"
test_file.write_text(r'''
from backend.app.runtime.action_adapter_execution_layer import execute_action_adapter

result = execute_action_adapter(
    {
        "implementation_action": "Send governed live email verification through connected email provider",
        "execution_adapter_target": "stakeholder_interview_outreach_adapter",
    },
    tenant_id="client_demo_001",
    connected_integrations=["email"],
    owner_approved=True,
)

assert result["adapter"] == "stakeholder_interview_outreach_adapter"
assert "actions_performed" in result
assert "real_external_result" in result
assert "external_action_performed" in result
assert "live_external_call_executed" in result

print("STAKEHOLDER_ADAPTER_LIVE_EXTERNAL_EXECUTION_TEST_PASSED")
''', encoding="utf-8")

print("STAKEHOLDER_ADAPTER_LIVE_EXTERNAL_EXECUTION_FIXED")
print(f"Backup: {backup_dir}")
print(f"Updated: {target}")
print(f"Created: {test_file}")