from pathlib import Path
from datetime import datetime
import re

root = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
backup_dir = root / "backups"
backup_dir.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

approval_path = root / "backend" / "app" / "approval" / "owner_approval_gateway.py"
workflow_path = root / "backend" / "app" / "workflows" / "ecommerce_workflow_engine.py"

for path in [approval_path, workflow_path]:
    backup = backup_dir / f"{path.stem}_before_phase_a_stabilizer_v2_{timestamp}{path.suffix}"
    backup.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")

approval_text = approval_path.read_text(encoding="utf-8")

if "governance_execution_registry" not in approval_text:
    approval_text = approval_text.replace(
        "from typing import Dict",
        "from backend.app.core.governance_execution_registry import is_safe_generation_action_type, is_prohibited_autonomous_action\nfrom typing import Dict",
    )

pattern = r"(class OwnerApprovalGateway:\s+def evaluate_action\(.*?\):)(.*?)(\ndef approval_summary)"
match = re.search(pattern, approval_text, flags=re.DOTALL)

if not match:
    raise RuntimeError("Could not patch evaluate_action")

replacement = '''class OwnerApprovalGateway:
    def evaluate_action(self, action_type: str, owner_approved: bool = False) -> ApprovalDecision:

        if is_prohibited_autonomous_action(action_type):
            return ApprovalDecision(
                action_type=action_type,
                requires_owner_approval=True,
                approved=False,
                status="rejected_prohibited_autonomous_action",
                reason="This action cannot be completed autonomously.",
            )

        if is_safe_generation_action_type(action_type):
            return ApprovalDecision(
                action_type=action_type,
                requires_owner_approval=False,
                approved=True,
                status="approved_safe_generation",
                reason="Approved by governance execution registry.",
            )

        if owner_approved:
            return ApprovalDecision(
                action_type=action_type,
                requires_owner_approval=True,
                approved=True,
                status="approved_by_owner",
                reason="Owner approved governed action.",
            )

        return ApprovalDecision(
            action_type=action_type,
            requires_owner_approval=True,
            approved=False,
            status="rejected_unknown_action",
            reason="Unknown actions are rejected by default.",
        )
'''

approval_text = (
    approval_text[:match.start()]
    + replacement
    + approval_text[match.end()-len("\ndef approval_summary"):]
)

approval_path.write_text(approval_text, encoding="utf-8")

workflow_text = workflow_path.read_text(encoding="utf-8")

if "governance_execution_registry" not in workflow_text:
    workflow_text = workflow_text.replace(
        "from typing import Dict",
        "from backend.app.core.governance_execution_registry import is_safe_generation_workflow_stage\nfrom typing import Dict",
    )

workflow_text = workflow_text.replace(
    'workflow_notes=["Rejected by default because the workflow stage is not recognised."]',
    'workflow_notes=["Safe generation workflow accepted."] if is_safe_generation_workflow_stage(workflow_stage) else ["Rejected by default because the workflow stage is not recognised."]'
)

workflow_text = workflow_text.replace(
    'blocked_reason="Unknown workflow stage. Owner approval or admin review required."',
    'blocked_reason=None if is_safe_generation_workflow_stage(workflow_stage) else "Unknown workflow stage. Owner approval or admin review required."'
)

workflow_text = workflow_text.replace(
    'requires_owner_approval=True,',
    'requires_owner_approval=not is_safe_generation_workflow_stage(workflow_stage),',
    1,
)

workflow_path.write_text(workflow_text, encoding="utf-8")

print("PHASE_A_STABILIZER_V2_INSTALLED")