from pathlib import Path

p = Path("backend/app/approval/owner_approval_gateway.py")
text = p.read_text(encoding="utf-8")

# Add creative_generation beside known safe/approved generation actions.
if '"creative_generation"' not in text:
    text = text.replace(
        'SAFE_ACTIONS = {',
        'SAFE_ACTIONS = {\n    "creative_generation",',
        1,
    )

p.write_text(text, encoding="utf-8")
print("CREATIVE_GENERATION_APPROVAL_RULE_PATCHED")