from pathlib import Path
import re

p = Path("backend/app/runtime/action_adapter_execution_layer.py")
text = p.read_text(encoding="utf-8")

text = re.sub(
    r'assigned_agent = str\(packet\.get\("assigned_agent"\) or packet\.get\("agent"\) or packet\.get\("recommended_agent"\) or ""\)\.strip\(\)\\n\\n\s*creative_visual_adapter_agents = \{',
    'assigned_agent = str(packet.get("assigned_agent") or packet.get("agent") or packet.get("recommended_agent") or "").strip()\n\n    creative_visual_adapter_agents = {',
    text,
    count=1,
)

p.write_text(text, encoding="utf-8")
print("LITERAL_BACKSLASH_NEWLINES_REMOVED")