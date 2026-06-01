from pathlib import Path

p = Path("backend/app/runtime/action_adapter_execution_layer.py")
text = p.read_text(encoding="utf-8")

start_marker = '    \n    if adapter == "ugc_creative_deliverable_adapter":\n        visual_asset = generate_ugc_visual_asset('
mid_marker = '\nif adapter == "ugc_creative_deliverable_adapter":\n        media_plan = create_media_generation_plan('

start = text.find(start_marker)
mid = text.find(mid_marker)

if start == -1 or mid == -1:
    raise SystemExit(f"Markers not found. start={start}, mid={mid}")

# Remove the bad first visual-only block, and restore indentation on the real UGC block.
text = text[:start] + '\n    if adapter == "ugc_creative_deliverable_adapter":\n        media_plan = create_media_generation_plan(' + text[mid + len(mid_marker):]

# Add visual asset generation after media_plan block if not already inside the kept block.
needle = '''        )
        ugc_output = _generate_ugc_creative_deliverable(str(packet.get("user_requested_task") or action_text))
'''

replacement = '''        )
        visual_asset = generate_ugc_visual_asset(
            prompt=str(packet.get("user_requested_task") or action_text),
            tenant_id=tenant_id,
        )
        ugc_output = _generate_ugc_creative_deliverable(str(packet.get("user_requested_task") or action_text))
'''

if "visual_asset = generate_ugc_visual_asset(" not in text[text.find('    if adapter == "ugc_creative_deliverable_adapter":'):text.find("    real_external_result = None")]:
    text = text.replace(needle, replacement, 1)

# Add URL fields to return payload if missing.
payload_needle = '''            "media_generation_plan": media_plan,
            "output": ugc_output,
'''

payload_replacement = '''            "media_generation_plan": media_plan,
            "preview_url": visual_asset.get("preview_url"),
            "asset_url": visual_asset.get("asset_url"),
            "media_url": visual_asset.get("media_url"),
            "generated_files": visual_asset.get("generated_files", []),
            "output": ugc_output,
'''

if '"asset_url": visual_asset.get("asset_url")' not in text:
    text = text.replace(payload_needle, payload_replacement, 1)

text = text.replace('"download_ready": False,', '"download_ready": True,', 1)

p.write_text(text, encoding="utf-8")
print("UGC_DUPLICATE_BLOCK_REPAIRED")