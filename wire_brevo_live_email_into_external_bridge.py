from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
target = ROOT / "backend" / "app" / "runtime" / "real_external_integration_execution_bridge.py"

backup_dir = ROOT / "backups" / f"brevo_live_email_external_bridge_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)
shutil.copy2(target, backup_dir / target.name)

text = target.read_text(encoding="utf-8")

old_import = """from uuid import uuid4
"""

new_import = """from uuid import uuid4

from backend.app.core.integration_live_adapter_registry import execute_integration_action
"""

if old_import not in text:
    raise SystemExit("IMPORT_BLOCK_NOT_FOUND")

text = text.replace(old_import, new_import)

old_email_block = '''            email_action = {
                "type": "email_draft_created",
                "status": "executed",
                "provider": "governed_email_runtime",
                "draft_id": f"email_draft_{uuid4().hex[:10]}",
                "subject": action_text[:120],
                "tenant_id": tenant_id,
            }
            actions_performed.append(email_action)
            external_calls.append("email")
'''

new_email_block = '''            email_payload = {
                "recipient": "mark@trance-formation.com.au",
                "sender_email": "noreply@trance-formation.com.au",
                "sender_name": "AI Workforce Platform",
                "subject": f"Live delegated workforce proof: {action_text[:80]}",
                "html_content": (
                    "<p>This is a governed live email execution proof from the delegated "
                    "AI workforce runtime.</p>"
                    f"<p><strong>Action:</strong> {action_text}</p>"
                ),
            }

            email_result = execute_integration_action(
                tenant_id=tenant_id,
                integration_key="email",
                action="send_email",
                payload=email_payload,
                actor_role="owner",
            )

            if email_result.get("success"):
                email_action = {
                    "type": "email_sent",
                    "status": "executed",
                    "provider": email_result.get("provider") or "Brevo",
                    "provider_mode": email_result.get("mode"),
                    "provider_response": email_result.get("provider_response"),
                    "recipient": email_result.get("recipient"),
                    "subject": email_result.get("subject"),
                    "tenant_id": tenant_id,
                    "credential_exposed": False,
                }
            else:
                email_action = {
                    "type": "email_live_execution_failed",
                    "status": "failed",
                    "provider": email_result.get("provider") or "Brevo",
                    "error": email_result.get("error"),
                    "message": email_result.get("message"),
                    "tenant_id": tenant_id,
                    "credential_exposed": False,
                }

            actions_performed.append(email_action)
            if email_result.get("success"):
                external_calls.append("email")
'''

if old_email_block not in text:
    raise SystemExit("EMAIL_BLOCK_NOT_FOUND")

text = text.replace(old_email_block, new_email_block)

target.write_text(text, encoding="utf-8")

test_file = ROOT / "test_brevo_live_email_bridge_wiring.py"
test_file.write_text(r'''
from pathlib import Path

p = Path("backend/app/runtime/real_external_integration_execution_bridge.py")
text = p.read_text(encoding="utf-8")

assert "execute_integration_action" in text
assert 'integration_key="email"' in text
assert 'action="send_email"' in text
assert "email_sent" in text
assert "email_live_execution_failed" in text
assert "credential_exposed" in text

print("BREVO_LIVE_EMAIL_BRIDGE_WIRING_TEST_PASSED")
''', encoding="utf-8")

print("BREVO_LIVE_EMAIL_EXTERNAL_BRIDGE_WIRED")
print(f"Backup: {backup_dir}")
print(f"Updated: {target}")
print(f"Created: {test_file}")