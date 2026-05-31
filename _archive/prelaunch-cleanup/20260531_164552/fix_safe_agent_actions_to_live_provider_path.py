from pathlib import Path
from datetime import datetime

path = Path("backend/app/main.py")
text = path.read_text(encoding="utf-8")

backup_dir = Path("backups") / ("safe_agent_actions_live_provider_path_before_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
backup_dir.mkdir(parents=True, exist_ok=True)
backup = backup_dir / "main.py"
backup.write_text(text, encoding="utf-8")

old = '''ACTION_TO_EXECUTION_MAP: Dict[str, str] = {
    "ugc_script_generation": "create_ugc_video_brief",
    "product_image_generation": "create_product_image_brief",
    "product_image_direction": "create_product_image_brief",
    "ad_copy_generation": "create_ad_copy_brief",
    "website_content_generation": "create_landing_page_brief",
    "product_copy_generation": "create_shopify_product_page",
    "influencer_shortlist": "prepare_influencer_outreach",
    "influencer_outreach_draft": "prepare_influencer_outreach",
    "customer_support_reply": "prepare_customer_support_reply",
    "analytics_report": "prepare_analytics_report",
    "scale_campaign": "scale_campaign",
    "launch_paid_campaign": "launch_paid_campaign",
    "increase_ad_spend": "increase_ad_spend",
    "change_campaign_budget": "change_campaign_budget",
    "paid_influencer_collaboration": "paid_influencer_collaboration",
    "commission_agreement": "commission_agreement",
    "usage_rights_contract": "usage_rights_contract",
    "large_supplier_order": "large_supplier_order",
    "large_refund_batch": "large_refund_batch",
    "major_strategy_change": "major_strategy_change",
}
'''

new = '''ACTION_TO_EXECUTION_MAP: Dict[str, str] = {
    # Safe generation actions must use the canonical governed live provider path.
    "general_ecommerce_agent_output": "governed_live_provider_generation",
    "marketing_campaign_execution": "governed_live_provider_generation",
    "content_generation": "governed_live_provider_generation",
    "ugc_script_generation": "governed_live_provider_generation",
    "product_image_generation": "governed_live_provider_generation",
    "product_image_direction": "governed_live_provider_generation",
    "ad_copy_generation": "governed_live_provider_generation",
    "website_content_generation": "governed_live_provider_generation",
    "product_copy_generation": "governed_live_provider_generation",
    "influencer_shortlist": "governed_live_provider_generation",
    "influencer_outreach_draft": "governed_live_provider_generation",
    "customer_support_reply": "governed_live_provider_generation",
    "analytics_report": "governed_live_provider_generation",
    "seo_strategy": "governed_live_provider_generation",
    "business_growth": "governed_live_provider_generation",
    "crm_strategy": "governed_live_provider_generation",
    "billing_optimisation": "governed_live_provider_generation",
    "training_learning": "governed_live_provider_generation",
    "qa_testing": "governed_live_provider_generation",
    "security_compliance": "governed_live_provider_generation",
    "integration_automation": "governed_live_provider_generation",
    "orchestration": "governed_live_provider_generation",
    "website_app_build": "governed_live_provider_generation",
    "analytics_intelligence": "governed_live_provider_generation",

    # Sensitive/high-authority actions remain owner-gated.
    "scale_campaign": "scale_campaign",
    "launch_paid_campaign": "launch_paid_campaign",
    "increase_ad_spend": "increase_ad_spend",
    "change_campaign_budget": "change_campaign_budget",
    "paid_influencer_collaboration": "paid_influencer_collaboration",
    "commission_agreement": "commission_agreement",
    "usage_rights_contract": "usage_rights_contract",
    "large_supplier_order": "large_supplier_order",
    "large_refund_batch": "large_refund_batch",
    "major_strategy_change": "major_strategy_change",
}
'''

if old not in text:
    raise SystemExit("TARGET_BLOCK_NOT_FOUND")

path.write_text(text.replace(old, new), encoding="utf-8")

print("SAFE_AGENT_ACTIONS_TO_LIVE_PROVIDER_PATH_PATCHED")
print("Backup:", backup)