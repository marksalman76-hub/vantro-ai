from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
ARCHIVE = ROOT / "cleanup_archive" / f"ui_cleanup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
ARCHIVE.mkdir(parents=True, exist_ok=True)

KEEP = {
    "rebuild_clean_compact_execution_workspace.py",
    "polish_left_run_agent_section_only.py",
    "remove_execution_layout_useeffects_final.py",
}

ARCHIVE_PATTERNS = [
    "apply_business_profile_*.py",
    "business_profile_*.txt",
    "client_header_block.txt",
    "client_page_structure_report.txt",
    "client_top_section_exact.txt",
    "client_workspace_runtime_pass1.py",
    "compact_business_profile_action_pills.py",
    "compact_profile_panel_save_layout.py",
    "current_pd_menu_block.txt",
    "current_run_agent_block.txt",
    "fix_*",
    "force_*",
    "inspect_*",
    "install_client_business_profile_runtime.py",
    "live_deploy_email_result_test.py",
    "polish_onboarding_activation_login_ui.py",
    "remove_account_centre_tab_buttons.py",
    "settings_menu_debug.txt",
    "slim_business_profile_action_strip.py",
    "wire_client_business_profile_ui.py",
    "({",
    "({}))",
    "git",
    "npm",
]

moved = []
removed_pycache = []

for pattern in ARCHIVE_PATTERNS:
    for path in ROOT.glob(pattern):
        if path.name in KEEP:
            continue
        if path.is_file():
            target = ARCHIVE / path.name
            if target.exists():
                target = ARCHIVE / f"{path.stem}_{datetime.now().strftime('%H%M%S')}{path.suffix}"
            shutil.move(str(path), str(target))
            moved.append(str(path.relative_to(ROOT)))

# Archive nested old one-off scripts accidentally created under frontend/
for nested in [
    ROOT / "frontend" / "install_client_header_account_menu.py",
    ROOT / "frontend" / "replace_integrations_layout_final.py",
]:
    if nested.exists() and nested.is_file():
        target = ARCHIVE / f"frontend__{nested.name}"
        shutil.move(str(nested), str(target))
        moved.append(str(nested.relative_to(ROOT)))

# Remove Python cache folders safely.
for pycache in ROOT.rglob("__pycache__"):
    if pycache.is_dir():
        shutil.rmtree(pycache)
        removed_pycache.append(str(pycache.relative_to(ROOT)))

print("SAFE_REPO_DECLUTTER_COMPLETE")
print(f"Archive folder: {ARCHIVE}")
print("Archived files:", len(moved))
for item in moved:
    print("ARCHIVED:", item)
print("Removed __pycache__ folders:", len(removed_pycache))
for item in removed_pycache:
    print("REMOVED_PYCACHE:", item)