from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
adapter_file = ROOT / "backend" / "app" / "runtime" / "action_adapter_execution_layer.py"

backup_dir = ROOT / "backups" / f"execution_adapter_target_propagation_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)
shutil.copy2(adapter_file, backup_dir / adapter_file.name)

text = adapter_file.read_text(encoding="utf-8")

old = '''    adapter = classify_action_adapter(packet)
    external_readiness = classify_external_action_readiness(
        adapter=adapter,
'''

new = '''    adapter = (
        packet.get("execution_adapter_target")
        or packet.get("adapter")
        or classify_action_adapter(packet)
    )
    external_readiness = classify_external_action_readiness(
        adapter=adapter,
'''

if old not in text:
    raise SystemExit("ADAPTER_ASSIGNMENT_BLOCK_NOT_FOUND")

text = text.replace(old, new, 1)

adapter_file.write_text(text, encoding="utf-8")

test_file = ROOT / "test_execution_adapter_target_propagation.py"
test_file.write_text(r'''
from backend.app.runtime.action_adapter_execution_layer import execute_action_adapter

packet = {
    "implementation_action": "Send governed live email verification through connected email provider",
    "execution_adapter_target": "stakeholder_interview_outreach_adapter",
}

result = execute_action_adapter(
    packet,
    tenant_id="tenant_test",
    connected_integrations=["email"],
    owner_approved=True,
)

assert result["adapter"] == "stakeholder_interview_outreach_adapter"
assert result["external_readiness"]["adapter"] == "stakeholder_interview_outreach_adapter"
assert result["performed_actual_action"] is True

print("EXECUTION_ADAPTER_TARGET_PROPAGATION_TEST_PASSED")
''', encoding="utf-8")

print("EXECUTION_ADAPTER_TARGET_PROPAGATION_FIXED")
print(f"Backup: {backup_dir}")
print(f"Updated: {adapter_file}")
print(f"Created: {test_file}")