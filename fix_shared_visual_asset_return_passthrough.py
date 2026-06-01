from pathlib import Path

p = Path("backend/app/runtime/action_adapter_execution_layer.py")
text = p.read_text(encoding="utf-8")

old = '''    return {
        "success": True,
        "execution_id": execution_id,
        "adapter": adapter,
'''

new = '''    visual_preview_url = visual_asset.get("preview_url") if visual_asset else ""
    visual_asset_url = visual_asset.get("asset_url") if visual_asset else ""
    visual_media_url = visual_asset.get("media_url") if visual_asset else ""
    visual_generated_files = visual_asset.get("generated_files", []) if visual_asset else []
    visual_provider = visual_asset.get("provider") if visual_asset else None
    visual_provider_live_generation = visual_asset.get("provider_live_generation") if visual_asset else False
    visual_fallback_used = visual_asset.get("fallback_used") if visual_asset else False

    return {
        "success": True,
        "execution_id": execution_id,
        "adapter": adapter,
'''

if old not in text:
    raise SystemExit("generic return block not found")

text = text.replace(old, new, 1)

old2 = '''        "live_external_call_executed": bool(real_external_result and real_external_result.get("live_external_call_executed")),
        "external_readiness": external_readiness,
'''

new2 = '''        "live_external_call_executed": bool(real_external_result and real_external_result.get("live_external_call_executed")) or bool(visual_provider_live_generation),
        "preview_url": visual_preview_url,
        "asset_url": visual_asset_url,
        "media_url": visual_media_url,
        "generated_files": visual_generated_files,
        "provider": visual_provider,
        "provider_live_generation": visual_provider_live_generation,
        "fallback_used": visual_fallback_used,
        "external_readiness": external_readiness,
'''

if old2 not in text:
    raise SystemExit("return passthrough anchor not found")

text = text.replace(old2, new2, 1)

p.write_text(text, encoding="utf-8")
print("SHARED_VISUAL_ASSET_RETURN_PASSTHROUGH_FIXED")