from pathlib import Path
from datetime import datetime
import re

root = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
backup_dir = root / "backups"
backup_dir.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

approval_path = root / "backend" / "app" / "core" / "owner_approval_gateway.py"
workflow_path = root / "backend" / "app" / "workflows" / "ecommerce_workflow_engine.py"
main_path = root / "backend" / "app" / "main.py"

for path in [approval_path, workflow_path, main_path]:
    backup = backup_dir / f"{path.stem}_before_phase_a_governance_stabilizer_{timestamp}{path.suffix}"
    backup.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")

approval_text = approval_path.read_text(encoding="utf-8")

if "governance_execution_registry" not in approval_text:
    approval_text = approval_text.replace(
        "from typing import",
        "from backend.app.core.governance_execution_registry import is_safe_generation_action_type, is_prohibited_autonomous_action\nfrom typing import",
        1,
    )

pattern = r"(    def evaluate_action\(.*?\n)(.*?)(\n    def |\Z)"
match = re.search(pattern, approval_text, flags=re.DOTALL)

if not match:
    raise RuntimeError("Could not locate evaluate_action method in owner_approval_gateway.py")

method_header = match.group(1)
next_marker = match.group(3)

new_method_body = '''        if is_prohibited_autonomous_action(action_type):
            return ApprovalDecision(
                action_type=action_type,
                requires_owner_approval=True,
                approved=False,
                status="rejected_prohibited_autonomous_action",
                reason="This action cannot be completed autonomously and requires explicit owner control.",
            )

        if is_safe_generation_action_type(action_type):
            return ApprovalDecision(
                action_type=action_type,
                requires_owner_approval=False,
                approved=True,
                status="approved_safe_generation",
                reason="Safe generation action approved by governance execution registry.",
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
            reason="Unknown actions are rejected by default until owner approval rules are defined.",
        )
'''

approval_text = approval_text[:match.start()] + method_header + new_method_body + next_marker + approval_text[match.end():]
approval_path.write_text(approval_text, encoding="utf-8")

workflow_text = workflow_path.read_text(encoding="utf-8")

if "governance_execution_registry" not in workflow_text:
    workflow_text = workflow_text.replace(
        "from typing import",
        "from backend.app.core.governance_execution_registry import is_safe_generation_workflow_stage\nfrom typing import",
        1,
    )

workflow_text = workflow_text.replace(
    '''            requires_owner_approval=True,
            client_safe=True,
            blocked_reason="Unknown workflow stage. Owner approval or admin review required.",
            workflow_notes=["Rejected by default because the workflow stage is not recognised."],
''',
    '''            requires_owner_approval=not is_safe_generation_workflow_stage(workflow_stage),
            client_safe=True,
            blocked_reason=None if is_safe_generation_workflow_stage(workflow_stage) else "Unknown workflow stage. Owner approval or admin review required.",
            workflow_notes=["Safe generation workflow accepted."] if is_safe_generation_workflow_stage(workflow_stage) else ["Rejected by default because the workflow stage is not recognised."],
''',
)

workflow_path.write_text(workflow_text, encoding="utf-8")

test_path = root / "test_phase_a_all_25_agents_execution.py"
test_path.write_text(
'''import requests

from backend.app.core.governance_execution_registry import get_default_workflow_stage

BASE_URL = "http://127.0.0.1:8000"

AGENTS = [
    "head_agent",
    "strategist_agent",
    "business_growth_partnerships_agent",
    "lead_generator_appointment_setter_agent",
    "marketing_specialist_agent",
    "social_media_manager_content_creator_agent",
    "seo_agent",
    "email_reply_agent",
    "crm_ai_agent",
    "sales_closer_agent",
    "receptionist_agent",
    "customer_support_agent",
    "ecommerce_agent",
    "product_research_agent",
    "competitor_intelligence_agent",
    "brand_strategy_agent",
    "store_builder_agent",
    "website_landing_apps_agent",
    "product_development_agent",
    "product_copywriting_agent",
    "ugc_creative_agent",
    "product_image_agent",
    "paid_ads_agent",
    "analytics_optimisation_agent",
    "influencer_collaboration_agent",
]

headers = {
    "Content-Type": "application/json",
    "x-tenant-id": "client_demo_001",
    "x-actor-role": "owner",
}

passed = []
failed = []

for agent_id in AGENTS:
    payload = {
        "tenant_id": "client_demo_001",
        "workflow_stage": get_default_workflow_stage(agent_id),
        "requested_agent": agent_id,
        "task": f"Create a premium real-world task-ready output for {agent_id}.",
        "action_type": "content_generation",
        "owner_approved": True,
        "actor_role": "owner",
        "requested_credits": 1,
    }

    response = requests.post(f"{BASE_URL}/run-agent", json=payload, headers=headers, timeout=120)

    try:
        data = response.json()
    except Exception:
        data = {"raw": response.text}

    if response.status_code == 200 and data.get("success") is True:
        passed.append(agent_id)
        print(f"{agent_id}: PASS")
    else:
        failed.append({"agent": agent_id, "status": response.status_code, "response": data})
        print(f"{agent_id}: FAIL")

print("PHASE_A_ALL_25_AGENTS_EXECUTION_RESULTS")
print("PASSED_COUNT", len(passed))
print("FAILED_COUNT", len(failed))

if failed:
    print("FAILED_DETAILS")
    for item in failed:
        print(item)

if not failed:
    print("PHASE_A_ALL_25_AGENTS_EXECUTION_READY")
''',
encoding="utf-8",
)

print("PHASE_A_GOVERNANCE_EXECUTION_STABILIZER_INSTALLED")
print("Backups created in backups folder.")
print(f"Created: {test_path}")