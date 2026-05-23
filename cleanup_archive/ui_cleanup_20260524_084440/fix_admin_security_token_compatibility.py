from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent
TARGET = ROOT / "backend" / "app" / "core" / "security_audit_enforcement_runtime.py"
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

backup = BACKUPS / f"security_audit_before_admin_token_compat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"

s = TARGET.read_text(encoding="utf-8", errors="ignore")
backup.write_text(s, encoding="utf-8")

old = '''def _admin_token_valid(request: Request) -> bool:
    expected = os.getenv("ADMIN_PLATFORM_TOKEN", "") or os.getenv("ADMIN_AUTH_SECRET", "")
    if not expected:
        return not _is_production()

    supplied = _header(request, "x-admin-token") or _header(request, "authorization").replace("Bearer ", "")
    if not supplied:
        return False

    return hmac.compare_digest(str(supplied), str(expected))'''

new = '''def _admin_token_valid(request: Request) -> bool:
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

    return any(hmac.compare_digest(str(supplied), expected) for expected in expected_tokens)'''

if old not in s:
    raise SystemExit("TARGET_BLOCK_NOT_FOUND")

s = s.replace(old, new)

TARGET.write_text(s, encoding="utf-8")

print("ADMIN_SECURITY_TOKEN_COMPATIBILITY_FIXED")
print(f"Backup: {backup}")
print("BACKEND_SECURITY_COMPATIBILITY_ONLY")