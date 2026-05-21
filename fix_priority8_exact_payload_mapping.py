from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
TARGET = ROOT / "backend" / "app" / "core" / "saas_provisioning_runtime.py"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

if not TARGET.exists():
    raise FileNotFoundError(TARGET)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUP_DIR / f"saas_provisioning_runtime_before_exact_payload_mapping_{timestamp}.py"
backup.write_text(TARGET.read_text(encoding="utf-8"), encoding="utf-8")

text = TARGET.read_text(encoding="utf-8")

old_package = 'package = _normalise_package(payload.get("package"))'
new_package = 'package = _normalise_package(payload.get("package") or payload.get("package_id") or payload.get("plan"))'

old_agents = 'requested_agents = payload.get("requested_agents") or payload.get("agents") or []'
new_agents = 'requested_agents = payload.get("requested_agents") or payload.get("selected_agents") or payload.get("agents") or []'

if old_package not in text:
    raise RuntimeError("Exact package mapping line not found")

if old_agents not in text:
    raise RuntimeError("Exact requested_agents mapping line not found")

text = text.replace(old_package, new_package)
text = text.replace(old_agents, new_agents)

TARGET.write_text(text, encoding="utf-8")

print("PRIORITY8_EXACT_PAYLOAD_MAPPING_FIXED")
print(f"Backup: {backup}")
print(f"Updated: {TARGET}")
print("Changed:")
print(new_package)
print(new_agents)