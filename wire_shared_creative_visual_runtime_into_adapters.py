from pathlib import Path

p = Path("backend/app/runtime/action_adapter_execution_layer.py")
text = p.read_text(encoding="utf-8")

if "from backend.app.runtime.shared_creative_visual_generation_runtime import generate_creative_visual_asset" not in text:
    text = text.replace(
        "from backend.app.runtime.ugc_visual_generation_runtime import generate_ugc_visual_asset\n",
        "from backend.app.runtime.ugc_visual_generation_runtime import generate_ugc_visual_asset\nfrom backend.app.runtime.shared_creative_visual_generation_runtime import generate_creative_visual_asset\n",
        1,
    )

# Add visual generation to common creative adapters after adapter/action_text are available.
target = '''    real_external_result = None
    media_plan = None
'''

insert = '''    creative_visual_adapter_agents = {
        "product_image_agent",
        "paid_ads_agent",
        "brand_strategy_agent",
        "marketing_specialist_agent",
        "social_media_manager_content_creator_agent",
    }

    if assigned_agent in creative_visual_adapter_agents and adapter in {
        "marketing_asset_adapter",
        "ads_campaign_draft_adapter",
        "client_deliverable_adapter",
        "product_image_adapter",
        "strategy_document_adapter",
    }:
        visual_asset = generate_creative_visual_asset(
            prompt=str(packet.get("user_requested_task") or action_text),
            agent_id=assigned_agent,
            tenant_id=tenant_id,
            asset_kind=f"{assigned_agent}_visual_asset",
        )
    else:
        visual_asset = None

    real_external_result = None
    media_plan = None
'''

if "creative_visual_adapter_agents" not in text:
    text = text.replace(target, insert, 1)

# Ensure generic return payloads can include visual asset fields where visual_asset exists.
old = '''    return {
        "success": True,
        "execution_id": execution_id,
        "adapter": adapter,
'''

new = '''    visual_preview_url = visual_asset.get("preview_url") if visual_asset else ""
    visual_asset_url = visual_asset.get("asset_url") if visual_asset else ""
    visual_media_url = visual_asset.get("media_url") if visual_asset else ""
    visual_generated_files = visual_asset.get("generated_files", []) if visual_asset else []

    return {
        "success": True,
        "execution_id": execution_id,
        "adapter": adapter,
'''

if "visual_preview_url = visual_asset.get" not in text:
    text = text.replace(old, new, 1)

old2 = '''        "output": output,
        "asset": {'''

new2 = '''        "preview_url": visual_preview_url,
        "asset_url": visual_asset_url,
        "media_url": visual_media_url,
        "generated_files": visual_generated_files,
        "output": output,
        "asset": {'''

if '"preview_url": visual_preview_url' not in text:
    text = text.replace(old2, new2, 1)

p.write_text(text, encoding="utf-8")
print("SHARED_CREATIVE_VISUAL_RUNTIME_WIRED_INTO_ADAPTERS")