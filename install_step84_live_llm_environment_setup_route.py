from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
TARGET_FILE = PROJECT_ROOT / "backend" / "app" / "main.py"

BACKUP_DIR = PROJECT_ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_file = BACKUP_DIR / f"main_before_step84_live_llm_env_setup_route_{timestamp}.py"

original = TARGET_FILE.read_text(encoding="utf-8")
backup_file.write_text(original, encoding="utf-8")

route_block = '''

# Step 84 — Live LLM Environment Setup Guide Route
@app.get("/admin/live-llm-environment-setup")
def admin_live_llm_environment_setup():
    return {
        "success": True,
        "route": "/admin/live-llm-environment-setup",
        "purpose": "Admin-safe setup checklist for enabling governed live LLM execution.",
        "required_environment_variables": [
            {
                "name": "OPENAI_API_KEY",
                "required_for": "OpenAI live provider execution",
                "value_exposed": False,
                "status": "Set this in the server environment only. Never store or display the value in the UI.",
            },
            {
                "name": "ENABLE_LIVE_LLM_CALLS",
                "required_for": "Global live LLM execution gate",
                "value_exposed": False,
                "accepted_values": ["1", "true", "yes", "enabled"],
                "status": "Must be enabled only after provider credentials and owner control are approved.",
            },
        ],
        "activation_requirements": {
            "openai_sdk_installed": True,
            "provider_credential_configured": "OPENAI_API_KEY must be configured in the backend server environment.",
            "owner_control_enabled": "Owner must enable /admin/live-llm-control.",
            "global_gate_enabled": "ENABLE_LIVE_LLM_CALLS must be enabled in the server environment.",
            "safety_test_required": "Run final no-secret/no-prompt/no-config exposure verification before live production use.",
        },
        "security_rules": {
            "credential_values_exposed": False,
            "internal_prompts_exposed": False,
            "backend_config_exposed": False,
            "learning_internals_exposed": False,
            "governance_internals_exposed": False,
            "client_safe": True,
        },
        "safe_next_steps": [
            "Set OPENAI_API_KEY in the local backend environment.",
            "Set ENABLE_LIVE_LLM_CALLS=true only when ready to allow live calls.",
            "Use /admin/live-llm-control to enable owner control.",
            "Check /admin/live-llm-readiness-dashboard.",
            "Run a controlled live call test with a low-risk ecommerce task.",
        ],
    }
'''

if "/admin/live-llm-environment-setup" in original:
    print("STEP_84_LIVE_LLM_ENVIRONMENT_SETUP_ROUTE_ALREADY_PRESENT")
    print(f"Backup created: {backup_file}")
else:
    TARGET_FILE.write_text(original.rstrip() + route_block + "\n", encoding="utf-8")
    print("STEP_84_LIVE_LLM_ENVIRONMENT_SETUP_ROUTE_INSTALLED")
    print(f"Backup created: {backup_file}")
    print(f"Updated: {TARGET_FILE}")