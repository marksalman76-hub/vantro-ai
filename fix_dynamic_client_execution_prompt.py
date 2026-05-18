from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

client_page = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
text = client_page.read_text(encoding="utf-8", errors="ignore")

backup = BACKUPS / f"client_page_before_dynamic_execution_prompt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
backup.write_text(text, encoding="utf-8")

old_default = 'defaultValue="Create premium ecommerce campaign assets for this business using the saved business profile, active agents, and selected execution requirements."'
new_default = 'defaultValue="Create a client-specific premium deliverable using the saved business profile, selected active agents, current offer, target audience, goals, and execution requirements."'
text = text.replace(old_default, new_default)

old_payload_task = 'task: "Create premium ecommerce campaign assets for this business using the saved business profile, active agents, and selected execution requirements.",'
new_payload_task = 'task: "Create a client-specific premium deliverable using the saved business profile, selected active agents, current offer, target audience, goals, and execution requirements.",'
text = text.replace(old_payload_task, new_payload_task)

old_profile = '''business_profile: {
                            niche: "Client ecommerce business",
                            target_audience: "Target customers from the saved business profile",
                            positioning: "Commercial-grade client-specific campaign",
                          },'''

new_profile = '''business_profile: {
                            niche: "Saved client business profile",
                            target_audience: "Saved target audience and customer context",
                            positioning: "Client-specific commercial positioning and execution requirements",
                          },'''

text = text.replace(old_profile, new_profile)

if "Create premium ecommerce campaign assets for this business" in text:
    raise RuntimeError("Old hardcoded execution prompt still exists.")

client_page.write_text(text, encoding="utf-8")

print("DYNAMIC_CLIENT_EXECUTION_PROMPT_FIXED")
print(f"Backup: {backup}")