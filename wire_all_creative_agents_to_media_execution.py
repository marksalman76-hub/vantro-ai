from pathlib import Path
from datetime import datetime

root = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
path = root / "backend" / "app" / "runtime" / "real_action_execution_bridge.py"

text = path.read_text(encoding="utf-8")

backup_dir = root / "backups" / f"real_action_bridge_before_all_creative_media_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)
(backup_dir / "real_action_execution_bridge.py").write_text(text, encoding="utf-8")

# Add full creative team mapping after SAFE_ACTION_ADAPTERS.
marker = '''SAFE_ACTION_ADAPTERS = {
    "create_marketing_asset": "marketing_asset_adapter",
    "create_sales_asset": "sales_asset_adapter",
    "create_email_draft": "email_draft_adapter",
    "create_content_calendar": "content_calendar_adapter",
    "create_research_summary": "research_summary_adapter",
    "create_strategy_document": "strategy_document_adapter",
    "create_client_deliverable": "client_deliverable_adapter",
    "prepare_outreach_draft": "outreach_draft_adapter",
    "prepare_implementation_checklist": "implementation_checklist_adapter",
    "website_draft_page": "website_draft_page_adapter",
    "ads_campaign_draft": "ads_campaign_draft_adapter",
    "seo_content_plan": "seo_deliverable_adapter",
    "store_draft_update": "store_draft_update_adapter",
    "product_copywriting": "product_copywriting_adapter",
    "ugc_creative_deliverable": "ugc_creative_deliverable_adapter",
}
'''

replacement = marker + '''

CREATIVE_MEDIA_AGENT_IDS = {
    "ugc_creative_agent",
    "paid_ads_agent",
    "product_image_agent",
    "social_media_manager_content_creator_agent",
    "brand_strategy_agent",
    "marketing_specialist_agent",
    "website_landing_apps_agent",
    "influencer_collaboration_agent",
    "creative_rotation_agent",
    "product_development_agent",
    "ecommerce_agent",
}

CREATIVE_MEDIA_INTENT_KEYWORDS = {
    "actual video",
    "generate video",
    "create video",
    "video ad",
    "ugc video",
    "short-form video",
    "reels",
    "tiktok",
    "voiceover",
    "audio",
    "avatar",
    "lip sync",
    "lipsync",
    "image asset",
    "product image",
    "creative asset",
    "media asset",
    "runway",
    "kling",
    "heygen",
    "elevenlabs",
    "visual",
    "ad creative",
    "campaign creative",
}
'''

if "CREATIVE_MEDIA_AGENT_IDS" not in text:
    if marker not in text:
        raise SystemExit("SAFE_ACTION_ADAPTERS marker not found.")
    text = text.replace(marker, replacement)

# Add helper before _normalise_action_type.
helper_marker = "def _normalise_action_type(packet: Dict[str, Any]) -> str:"
helper = '''def _is_creative_media_agent_or_request(packet: Dict[str, Any]) -> bool:
    assigned_agent = str(packet.get("assigned_agent") or packet.get("recommended_agent") or packet.get("agent") or "").strip().lower()

    raw = " ".join(
        str(packet.get(key, ""))
        for key in [
            "action_type",
            "implementation_action",
            "action",
            "title",
            "description",
            "user_requested_task",
            "task",
            "recommended_agent",
            "assigned_agent",
            "agent",
        ]
    ).lower().replace("_", " ")

    if assigned_agent in CREATIVE_MEDIA_AGENT_IDS:
        return True

    return any(keyword in raw for keyword in CREATIVE_MEDIA_INTENT_KEYWORDS)


'''

if "_is_creative_media_agent_or_request" not in text:
    if helper_marker not in text:
        raise SystemExit("_normalise_action_type marker not found.")
    text = text.replace(helper_marker, helper + helper_marker)

# Insert creative-team routing near top of _normalise_action_type, after assigned_agent line.
old = '''    assigned_agent = str(packet.get("assigned_agent") or packet.get("recommended_agent") or "").strip().lower()

    if "website draft page" in raw or "landing page" in raw or assigned_agent == "website_landing_apps_agent":
        return "website_draft_page"
'''

new = '''    assigned_agent = str(packet.get("assigned_agent") or packet.get("recommended_agent") or "").strip().lower()

    if _is_creative_media_agent_or_request(packet):
        return "ugc_creative_deliverable"

    if "website draft page" in raw or "landing page" in raw or assigned_agent == "website_landing_apps_agent":
        return "website_draft_page"
'''

if old not in text:
    raise SystemExit("assigned_agent routing block not found.")
text = text.replace(old, new)

path.write_text(text, encoding="utf-8")

print("ALL_CREATIVE_AGENTS_ROUTED_TO_MEDIA_EXECUTION")
print("Backup:", backup_dir)