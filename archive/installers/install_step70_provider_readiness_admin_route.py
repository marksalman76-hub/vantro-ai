from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
TARGET_FILE = PROJECT_ROOT / "backend" / "app" / "main.py"

BACKUP_DIR = PROJECT_ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_file = BACKUP_DIR / f"main_before_step70_provider_readiness_route_{timestamp}.py"

original = TARGET_FILE.read_text(encoding="utf-8")
backup_file.write_text(original, encoding="utf-8")

route_block = '''

# Step 70 — Provider Credential Readiness Admin Route
try:
    from backend.app.core.llm_provider_credential_readiness import (
        LLMProviderCredentialReadiness,
    )
except Exception:
    LLMProviderCredentialReadiness = None


@app.get("/admin/provider-readiness")
def admin_provider_readiness():
    """
    Admin-safe provider readiness visibility.

    This route shows provider readiness only.
    It never exposes credential values, secrets, prompts, backend configuration,
    or learning/governance internals.
    """
    if LLMProviderCredentialReadiness is None:
        return {
            "success": False,
            "error": "provider_credential_readiness_unavailable",
            "credential_values_exposed": False,
            "internal_prompts_exposed": False,
            "backend_config_exposed": False,
            "client_safe": True,
        }

    readiness = LLMProviderCredentialReadiness().check_all()

    return {
        "success": True,
        "route": "/admin/provider-readiness",
        "readiness": readiness,
        "visibility": {
            "admin_only": True,
            "client_safe": True,
            "credential_values_exposed": False,
            "internal_prompts_exposed": False,
            "backend_config_exposed": False,
            "learning_internals_exposed": False,
            "governance_internals_exposed": False,
        },
    }
'''

if "/admin/provider-readiness" in original:
    print("STEP_70_PROVIDER_READINESS_ADMIN_ROUTE_ALREADY_PRESENT")
    print(f"Backup created: {backup_file}")
else:
    TARGET_FILE.write_text(original.rstrip() + route_block + "\n", encoding="utf-8")
    print("STEP_70_PROVIDER_READINESS_ADMIN_ROUTE_INSTALLED")
    print(f"Backup created: {backup_file}")
    print(f"Updated: {TARGET_FILE}")