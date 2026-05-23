from pathlib import Path
from datetime import datetime
import re

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
MAIN = ROOT / "backend" / "app" / "main.py"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

text = MAIN.read_text(encoding="utf-8")

backup = BACKUP_DIR / f"main_before_admin_token_function_repair_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
backup.write_text(text, encoding="utf-8")

replacement = '''def _admin_token_valid(request: Request) -> bool:
    expected_tokens = [
        os.getenv("ADMIN_PLATFORM_TOKEN", ""),
        os.getenv("ADMIN_AUTH_SECRET", ""),
        os.getenv("ADMIN_AUTH_TOKEN", ""),
    ]
    expected_tokens = [str(token).strip() for token in expected_tokens if str(token).strip()]

    if not expected_tokens:
        return not _is_production()

    supplied = (
        _header(request, "x-admin-token")
        or _header(request, "authorization").replace("Bearer ", "")
    ).strip()

    if not supplied:
        return False

    return any(hmac.compare_digest(str(supplied), expected) for expected in expected_tokens)


def _is_admin_path(path: str) -> bool:
'''

pattern = r"def _admin_token_valid\(request: Request\) -> bool:.*?def _is_admin_path\(path: str\) -> bool:\n"

new_text, count = re.subn(pattern, replacement, text, count=1, flags=re.DOTALL)

if count != 1:
    raise SystemExit("ADMIN_TOKEN_FUNCTION_REPAIR_FAILED: target block not found")

MAIN.write_text(new_text, encoding="utf-8")

print("ADMIN_TOKEN_FUNCTION_REPAIRED")
print(f"Backup: {backup}")