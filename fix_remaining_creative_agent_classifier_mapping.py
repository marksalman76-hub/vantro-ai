from pathlib import Path

p = Path("backend/app/runtime/action_adapter_execution_layer.py")
text = p.read_text(encoding="utf-8")

anchor = '''    if assigned_agent == "social_media_manager_content_creator_agent":
        return "marketing_asset_adapter"

    if assigned_agent == "ugc_creative_agent" or "ugc" in text or "shot-by-shot" in text or "creator casting" in text or "video concept" in text:
        return "ugc_creative_deliverable_adapter"
'''

replacement = '''    if assigned_agent == "social_media_manager_content_creator_agent":
        return "marketing_asset_adapter"

    if assigned_agent == "website_landing_apps_agent":
        return "website_draft_page_adapter"

    if assigned_agent == "influencer_collaboration_agent":
        return "marketing_asset_adapter"

    if assigned_agent == "ugc_creative_agent" or "ugc" in text or "shot-by-shot" in text or "creator casting" in text or "video concept" in text:
        return "ugc_creative_deliverable_adapter"
'''

if anchor not in text:
    raise SystemExit("remaining creative mapping anchor not found")

text = text.replace(anchor, replacement, 1)

p.write_text(text, encoding="utf-8")
print("REMAINING_CREATIVE_AGENT_CLASSIFIER_MAPPING_FIXED")