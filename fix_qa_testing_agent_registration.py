from pathlib import Path
from datetime import datetime

backup_dir = Path("backups") / ("qa_testing_agent_registration_before_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
backup_dir.mkdir(parents=True, exist_ok=True)

main_path = Path("backend/app/main.py")
registry_path = Path("backend/app/core/global_agent_registry.py")
bridge_path = Path("backend/app/runtime/canonical_agent_identity_bridge.py")

for path in [main_path, registry_path, bridge_path]:
    if path.exists():
        (backup_dir / path.name).write_text(path.read_text(encoding="utf-8"), encoding="utf-8")

# 1) Ensure canonical bridge keeps QA as canonical.
bridge = bridge_path.read_text(encoding="utf-8")
qa_alias = '    "qa_testing_agent": "qa_testing_agent",'
if qa_alias not in bridge:
    bridge = bridge.replace(
        "CANONICAL_AGENT_ALIASES: Dict[str, str] = {",
        "CANONICAL_AGENT_ALIASES: Dict[str, str] = {\n" + qa_alias
    )
bridge_path.write_text(bridge, encoding="utf-8")

# 2) Add QA to global registry if missing from the executable registry list.
registry = registry_path.read_text(encoding="utf-8")

if '"agent_id": "qa_testing_agent"' not in registry:
    insert = '''    {
        "agent_id": "qa_testing_agent",
        "name": "QA / Testing Agent",
        "category": "system_quality",
        "description": "Internal quality assurance, regression testing, workflow validation, and release-readiness checks.",
        "enterprise_only": True,
        "client_visible": False,
        "owner_admin_only": True,
        "default_workflow_stage": "quality_assurance",
        "default_action_type": "qa_testing_generation",
    },
'''
    marker = "GLOBAL_AGENT_REGISTRY = ["
    if marker not in registry:
        raise SystemExit("GLOBAL_AGENT_REGISTRY_MARKER_NOT_FOUND")
    registry = registry.replace(marker, marker + "\n" + insert, 1)

registry_path.write_text(registry, encoding="utf-8")

# 3) Hard guarantee owner_admin /run-agent can validate QA even if registry shape changes.
main = main_path.read_text(encoding="utf-8")

if '"qa_testing_agent",' not in main:
    main = main.replace(
        'owner_admin_system_agents = {',
        'owner_admin_system_agents = {\n        "qa_testing_agent",'
    )

main_path.write_text(main, encoding="utf-8")

print("QA_TESTING_AGENT_REGISTRATION_FIXED")
print("Backup:", backup_dir)