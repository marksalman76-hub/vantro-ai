from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
main_file = ROOT / "backend" / "app" / "main.py"

backup_dir = ROOT / "backups" / f"provider_activation_visibility_import_fix_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)
shutil.copy2(main_file, backup_dir / "main.py")

text = main_file.read_text(encoding="utf-8")

text = text.replace(
    "from backend.app.runtime.real_provider_activation_registry import provider_activation_registry_status, provider_readiness, select_ready_provider_for_capability",
    "from backend.app.runtime.real_provider_activation_registry import get_all_provider_activation_statuses, get_provider_activation_status, select_ready_provider_for_capability",
)

text = text.replace(
    "provider_activation_registry_status()",
    "get_all_provider_activation_statuses()",
)

text = text.replace(
    "provider_readiness(provider_key)",
    "get_provider_activation_status(provider_key)",
)

main_file.write_text(text, encoding="utf-8")

print("PROVIDER_ACTIVATION_VISIBILITY_IMPORTS_FIXED")
print(f"Backup folder: {backup_dir}")
print(f"Updated: {main_file}")