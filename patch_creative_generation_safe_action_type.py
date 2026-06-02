from pathlib import Path

p = Path("backend/app/core/governance_execution_registry.py")
text = p.read_text(encoding="utf-8")

old = '''SAFE_GENERATION_ACTION_TYPES = {'''

new = '''SAFE_GENERATION_ACTION_TYPES = {
    "creative_generation",
'''

if old not in text:
    raise SystemExit("SAFE_GENERATION_ACTION_TYPES anchor not found")

if '"creative_generation"' not in text:
    text = text.replace(old, new, 1)

p.write_text(text, encoding="utf-8")
print("CREATIVE_GENERATION_SAFE_ACTION_TYPE_ADDED")