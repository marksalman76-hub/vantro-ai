from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent
TARGET = ROOT / "backend" / "app" / "core" / "session_auth_hardening_runtime.py"
BACKUP = ROOT / "backups" / f"governed_owner_admin_replay_bypass_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

OLD = '''    if _check_replay(request):
        reasons.append("possible_replay_request_detected")
        severity = "high" if severity in {"none", "medium"} else severity
        if production:
            blocked = True
'''

NEW = '''    if _check_replay(request):
        if (
            is_governed_execution_path
            and is_owner_admin_actor
            and (auth or admin_token)
        ):
            reasons.append("owner_admin_governed_execution_replay_bypass_applied")
            severity = "medium" if severity == "none" else severity
        else:
            reasons.append("possible_replay_request_detected")
            severity = "high" if severity in {"none", "medium"} else severity
            if production:
                blocked = True
'''

def main():
    text = TARGET.read_text(encoding="utf-8", errors="replace")

    if "owner_admin_governed_execution_replay_bypass_applied" in text:
        print("GOVERNED_OWNER_ADMIN_REPLAY_BYPASS_ALREADY_PRESENT")
        return

    if OLD not in text:
        raise RuntimeError("Replay enforcement block not found")

    BACKUP.mkdir(parents=True, exist_ok=True)
    (BACKUP / TARGET.name).write_text(text, encoding="utf-8")

    TARGET.write_text(text.replace(OLD, NEW, 1), encoding="utf-8")

    print("GOVERNED_OWNER_ADMIN_REPLAY_BYPASS_INSTALLED")
    print("Backup:", BACKUP)
    print("Updated:", TARGET)

if __name__ == "__main__":
    main()