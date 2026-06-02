from pathlib import Path

p = Path("backend/app/runtime/action_adapter_execution_layer.py")
text = p.read_text(encoding="utf-8")

bad = '''    if assigned_agent == "ugc_creative_agent" or "ugc" in text or "shot-by-shot" in text or "creator casting" in text or "video concept" in text or "voiceover" in text:
        return "ugc_creative_deliverable_adapter"
    assigned_agent = str(packet.get("assigned_agent") or packet.get("recommended_agent") or "").strip()

'''

if bad not in text:
    raise SystemExit("UGC hijack block not found")

text = text.replace(bad, "", 1)

p.write_text(text, encoding="utf-8")
print("UGC_KEYWORD_HIJACK_REMOVED_AGENT_PRIORITY_PRESERVED")