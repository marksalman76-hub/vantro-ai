from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
TARGET_FILE = PROJECT_ROOT / "backend" / "app" / "main.py"

BACKUP_DIR = PROJECT_ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_file = BACKUP_DIR / f"main_before_step82_openai_sdk_route_{timestamp}.py"

original = TARGET_FILE.read_text(encoding="utf-8")
backup_file.write_text(original, encoding="utf-8")

route_block = '''

# Step 82 — OpenAI SDK Admin Readiness Route
try:
    from backend.app.core.openai_sdk_dependency_guard import openai_sdk_dependency_guard
except Exception:
    openai_sdk_dependency_guard = None


@app.get("/admin/openai-sdk-readiness")
def admin_openai_sdk_readiness():
    if openai_sdk_dependency_guard is None:
        return {
            "success": False,
            "error": "openai_sdk_dependency_guard_unavailable",
            "live_call_attempted": False,
            "credential_values_exposed": False,
            "internal_prompts_exposed": False,
            "backend_config_exposed": False,
            "client_safe": True,
        }

    return {
        "success": True,
        "route": "/admin/openai-sdk-readiness",
        "readiness": openai_sdk_dependency_guard.check(),
        "visibility": {
            "admin_only": True,
            "live_call_attempted": False,
            "credential_values_exposed": False,
            "internal_prompts_exposed": False,
            "backend_config_exposed": False,
            "client_safe": True,
        },
    }
'''

if "/admin/openai-sdk-readiness" in original:
    print("STEP_82_OPENAI_SDK_ADMIN_ROUTE_ALREADY_PRESENT")
    print(f"Backup created: {backup_file}")
else:
    TARGET_FILE.write_text(original.rstrip() + route_block + "\n", encoding="utf-8")
    print("STEP_82_OPENAI_SDK_ADMIN_ROUTE_INSTALLED")
    print(f"Backup created: {backup_file}")
    print(f"Updated: {TARGET_FILE}")