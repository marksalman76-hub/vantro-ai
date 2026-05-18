from pathlib import Path
from datetime import datetime

root = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
backup_dir = root / "backups"
backup_dir.mkdir(exist_ok=True)

main_path = root / "backend" / "app" / "main.py"
workflow_path = root / "backend" / "app" / "workflows" / "ecommerce_workflow_engine.py"
approval_path = root / "backend" / "app" / "core" / "owner_approval_gateway.py"

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

for path in [main_path, workflow_path, approval_path]:
    if path.exists():
        backup = backup_dir / f"{path.stem}_before_step13_governance_execution_registry_{timestamp}{path.suffix}"
        backup.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")

registry_path = root / "backend" / "app" / "core" / "governance_execution_registry.py"
registry_path.write_text(
'''from __future__ import annotations

from typing import Dict, List


SAFE_GENERATION_WORKFLOW_STAGES = {
    "marketing_campaign",
    "content_generation",
    "sales_follow_up",
    "crm_optimisation",
    "customer_support",
    "seo_strategy",
    "product_research",
    "competitor_analysis",
    "brand_strategy",
    "store_optimisation",
    "website_landing_page",
    "product_development",
    "product_copywriting",
    "ugc_creative",
    "product_image_direction",
    "paid_ads_strategy",
    "analytics_optimisation",
    "influencer_outreach",
    "reception_intake",
    "business_growth",
    "strategic_planning",
    "head_agent_review",
}

SAFE_GENERATION_ACTION_TYPES = {
    "content_generation",
    "marketing_campaign_execution",
    "strategy_generation",
    "draft_generation",
    "analysis_generation",
    "crm_recommendation",
    "support_response_generation",
    "seo_plan_generation",
    "sales_follow_up_generation",
    "website_brief_generation",
    "product_brief_generation",
    "creative_brief_generation",
    "analytics_report_generation",
    "influencer_outreach_generation",
}

REAL_WORLD_ACTION_TYPES_REQUIRING_OWNER_APPROVAL = {
    "send_email",
    "send_sms",
    "create_crm_contact",
    "create_crm_opportunity",
    "update_crm_record",
    "publish_content",
    "launch_campaign",
    "website_deploy_execution",
    "billing_payment_execution",
}

PROHIBITED_AUTONOMOUS_ACTION_TYPES = {
    "increase_ad_spend",
    "change_ad_budget",
    "scale_campaign_budget",
    "approve_contract",
    "approve_paid_collaboration",
    "purchase_inventory",
    "charge_customer",
    "change_subscription_price",
}

AGENT_DEFAULT_WORKFLOW_STAGE: Dict[str, str] = {
    "head_agent": "head_agent_review",
    "strategist_agent": "strategic_planning",
    "business_growth_partnerships_agent": "business_growth",
    "lead_generator_appointment_setter_agent": "sales_follow_up",
    "marketing_specialist_agent": "marketing_campaign",
    "social_media_manager_content_creator_agent": "content_generation",
    "seo_agent": "seo_strategy",
    "email_reply_agent": "content_generation",
    "crm_ai_agent": "crm_optimisation",
    "sales_closer_agent": "sales_follow_up",
    "receptionist_agent": "reception_intake",
    "customer_support_agent": "customer_support",
    "ecommerce_agent": "store_optimisation",
    "product_research_agent": "product_research",
    "competitor_intelligence_agent": "competitor_analysis",
    "brand_strategy_agent": "brand_strategy",
    "store_builder_agent": "store_optimisation",
    "website_landing_apps_agent": "website_landing_page",
    "product_development_agent": "product_development",
    "product_copywriting_agent": "product_copywriting",
    "ugc_creative_agent": "ugc_creative",
    "product_image_agent": "product_image_direction",
    "paid_ads_agent": "paid_ads_strategy",
    "analytics_optimisation_agent": "analytics_optimisation",
    "influencer_collaboration_agent": "influencer_outreach",
}


def is_safe_generation_workflow_stage(workflow_stage: str) -> bool:
    return str(workflow_stage or "").strip() in SAFE_GENERATION_WORKFLOW_STAGES


def is_safe_generation_action_type(action_type: str) -> bool:
    return str(action_type or "").strip() in SAFE_GENERATION_ACTION_TYPES


def is_real_world_action_requiring_owner_approval(action_type: str) -> bool:
    return str(action_type or "").strip() in REAL_WORLD_ACTION_TYPES_REQUIRING_OWNER_APPROVAL


def is_prohibited_autonomous_action(action_type: str) -> bool:
    return str(action_type or "").strip() in PROHIBITED_AUTONOMOUS_ACTION_TYPES


def get_default_workflow_stage(agent_id: str) -> str:
    return AGENT_DEFAULT_WORKFLOW_STAGE.get(str(agent_id or "").strip(), "content_generation")


def registry_summary() -> Dict[str, object]:
    return {
        "success": True,
        "safe_generation_workflow_stage_count": len(SAFE_GENERATION_WORKFLOW_STAGES),
        "safe_generation_action_type_count": len(SAFE_GENERATION_ACTION_TYPES),
        "real_world_owner_approval_action_count": len(REAL_WORLD_ACTION_TYPES_REQUIRING_OWNER_APPROVAL),
        "prohibited_autonomous_action_count": len(PROHIBITED_AUTONOMOUS_ACTION_TYPES),
        "agent_default_workflow_count": len(AGENT_DEFAULT_WORKFLOW_STAGE),
    }
''',
encoding="utf-8",
)

