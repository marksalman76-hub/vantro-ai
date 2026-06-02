from pathlib import Path

p = Path("backend/app/runtime/action_adapter_execution_layer.py")
lines = p.read_text(encoding="utf-8").splitlines()

start = None
end = None

for i, line in enumerate(lines):
    if line.strip() == "creative_visual_adapter_agents = {":
        start = i
        continue
    if start is not None and i > start and line.strip() == "}":
        end = i
        break

if start is None or end is None:
    raise SystemExit("creative_visual_adapter_agents block not found")

replacement = [
    '    creative_visual_adapter_agents = {',
    '        "product_image_agent",',
    '        "paid_ads_agent",',
    '        "brand_strategy_agent",',
    '        "marketing_specialist_agent",',
    '        "social_media_manager_content_creator_agent",',
    '        "influencer_collaboration_agent",',
    '    }',
]

lines = lines[:start] + replacement + lines[end + 1:]
p.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("CREATIVE_VISUAL_AGENT_SET_REPAIRED")