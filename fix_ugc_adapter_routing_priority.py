from pathlib import Path

p = Path("backend/app/runtime/real_action_execution_bridge.py")
text = p.read_text(encoding="utf-8")

old = '''    if "product description" in raw or "product copy" in raw or assigned_agent == "product_copywriting_agent":
        return "product_copywriting"

    if "email" in raw:
        return "create_email_draft"
'''

new = '''    if (
        assigned_agent == "ugc_creative_agent"
        or "ugc" in raw
        or "creator" in raw
        or "shot-by-shot" in raw
        or "video concept" in raw
        or "media generation" in raw
        or "ugc script" in raw
    ):
        return "ugc_creative_deliverable"

    if "product description" in raw or "product copy" in raw or assigned_agent == "product_copywriting_agent":
        return "product_copywriting"

    if "email" in raw:
        return "create_email_draft"
'''

text = text.replace(old, new)

old2 = '''    "product_copywriting": "product_copywriting_adapter",
}'''

new2 = '''    "product_copywriting": "product_copywriting_adapter",
    "ugc_creative_deliverable": "ugc_creative_deliverable_adapter",
}'''

text = text.replace(old2, new2)

p.write_text(text, encoding="utf-8")

print("UGC_ADAPTER_ROUTING_PRIORITY_FIXED")