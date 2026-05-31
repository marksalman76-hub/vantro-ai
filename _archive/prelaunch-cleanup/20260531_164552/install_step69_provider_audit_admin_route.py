from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
TARGET_FILE = PROJECT_ROOT / "backend" / "app" / "main.py"

BACKUP_DIR = PROJECT_ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_file = BACKUP_DIR / f"main_before_step69_provider_audit_route_{timestamp}.py"

original = TARGET_FILE.read_text(encoding="utf-8")
backup_file.write_text(original, encoding="utf-8")

route_block = '''

# Step 69 — Provider Execution Audit Admin Visibility Route
try:
    from backend.app.core.provider_execution_audit_log import provider_execution_audit_log
except Exception:
    provider_execution_audit_log = None


@app.get("/admin/provider-execution-audit")
def admin_provider_execution_audit(limit: int = 20):
    """
    Admin-safe provider execution audit visibility.

    Does not expose:
    - provider credential values
    - internal prompts
    - backend configuration
    - learning internals
    - governance internals
    """
    if provider_execution_audit_log is None:
        return {
            "success": False,
            "error": "provider_execution_audit_log_unavailable",
            "client_safe": True,
            "credential_values_exposed": False,
            "internal_prompts_exposed": False,
            "backend_config_exposed": False,
        }

    safe_limit = max(1, min(int(limit), 100))
    latest = provider_execution_audit_log.latest(safe_limit)

    return {
        "success": True,
        "route": "/admin/provider-execution-audit",
        "events": latest.get("events", []),
        "count": latest.get("count", 0),
        "limit": safe_limit,
        "visibility": {
            "admin_only": True,
            "client_safe": True,
            "credential_values_exposed": False,
            "internal_prompts_exposed": False,
            "backend_config_exposed": False,
            "learning_internals_exposed": False,
        },
    }
'''

if "/admin/provider-execution-audit" in original:
    print("STEP_69_PROVIDER_AUDIT_ADMIN_ROUTE_ALREADY_PRESENT")
    print(f"Backup created: {backup_file}")
else:
    TARGET_FILE.write_text(original.rstrip() + route_block + "\n", encoding="utf-8")
    print("STEP_69_PROVIDER_AUDIT_ADMIN_ROUTE_INSTALLED")
    print(f"Backup created: {backup_file}")
    print(f"Updated: {TARGET_FILE}")