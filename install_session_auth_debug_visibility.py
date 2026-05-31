from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent
TARGET = ROOT / "backend" / "app" / "core" / "session_auth_hardening_runtime.py"
BACKUP = ROOT / "backups" / f"session_auth_debug_visibility_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

OLD = '''        if assessment["blocked"]:
            return JSONResponse(
                status_code=403,
                content={
                    "success": False,
                    "error": "auth_security_policy_blocked",
                    "message": "Request blocked by authentication security policy.",
                    "security_profile": SESSION_AUTH_PROFILE,
                },
            )
'''

NEW = '''        if assessment["blocked"]:
            content = {
                "success": False,
                "error": "auth_security_policy_blocked",
                "message": "Request blocked by authentication security policy.",
                "security_profile": SESSION_AUTH_PROFILE,
            }

            if (
                request.url.path.lower() in {"/run-agent", "/api/run-agent"}
                and (
                    request.headers.get("authorization")
                    or request.headers.get("x-admin-token")
                )
            ):
                content["debug_visibility"] = {
                    "customer_safe": True,
                    "secret_values_exposed": False,
                    "path": request.url.path,
                    "method": request.method,
                    "severity": assessment.get("severity"),
                    "blocked": assessment.get("blocked"),
                    "reasons": assessment.get("reasons", []),
                }

            return JSONResponse(
                status_code=403,
                content=content,
            )
'''

def main():
    text = TARGET.read_text(encoding="utf-8", errors="replace")

    if '"debug_visibility"' in text:
        print("SESSION_AUTH_DEBUG_VISIBILITY_ALREADY_PRESENT")
        return

    if OLD not in text:
        raise RuntimeError("Blocked response block not found")

    BACKUP.mkdir(parents=True, exist_ok=True)
    (BACKUP / TARGET.name).write_text(text, encoding="utf-8")

    TARGET.write_text(text.replace(OLD, NEW, 1), encoding="utf-8")

    print("SESSION_AUTH_DEBUG_VISIBILITY_INSTALLED")
    print("Backup:", BACKUP)
    print("Updated:", TARGET)

if __name__ == "__main__":
    main()