# Patch workflow engine unknown-stage rejection into safe-generation acceptance.
if workflow_path.exists():
    text = workflow_path.read_text(encoding="utf-8")

    if "from backend.app.core.governance_execution_registry import is_safe_generation_workflow_stage" not in text:
        text = text.replace(
            "from typing import",
            "from backend.app.core.governance_execution_registry import is_safe_generation_workflow_stage\nfrom typing import",
            1,
        )

    old = '''            requires_owner_approval=True,
            client_safe=True,
            blocked_reason="Unknown workflow stage. Owner approval or admin review required.",
            workflow_notes=["Rejected by default because the workflow stage is not recognised."],
'''
    new = '''            requires_owner_approval=not is_safe_generation_workflow_stage(workflow_stage),
            client_safe=True,
            blocked_reason=None if is_safe_generation_workflow_stage(workflow_stage) else "Unknown workflow stage. Owner approval or admin review required.",
            workflow_notes=["Safe generation workflow accepted."] if is_safe_generation_workflow_stage(workflow_stage) else ["Rejected by default because the workflow stage is not recognised."],
'''
    if old in text:
        text = text.replace(old, new)

    workflow_path.write_text(text, encoding="utf-8")

# Patch approval gateway unknown action rejection into safe-generation approval.
if approval_path.exists():
    text = approval_path.read_text(encoding="utf-8")

    if "from backend.app.core.governance_execution_registry import is_safe_generation_action_type, is_prohibited_autonomous_action" not in text:
        text = text.replace(
            "from typing import",
            "from backend.app.core.governance_execution_registry import is_safe_generation_action_type, is_prohibited_autonomous_action\nfrom typing import",
            1,
        )

    marker = "    def evaluate_action("
    if marker in text and "is_safe_generation_action_type(action_type)" not in text:
        insert_after = text.find(":", text.find(marker)) + 1
        injection = '''
        if is_prohibited_autonomous_action(action_type):
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
'''
        text = text[:insert_after] + injection + text[insert_after:]

    approval_path.write_text(text, encoding="utf-8")

test_path = root / "test_step13_governance_execution_registry.py"
test_path.write_text(
'''import requests

from backend.app.core.governance_execution_registry import (
    registry_summary,
    get_default_workflow_stage,
)

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

print("GOVERNANCE_REGISTRY_SUMMARY", registry_summary())

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

    response = requests.post(f"{BASE_URL}/run-agent", json=payload, headers=headers, timeout=90)

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

print("STEP_13_EXECUTION_CERTIFICATION_RESULTS")
print("PASSED_COUNT", len(passed))
print("FAILED_COUNT", len(failed))

if failed:
    print("FAILED_DETAILS")
    for item in failed:
        print(item)

if not failed:
    print("STEP_13_ALL_25_AGENTS_EXECUTION_READY")
''',
encoding="utf-8",
)

print("STEP_13_GOVERNANCE_EXECUTION_REGISTRY_INSTALLED")
print(f"Created: {registry_path}")
print(f"Created: {test_path}")
print("Backups created in backups folder.")