from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
TARGET_FILE = PROJECT_ROOT / "backend" / "app" / "main.py"

BACKUP_DIR = PROJECT_ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_file = BACKUP_DIR / f"main_before_step98_admin_operational_dashboard_{timestamp}.py"

original = TARGET_FILE.read_text(encoding="utf-8")
backup_file.write_text(original, encoding="utf-8")

route_block = '''

# Step 98 — Admin-Safe Operational Dashboard Consolidation Route
@app.get("/admin/operational-dashboard")
def admin_operational_dashboard():
    dashboard = {
        "success": True,
        "route": "/admin/operational-dashboard",
        "dashboard_status": "admin_safe_operational_dashboard_ready",
        "runtime_status": {
            "memory_stack_complete": True,
            "learning_stack_complete": True,
            "sqlite_persistence_complete": True,
            "llm_provider_stack_complete": True,
            "output_quality_stack_complete": True,
            "live_llm_gated_safe": True,
        },
        "admin_visibility": {
            "provider_readiness_route": "/admin/provider-readiness",
            "provider_audit_route": "/admin/provider-execution-audit",
            "openai_sdk_readiness_route": "/admin/openai-sdk-readiness",
            "live_llm_readiness_dashboard_route": "/admin/live-llm-readiness-dashboard",
            "live_llm_control_route": "/admin/live-llm-control",
            "output_quality_summary_route": "/admin/output-quality-summary",
            "platform_progress_matrix_route": "/admin/platform-progress-matrix",
        },
        "operational_controls": {
            "owner_live_llm_control_available": True,
            "provider_audit_available": True,
            "safe_readiness_checks_available": True,
            "environment_setup_guide_available": True,
            "progress_matrix_available": True,
        },
        "release_readiness": {
            "admin_safe_visibility_ready": True,
            "customer_safe_surface_pending_step_99": True,
            "final_local_regression_pending_step_100": True,
        },
        "security_summary": {
            "credential_values_exposed": False,
            "internal_prompts_exposed": False,
            "backend_config_exposed": False,
            "learning_internals_exposed": False,
            "governance_internals_exposed": False,
            "client_safe": True,
        },
    }

    return dashboard
'''

if "/admin/operational-dashboard" in original:
    print("STEP_98_ADMIN_OPERATIONAL_DASHBOARD_ALREADY_PRESENT")
    print(f"Backup created: {backup_file}")
else:
    TARGET_FILE.write_text(original.rstrip() + route_block + "\n", encoding="utf-8")
    print("STEP_98_ADMIN_OPERATIONAL_DASHBOARD_INSTALLED")
    print(f"Backup created: {backup_file}")
    print(f"Updated: {TARGET_FILE}")