from pathlib import Path
from datetime import datetime
import shutil
import re

p = Path("frontend/src/app/admin/page.tsx")
backup = Path("backups") / f"admin_main_live_execution_rendering_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup.mkdir(parents=True, exist_ok=True)
shutil.copy2(p, backup / "page.tsx")

s = p.read_text(encoding="utf-8")

replacements = {
    '["strategy_agent", "Strategy Agent"]': '["strategist_agent", "Strategist Agent"]',
    '["business_growth_agent", "Business Growth Agent"]': '["business_growth_partnerships_agent", "Business Growth Agent"]',
    '["lead_generation_agent", "Lead Generation Agent"]': '["lead_generator_appointment_setter_agent", "Lead Generation Agent"]',
    '["social_media_manager_agent", "Social Media Manager Agent"]': '["social_media_manager_content_creator_agent", "Social Media Manager Agent"]',
    '["content_creator_agent", "Content Creator Agent"]': '["social_media_manager_content_creator_agent", "Content Creator Agent"]',
    '["ad_creative_agent", "Ad Creative Agent"]': '["paid_ads_agent", "Ad Creative Agent"]',
    '["crm_agent", "CRM Agent"]': '["crm_ai_agent", "CRM Agent"]',
    '["product_image_direction_agent", "Product Image Direction Agent"]': '["product_image_agent", "Product Image Direction Agent"]',
    '["website_landing_page_agent", "Website / Landing Page Agent"]': '["website_landing_apps_agent", "Website / Landing Page Agent"]',
}

for old, new in replacements.items():
    s = s.replace(old, new)

s = s.replace('useState<string[]>(["strategy_agent"])', 'useState<string[]>(["marketing_specialist_agent"])')

s = s.replace(
    'const allSucceeded = results.every((item) => item.success === true);',
    'const allSucceeded = results.every((item) => item.success === true && item.live_external_call_executed === true);'
)

s = s.replace("Admin execution needs review", "Live execution needs review")
s = s.replace("Admin execution completed", "Live execution completed")
s = s.replace("2 selected agent run(s) processed through the owner/admin path.", "Selected agent run(s) processed through the governed live provider path.")
s = s.replace("processed through the owner/admin path", "processed through the governed live provider path")
s = s.replace("The agent returned a governed result and is ready for", "The agent returned a live provider result and is ready for")

p.write_text(s, encoding="utf-8")

print("ADMIN_MAIN_LIVE_EXECUTION_RESULT_RENDERING_FIXED")
print(f"Backup: {backup}")
print(f"Updated: {p}")