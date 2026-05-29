from pathlib import Path
from datetime import datetime

path = Path("backend/app/core/security_audit_enforcement_runtime.py")
text = path.read_text(encoding="utf-8")

backup_dir = Path("backups") / ("admin_security_token_validation_before_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
backup_dir.mkdir(parents=True, exist_ok=True)
backup = backup_dir / "security_audit_enforcement_runtime.py"
backup.write_text(text, encoding="utf-8")

old = '''def _admin_token_valid(request: Request) -> bool:
    expected = os.getenv("ADMIN_PLATFORM_TOKEN", "") or os.getenv("ADMIN_AUTH_SECRET", "")
    if not expected:
        return not _is_production()

    supplied = _header(request, "x-admin-token") or _header(request, "authorization").replace("Bearer ", "")
    if not supplied:
        return False

    return hmac.compare_digest(str(supplied), str(expected))
'''

new = '''def _admin_token_valid(request: Request) -> bool:
    expected_values = [
        os.getenv("ADMIN_PLATFORM_TOKEN", ""),
        os.getenv("ADMIN_AUTH_SECRET", ""),
        os.getenv("ADMIN_TOKEN", ""),
        os.getenv("PLATFORM_ADMIN_TOKEN", ""),
        os.getenv("OWNER_ADMIN_TOKEN", ""),
    ]
    expected_tokens = [str(value).strip().strip(chr(34)).strip(chr(39)) for value in expected_values if str(value).strip()]

    if not expected_tokens:
        return not _is_production()

    supplied = _header(request, "x-admin-token") or _header(request, "authorization").replace("Bearer ", "")
    supplied = str(supplied).strip().strip(chr(34)).strip(chr(39))

    if not supplied:
        return False

    return any(hmac.compare_digest(supplied, expected) for expected in expected_tokens)
'''

if old not in text:
    raise SystemExit("TARGET_BLOCK_NOT_FOUND")

path.write_text(text.replace(old, new), encoding="utf-8")

print("ADMIN_SECURITY_TOKEN_VALIDATION_PATCHED")
print("Backup:", backup)