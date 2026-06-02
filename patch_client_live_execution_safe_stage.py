from pathlib import Path

p = Path("backend/app/core/governance_execution_registry.py")
text = p.read_text(encoding="utf-8")

old = '''SAFE_GENERATION_WORKFLOW_STAGES = {'''

new = '''SAFE_GENERATION_WORKFLOW_STAGES = {
    "client_live_execution",
'''

if old not in text:
    raise SystemExit("SAFE_GENERATION_WORKFLOW_STAGES anchor not found")

text = text.replace(old, new, 1)

p.write_text(text, encoding="utf-8")

print("CLIENT_LIVE_EXECUTION_SAFE_STAGE_ADDED")