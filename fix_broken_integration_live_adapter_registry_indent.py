from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
target = ROOT / "backend" / "app" / "core" / "integration_live_adapter_registry.py"

backup_dir = ROOT / "backups" / f"integration_live_adapter_registry_indent_fix_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)
shutil.copy2(target, backup_dir / target.name)

text = target.read_text(encoding="utf-8")

bad_block = '''
    runtime_context = runtime_context or {}
    execution_packet = execution_packet or {}
    action_packet = action_packet or {}
    payload = payload or {}
'''

text = text.replace(bad_block, "")

target.write_text(text, encoding="utf-8")

print("INTEGRATION_LIVE_ADAPTER_REGISTRY_INDENT_FIXED")
print(f"Backup: {backup_dir}")
print(f"Updated: {target}")