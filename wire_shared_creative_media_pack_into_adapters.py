from pathlib import Path

p = Path("backend/app/runtime/action_adapter_execution_layer.py")
text = p.read_text(encoding="utf-8")

if "from backend.app.runtime.shared_creative_media_generation_runtime import generate_creative_media_pack" not in text:
    text = text.replace(
        "from backend.app.runtime.shared_creative_visual_generation_runtime import generate_creative_visual_asset\n",
        "from backend.app.runtime.shared_creative_visual_generation_runtime import generate_creative_visual_asset\nfrom backend.app.runtime.shared_creative_media_generation_runtime import generate_creative_media_pack\n",
        1,
    )

old = '''    if assigned_agent in creative_visual_adapter_agents and adapter in {
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
'''

new = '''    if assigned_agent in creative_visual_adapter_agents and adapter in {
        "marketing_asset_adapter",
        "ads_campaign_draft_adapter",
        "client_deliverable_adapter",
        "product_image_adapter",
        "strategy_document_adapter",
    }:
        media_pack = generate_creative_media_pack(
            task=str(packet.get("user_requested_task") or action_text),
            agent_id=assigned_agent,
            tenant_id=tenant_id,
            include_image=True,
            include_audio=True,
            include_video=True,
            include_avatar=True,
        )
        visual_asset = (media_pack.get("image_assets") or [None])[0]
    else:
        media_pack = None
        visual_asset = None
'''

if old not in text:
    raise SystemExit("shared visual block not found")

text = text.replace(old, new, 1)

old2 = '''    visual_fallback_used = visual_asset.get("fallback_used") if visual_asset else False
'''

new2 = '''    visual_fallback_used = visual_asset.get("fallback_used") if visual_asset else False
    media_pack_payload = media_pack or {}
'''

text = text.replace(old2, new2, 1)

old3 = '''        "fallback_used": visual_fallback_used,
        "external_readiness": external_readiness,
'''

new3 = '''        "fallback_used": visual_fallback_used,
        "media_pack": media_pack_payload,
        "voiceover_script": media_pack_payload.get("voiceover_script", ""),
        "video_prompt": media_pack_payload.get("video_prompt", ""),
        "avatar_prompt": media_pack_payload.get("avatar_prompt", ""),
        "generation_jobs": media_pack_payload.get("generation_jobs", []),
        "provider_stack": media_pack_payload.get("provider_stack", {}),
        "provider_chain": media_pack_payload.get("provider_chain", []),
        "supports_audio": media_pack_payload.get("supports_audio", False),
        "supports_video": media_pack_payload.get("supports_video", False),
        "supports_avatar_video": media_pack_payload.get("supports_avatar_video", False),
        "external_readiness": external_readiness,
'''

if old3 not in text:
    raise SystemExit("media passthrough return anchor not found")

text = text.replace(old3, new3, 1)

p.write_text(text, encoding="utf-8")
print("SHARED_CREATIVE_MEDIA_PACK_WIRED_INTO_ADAPTERS")