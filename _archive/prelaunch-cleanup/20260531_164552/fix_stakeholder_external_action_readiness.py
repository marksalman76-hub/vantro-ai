from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
target = ROOT / "backend" / "app" / "runtime" / "external_action_readiness_classifier.py"

backup_dir = ROOT / "backups" / f"stakeholder_external_action_readiness_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)
shutil.copy2(target, backup_dir / target.name)

text = target.read_text(encoding="utf-8")

print("CURRENT FILE PREVIEW:")
print(text[:4000])

# Robust append-style override: keep existing code, then redefine the function at bottom.
append = r'''

# --- patched: stakeholder outreach adapter live external readiness ---
_PREVIOUS_CLASSIFY_EXTERNAL_ACTION_READINESS = classify_external_action_readiness

def classify_external_action_readiness(
    *,
    adapter: str,
    connected_integrations: list[str] | None = None,
    owner_approved: bool = False,
):
    connected = set(connected_integrations or [])

    if adapter == "stakeholder_interview_outreach_adapter":
        required = []
        if "email" not in connected:
            required.append("email")

        return {
            "success": True,
            "profile": "external_action_readiness_classifier_v1",
            "adapter": adapter,
            "connected_integrations": list(connected),
            "external_action_ready": "email" in connected,
            "required_connections": ["email"],
            "missing_connections": required,
            "owner_approved": owner_approved,
            "live_execution_allowed": "email" in connected and owner_approved is True,
            "customer_safe": True,
            "credential_values_exposed": False,
        }

    return _PREVIOUS_CLASSIFY_EXTERNAL_ACTION_READINESS(
        adapter=adapter,
        connected_integrations=connected_integrations,
        owner_approved=owner_approved,
    )
'''

if "_PREVIOUS_CLASSIFY_EXTERNAL_ACTION_READINESS" not in text:
    text = text.rstrip() + "\n" + append

target.write_text(text, encoding="utf-8")

test_file = ROOT / "test_stakeholder_external_action_readiness.py"
test_file.write_text(r'''
from backend.app.runtime.external_action_readiness_classifier import classify_external_action_readiness
from backend.app.runtime.action_adapter_execution_layer import execute_action_adapter

ready = classify_external_action_readiness(
    adapter="stakeholder_interview_outreach_adapter",
    connected_integrations=["email"],
    owner_approved=True,
)

assert ready["success"] is True
assert ready["external_action_ready"] is True
assert ready["live_execution_allowed"] is True
assert ready["missing_connections"] == []

blocked = classify_external_action_readiness(
    adapter="stakeholder_interview_outreach_adapter",
    connected_integrations=[],
    owner_approved=True,
)

assert blocked["external_action_ready"] is False
assert "email" in blocked["missing_connections"]

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
assert result["external_action_ready"] is True
assert "real_external_execution" in result

print("STAKEHOLDER_EXTERNAL_ACTION_READINESS_TEST_PASSED")
''', encoding="utf-8")

print("STAKEHOLDER_EXTERNAL_ACTION_READINESS_FIXED")
print(f"Backup: {backup_dir}")
print(f"Updated: {target}")
print(f"Created: {test_file}")