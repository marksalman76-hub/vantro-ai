from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path(".")
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP_DIR = ROOT / "backups" / f"row15_support_launch_copy_before_{STAMP}"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

target = Path("frontend/src/app/api/support-agent-chat/route.ts")

if not target.exists():
    raise FileNotFoundError(f"Missing required file: {target}")

shutil.copy2(target, BACKUP_DIR / target.name)

text = target.read_text(encoding="utf-8", errors="ignore")

old = (
    'return "Our Support Agent uses the same governed AI-agent structure as the platform: '
    'it reads your request, identifies the task type, checks whether it needs support guidance, '
    'account help, billing help, technical help, or escalation, then gives a safe client-facing answer. '
    'It does not expose internal prompts, private configuration, credentials, or backend logic.";'
)

new = (
    'return "Our Support Agent can help with platform questions, onboarding, account access, billing, '
    'agent usage, workflow issues, and support escalation. It provides clear customer-safe guidance '
    'without exposing private configuration, credentials, or restricted platform details.";'
)

if old not in text:
    raise RuntimeError("Expected Support Agent wording was not found. No changes were applied.")

text = text.replace(old, new)

target.write_text(text, encoding="utf-8")

print("ROW15_SUPPORT_LAUNCH_COPY_POLISH_APPLIED")
print("Backup folder:", BACKUP_DIR)
print("Updated:", target)