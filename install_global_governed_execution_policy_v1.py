from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent
SESSION_FILE = ROOT / "backend" / "app" / "core" / "session_auth_hardening_runtime.py"
BACKUP = ROOT / "backups" / f"global_governed_execution_policy_v1_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

def backup(path: Path):
    BACKUP.mkdir(parents=True, exist_ok=True)
    (BACKUP / path.name).write_text(path.read_text(encoding="utf-8", errors="replace"), encoding="utf-8")

def main():
    text = SESSION_FILE.read_text(encoding="utf-8", errors="replace")

    if '"/run-agent"' not in text and '"/api/run-agent"' not in text:
        old = '''ADMIN_PATH_PREFIXES = (
    "/admin",
    "/owner",
)
'''
        new = '''ADMIN_PATH_PREFIXES = (
    "/admin",
    "/owner",
)

GOVERNED_EXECUTION_PATHS = (
    "/run-agent",
    "/api/run-agent",
)
'''
        if old not in text:
            raise RuntimeError("ADMIN_PATH_PREFIXES block not found")
        text = text.replace(old, new, 1)

    if "def _is_governed_execution_path" not in text:
        old = '''def _is_admin_path(path: str) -> bool:
    return any(path.startswith(prefix) for prefix in ADMIN_PATH_PREFIXES)
'''
        new = '''def _is_admin_path(path: str) -> bool:
    return any(path.startswith(prefix) for prefix in ADMIN_PATH_PREFIXES)


def _is_governed_execution_path(path: str) -> bool:
    return any(path.startswith(prefix) for prefix in GOVERNED_EXECUTION_PATHS)
'''
        if old not in text:
            raise RuntimeError("_is_admin_path block not found")
        text = text.replace(old, new, 1)

    old = '''    if _is_admin_path(path):
        if role not in SAFE_DEV_ADMIN_ROLES:
            reasons.append("admin_path_invalid_actor_role")
            severity = "high"

        if production and not auth and not admin_token:
            reasons.append("production_admin_missing_authorization")
            severity = "critical"
            blocked = True

        if tenant in {"", "unknown", "none", "null"}:
            reasons.append("admin_path_missing_tenant")
            severity = "medium" if severity == "none" else severity
'''
    new = '''    is_admin_path = _is_admin_path(path)
    is_governed_execution_path = _is_governed_execution_path(path)
    is_owner_admin_actor = role in SAFE_DEV_ADMIN_ROLES

    if is_admin_path:
        if not is_owner_admin_actor:
            reasons.append("admin_path_invalid_actor_role")
            severity = "high"

        if production and not auth and not admin_token:
            reasons.append("production_admin_missing_authorization")
            severity = "critical"
            blocked = True

        if tenant in {"", "unknown", "none", "null"}:
            reasons.append("admin_path_missing_tenant")
            severity = "medium" if severity == "none" else severity

    if is_governed_execution_path and is_owner_admin_actor:
        if production and not auth and not admin_token:
            reasons.append("owner_admin_governed_execution_missing_authorization")
            severity = "critical"
            blocked = True

    if is_governed_execution_path and not is_owner_admin_actor:
        # Customer/client governed execution stays restricted by normal
        # customer session, entitlement, package, credit, and tenant checks.
        # This block intentionally does not grant admin bypass to customers.
        if role in {"", "anonymous", "unknown", "none", "null"}:
            reasons.append("customer_execution_missing_actor_role")
            severity = "high" if severity in {"none", "medium"} else severity
            if production:
                blocked = True
'''
    if old not in text:
        raise RuntimeError("Admin assessment block not found")
    text = text.replace(old, new, 1)

    old = '''    if _csrf_risk(request):
        reasons.append("csrf_token_or_origin_missing_for_state_change")
        severity = "high" if severity in {"none", "medium"} else severity
        if production:
            blocked = True
'''
    new = '''    if _csrf_risk(request):
        if _is_governed_execution_path(path) and is_owner_admin_actor and (auth or admin_token):
            reasons.append("owner_admin_governed_execution_csrf_bypass_applied")
            severity = "medium" if severity == "none" else severity
        else:
            reasons.append("csrf_token_or_origin_missing_for_state_change")
            severity = "high" if severity in {"none", "medium"} else severity
            if production:
                blocked = True
'''
    if old not in text:
        raise RuntimeError("CSRF block not found")
    text = text.replace(old, new, 1)

    backup(SESSION_FILE)
    SESSION_FILE.write_text(text, encoding="utf-8")

    print("GLOBAL_GOVERNED_EXECUTION_POLICY_V1_INSTALLED")
    print("Backup:", BACKUP)
    print("Updated:", SESSION_FILE)

if __name__ == "__main__":
    main()