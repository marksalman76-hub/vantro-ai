from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
TARGET_FILE = PROJECT_ROOT / "backend" / "app" / "main.py"

BACKUP_DIR = PROJECT_ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_file = BACKUP_DIR / f"main_before_step96_output_quality_summary_{timestamp}.py"

original = TARGET_FILE.read_text(encoding="utf-8")
backup_file.write_text(original, encoding="utf-8")

route_block = '''

# Step 96 — Output Quality Summary Admin Route
@app.get("/admin/output-quality-summary")
def admin_output_quality_summary():
    return {
        "success": True,
        "route": "/admin/output-quality-summary",
        "quality_stack_status": "premium_output_quality_expansion_complete",
        "completed_quality_layers": {
            "89": "Product agent output quality expansion",
            "90": "UGC agent output quality expansion",
            "91": "Product image agent output quality expansion",
            "92": "Influencer agent output quality expansion",
            "93": "Analytics agent output quality expansion",
            "94": "General agent output quality expansion",
            "95": "Final output quality regression test",
        },
        "active_quality_standards": {
            "product_page": "premium_global_ecommerce_standard",
            "ugc": "premium_global_ugc_ad_standard",
            "product_image": "premium_global_ecommerce_visual_standard",
            "influencer": "premium_global_creator_partnership_standard",
            "analytics": "premium_global_ecommerce_growth_intelligence_standard",
            "general": "premium_global_ecommerce_agent_standard",
        },
        "platform_positioning": {
            "white_label_saas_ready": True,
            "global_localisation_ready": True,
            "competitor_benchmark_quality_ready": True,
            "premium_client_safe_outputs": True,
            "governed_execution_preserved": True,
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
'''

if "/admin/output-quality-summary" in original:
    print("STEP_96_OUTPUT_QUALITY_SUMMARY_ROUTE_ALREADY_PRESENT")
    print(f"Backup created: {backup_file}")
else:
    TARGET_FILE.write_text(original.rstrip() + route_block + "\n", encoding="utf-8")
    print("STEP_96_OUTPUT_QUALITY_SUMMARY_ROUTE_INSTALLED")
    print(f"Backup created: {backup_file}")
    print(f"Updated: {TARGET_FILE}")