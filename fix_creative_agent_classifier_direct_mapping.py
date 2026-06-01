from pathlib import Path

p = Path("backend/app/runtime/action_adapter_execution_layer.py")
text = p.read_text(encoding="utf-8")

anchor = '''    if assigned_agent == "ugc_creative_agent" or "ugc" in text or "shot-by-shot" in text or "creator casting" in text or "video concept" in text:
        return "ugc_creative_deliverable_adapter"
'''

replacement = '''    if assigned_agent == "ugc_creative_agent" or "ugc" in text or "shot-by-shot" in text or "creator casting" in text or "video concept" in text:
        return "ugc_creative_deliverable_adapter"

    if assigned_agent == "paid_ads_agent":
        return "ads_campaign_draft_adapter"

    if assigned_agent == "product_image_agent":
        return "product_image_adapter"

    if assigned_agent == "brand_strategy_agent":
        return "strategy_document_adapter"

    if assigned_agent == "marketing_specialist_agent":
        return "marketing_asset_adapter"

    if assigned_agent == "social_media_manager_content_creator_agent":
        return "marketing_asset_adapter"
'''

if anchor not in text:
    raise SystemExit("anchor not found")

text = text.replace(anchor, replacement, 1)

p.write_text(text, encoding="utf-8")
print("CREATIVE_AGENT_CLASSIFIER_DIRECT_MAPPING_FIXED")