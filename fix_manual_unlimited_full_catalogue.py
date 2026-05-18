from pathlib import Path
from datetime import datetime

TARGET = Path("backend/app/core/admin_deployment_control_runtime.py")

content = TARGET.read_text(encoding="utf-8")

backup_dir = Path("backups")
backup_dir.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

backup_file = backup_dir / f"admin_deployment_control_runtime_before_full_catalogue_{timestamp}.py"
backup_file.write_text(content, encoding="utf-8")

catalogue_block = '''
FULL_AGENT_CATALOGUE = [
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
    "website_landing_apps_agent",
    "product_development_agent",
    "ecommerce_agent",
    "ugc_creative_agent",
    "product_copywriting_agent",
    "product_image_agent",
    "influencer_collaboration_agent",
    "analytics_optimisation_agent",
    "orchestration_agent",
    "security_compliance_agent",
    "integration_automation_agent"
]

'''

if "FULL_AGENT_CATALOGUE" not in content:
    content = content.replace(
        'STATE_FILE = DATA_DIR / "admin_deployment_control_state.json"\n',
        'STATE_FILE = DATA_DIR / "admin_deployment_control_state.json"\n\n' + catalogue_block
    )

old_block = '''    active_agents = payload.get("active_agents") or payload.get("paid_agents") or []

    if not isinstance(active_agents, list):
        active_agents = []
'''

new_block = '''    active_agents = payload.get("active_agents") or payload.get("paid_agents") or []

    if not isinstance(active_agents, list):
        active_agents = []

    if package_name.lower() == "manual unlimited":
        active_agents = FULL_AGENT_CATALOGUE.copy()
'''

content = content.replace(old_block, new_block)

TARGET.write_text(content, encoding="utf-8")

print("MANUAL_UNLIMITED_FULL_CATALOGUE_FIXED")
print(f"Backup: {backup_file}")