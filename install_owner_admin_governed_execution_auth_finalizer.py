from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent
SESSION_FILE = ROOT / "backend" / "app" / "core" / "session_auth_hardening_runtime.py"
BACKUP = ROOT / "backups" / f"owner_admin_governed_execution_auth_finalizer_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

def main():
    text = SESSION_FILE.read_text(encoding="utf-8", errors="replace")

    if "owner_admin_governed_execution_auth_finalized" in text:
        print("OWNER_ADMIN_GOVERNED_EXECUTION_AUTH_FINALIZER_ALREADY_PRESENT")
        return

    marker = '''    if reasons:
        severity = severity if severity != "none" else "low"
'''

    replacement = '''    owner_admin_governed_execution_authorised = (
        is_governed_execution_path
        and is_owner_admin_actor
        and bool(auth or admin_token)
    )

    if owner_admin_governed_execution_authorised and blocked:
        allowed_reasons = {
            "csrf_token_or_origin_missing_for_state_change",
            "possible_replay_request_detected",
            "owner_admin_governed_execution_csrf_bypass_applied",
        }
        if set(reasons).issubset(allowed_reasons):
            reasons.append("owner_admin_governed_execution_auth_finalized")
            severity = "medium" if severity == "none" else severity
            blocked = False

    if reasons:
        severity = severity if severity != "none" else "low"
'''

    if marker not in text:
        raise RuntimeError("Final reasons block marker not found")

    BACKUP.mkdir(parents=True, exist_ok=True)
    (BACKUP / SESSION_FILE.name).write_text(text, encoding="utf-8")

    SESSION_FILE.write_text(text.replace(marker, replacement, 1), encoding="utf-8")

    print("OWNER_ADMIN_GOVERNED_EXECUTION_AUTH_FINALIZER_INSTALLED")
    print("Backup:", BACKUP)
    print("Updated:", SESSION_FILE)

if __name__ == "__main__":
    main()