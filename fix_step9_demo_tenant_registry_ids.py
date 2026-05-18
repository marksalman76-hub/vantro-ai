from pathlib import Path
from datetime import datetime

root = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
main_path = root / "backend" / "app" / "main.py"
backup_dir = root / "backups"
backup_dir.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_path = backup_dir / f"main_before_step9_demo_tenant_registry_ids_{timestamp}.py"

text = main_path.read_text(encoding="utf-8")
backup_path.write_text(text, encoding="utf-8")

replacements = {
    '"master_orchestrator_agent"': '"head_agent"',
    '"product_image_direction_agent"': '"product_image_agent"',
}

for old, new in replacements.items():
    text = text.replace(old, new)

if "master_orchestrator_agent" in text:
    raise RuntimeError("master_orchestrator_agent still exists in main.py")

if "product_image_direction_agent" in text:
    raise RuntimeError("product_image_direction_agent still exists in main.py")

if "AGENT_ALIAS_MAP" in text:
    raise RuntimeError("AGENT_ALIAS_MAP still exists in main.py")

main_path.write_text(text, encoding="utf-8")

print("STEP_9_DEMO_TENANT_REGISTRY_IDS_FIXED")
print(f"Backup: {backup_path}")