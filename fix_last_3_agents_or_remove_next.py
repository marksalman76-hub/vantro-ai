from pathlib import Path
from datetime import datetime

backup_dir = Path("backups") / ("last_3_agents_final_fix_before_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
backup_dir.mkdir(parents=True, exist_ok=True)

files = [
    Path("backend/app/runtime/canonical_agent_identity_bridge.py"),
    Path("backend/app/core/global_agent_registry.py"),
    Path("backend/app/runtime/real_agent_component_catalogue.py"),
    Path("backend/app/main.py"),
]

for p in files:
    if p.exists():
        (backup_dir / p.name).write_text(p.read_text(encoding="utf-8"), encoding="utf-8")

# 1) Ensure QA is accepted by canonical identity before run-agent validation.
bridge = files[0].read_text(encoding="utf-8")
for line in [
    '    "qa_testing_agent": "qa_testing_agent",',
    '    "billing_optimisation_agent": "billing_optimisation_agent",',
    '    "training_learning_agent": "training_learning_agent",',
]:
    if line not in bridge:
        bridge = bridge.replace("CANONICAL_AGENT_ALIASES: Dict[str, str] = {", "CANONICAL_AGENT_ALIASES: Dict[str, str] = {\n" + line)
files[0].write_text(bridge, encoding="utf-8")

# 2) Make /run-agent owner_admin internal execution accept final system agents if global registry missed them.
main = files[3].read_text(encoding="utf-8")

main = main.replace(
'''    if not agent_exists(requested_agent):
        return {
            "success": False,
            "error": "unknown_agent",
            "requested_agent": request.requested_agent,
            "normalised_agent": requested_agent,
        }
''',
'''    owner_admin_system_agents = {
        "qa_testing_agent",
        "billing_optimisation_agent",
        "training_learning_agent",
    }

    if not agent_exists(requested_agent) and not (
        (request.actor_role or "").strip().lower() in {"owner", "admin", "owner_admin", "system"}
        and requested_agent in owner_admin_system_agents
    ):
        return {
            "success": False,
            "error": "unknown_agent",
            "requested_agent": request.requested_agent,
            "normalised_agent": requested_agent,
        }
'''
)

files[3].write_text(main, encoding="utf-8")

print("LAST_3_AGENTS_FINAL_FIX_APPLIED")
print("Backup:", backup_dir)