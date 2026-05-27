from pathlib import Path

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
MAIN = ROOT / "backend" / "app" / "main.py"

text = MAIN.read_text(encoding="utf-8")

text = text.replace(
    '''    actor_role: str = "client"
    requested_credits: int = 1
    actor_role: str = "client"
    requested_credits: int = 1''',
    '''    actor_role: str = "client"
    requested_credits: int = 1''',
)

MAIN.write_text(text, encoding="utf-8")

print("STEP_190_CLEAN_RUN_AGENT_REQUEST_DUPLICATES_INSTALLED")
print("STEP_190_OK")