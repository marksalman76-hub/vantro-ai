from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
TARGET_FILE = PROJECT_ROOT / ".env.example"

BACKUP_DIR = PROJECT_ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

if TARGET_FILE.exists():
    backup_file = BACKUP_DIR / f"env_example_before_step86_{timestamp}.txt"
    original = TARGET_FILE.read_text(encoding="utf-8")
    backup_file.write_text(original, encoding="utf-8")
else:
    backup_file = None
    original = ""

block = """
# ============================================================
# Live LLM Provider Configuration
# ============================================================
# SECURITY RULES:
# - Never commit real API keys.
# - Never expose provider keys in the client UI.
# - Keep live execution disabled until owner approval is complete.
# - ENABLE_LIVE_LLM_CALLS must stay false unless deliberately testing live provider calls.

OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GOOGLE_API_KEY=
XAI_API_KEY=
LOCAL_LLM_ENDPOINT=

# Accepted live values: 1, true, yes, enabled
ENABLE_LIVE_LLM_CALLS=false
"""

if "ENABLE_LIVE_LLM_CALLS" in original or "OPENAI_API_KEY" in original:
    print("STEP_86_ENV_EXAMPLE_LIVE_LLM_CONFIG_ALREADY_PRESENT")
    if backup_file:
        print(f"Backup created: {backup_file}")
else:
    updated = original.rstrip() + "\n\n" + block.strip() + "\n"
    TARGET_FILE.write_text(updated, encoding="utf-8")
    print("STEP_86_ENV_EXAMPLE_LIVE_LLM_CONFIG_INSTALLED")
    if backup_file:
        print(f"Backup created: {backup_file}")
    print(f"Updated: {TARGET_FILE}")