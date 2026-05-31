from pathlib import Path
from datetime import datetime

ROOT = Path(".")
backup_dir = ROOT / "backups" / ("failed_agent_execution_final_before_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
backup_dir.mkdir(parents=True, exist_ok=True)

def backup(path: Path):
    if path.exists():
        out = backup_dir / path.name
        out.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")

main_path = Path("backend/app/main.py")
bridge_path = Path("backend/app/runtime/canonical_agent_identity_bridge.py")

backup(main_path)
backup(bridge_path)

main = main_path.read_text(encoding="utf-8")

if "from backend.app.runtime.canonical_agent_identity_bridge import normalise_agent_identity" not in main:
    main = main.replace(
        "from backend.app.runtime.execution_stack import (",
        "from backend.app.runtime.canonical_agent_identity_bridge import normalise_agent_identity\nfrom backend.app.runtime.execution_stack import (",
    )

main = main.replace(
    "requested_agent = normalize_agent_id(request.requested_agent)",
    "requested_agent = normalise_agent_identity(normalize_agent_id(request.requested_agent))",
)

main_path.write_text(main, encoding="utf-8")

bridge = bridge_path.read_text(encoding="utf-8")

required_aliases = {
    '"custom_websites_landing_pages_apps_agent": "website_landing_apps_agent",': '"custom_websites_landing_pages_apps_agent": "website_landing_apps_agent",',
    '"analytics_intelligence_agent": "analytics_optimisation_agent",': '"analytics_intelligence_agent": "analytics_optimisation_agent",',
    '"qa_testing_agent": "qa_testing_agent",': '"qa_testing_agent": "qa_testing_agent",',
    '"billing_optimisation_agent": "billing_optimisation_agent",': '"billing_optimisation_agent": "billing_optimisation_agent",',
    '"training_learning_agent": "training_learning_agent",': '"training_learning_agent": "training_learning_agent",',
}

for line in required_aliases:
    if line not in bridge:
        bridge = bridge.replace("CANONICAL_AGENT_ALIASES: Dict[str, str] = {", "CANONICAL_AGENT_ALIASES: Dict[str, str] = {\n    " + line)

bridge_path.write_text(bridge, encoding="utf-8")

print("FAILED_AGENT_EXECUTION_FINAL_PATCH_APPLIED")
print("Backup:", backup_dir)