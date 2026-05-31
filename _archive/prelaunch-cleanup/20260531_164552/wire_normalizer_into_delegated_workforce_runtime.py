from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
runtime_file = ROOT / "backend" / "app" / "runtime" / "delegated_workforce_execution_runtime.py"

backup_dir = ROOT / "backups" / f"delegated_workforce_normalizer_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)
shutil.copy2(runtime_file, backup_dir / runtime_file.name)

content = runtime_file.read_text(encoding="utf-8")

old_import = """from backend.app.runtime.persistent_action_execution_history import (
    record_action_execution,
)
"""

new_import = """from backend.app.runtime.persistent_action_execution_history import (
    record_action_execution,
)
from backend.app.runtime.intelligent_action_packet_normalizer import (
    normalize_implementation_plan,
)
"""

if old_import not in content:
    raise SystemExit("HISTORY_IMPORT_BLOCK_NOT_FOUND")

content = content.replace(old_import, new_import)

old_start = """def execute_delegated_workforce_plan(
    *,
    implementation_plan: Dict[str, Any],
    owner_approved: bool = False,
    client_owned_agents: List[str] | None = None,
    package_tier: str = "starter",
) -> Dict[str, Any]:

    client_owned_agents = client_owned_agents or []

    package_tier = (package_tier or "starter").lower()
"""

new_start = """def execute_delegated_workforce_plan(
    *,
    implementation_plan: Dict[str, Any],
    owner_approved: bool = False,
    client_owned_agents: List[str] | None = None,
    package_tier: str = "starter",
) -> Dict[str, Any]:

    client_owned_agents = client_owned_agents or []

    implementation_plan = normalize_implementation_plan(
        implementation_plan or {"action_packets": []},
        fallback_agent="marketing_specialist_agent",
    )

    package_tier = (package_tier or "starter").lower()
"""

if old_start not in content:
    raise SystemExit("FUNCTION_START_BLOCK_NOT_FOUND")

content = content.replace(old_start, new_start)

old_return = """        "profile": "delegated_workforce_execution_runtime_v1",
        "execution_id": f"delegated_exec_{uuid.uuid4().hex[:12]}",
"""

new_return = """        "profile": "delegated_workforce_execution_runtime_v1",
        "normalization": implementation_plan.get("normalization"),
        "execution_id": f"delegated_exec_{uuid.uuid4().hex[:12]}",
"""

if old_return not in content:
    raise SystemExit("RETURN_PROFILE_BLOCK_NOT_FOUND")

content = content.replace(old_return, new_return)

runtime_file.write_text(content, encoding="utf-8")

test_file = ROOT / "test_normalized_delegated_workforce_runtime.py"
test_file.write_text(r'''
from backend.app.runtime.delegated_workforce_execution_runtime import execute_delegated_workforce_plan

plan = {
    "action_packets": [
        {
            "packet_id": "norm_runtime_001",
            "recommended_agent": "marketing_specialist_agent",
            "title": "4. Execution plan with concrete steps",
            "risk_level": "medium",
            "approval_required": False,
        },
        {
            "packet_id": "norm_runtime_002",
            "recommended_agent": "marketing_specialist_agent",
            "title": "Commission targeted healthcare technology market research and client interviews",
            "risk_level": "medium",
            "approval_required": False,
        },
        {
            "packet_id": "norm_runtime_003",
            "recommended_agent": "marketing_specialist_agent",
            "title": "Launch paid campaign and increase budget",
            "risk_level": "medium",
            "approval_required": False,
        },
    ]
}

result = execute_delegated_workforce_plan(
    implementation_plan=plan,
    owner_approved=False,
    client_owned_agents=["marketing_specialist_agent"],
    package_tier="enterprise",
)

assert result["success"] is True
assert result["normalization"]["normalized_count"] == 3
assert result["completed_count"] >= 2
assert result["queued_count"] >= 1

completed_actions = [
    item.get("completed_output", "")
    for item in result["completed_results"]
]
assert any("Created" in item for item in completed_actions)

for item in result["completed_results"]:
    assert item.get("normalization_applied") is True or item.get("real_execution") is True

print("NORMALIZED_DELEGATED_WORKFORCE_RUNTIME_TEST_PASSED")
''', encoding="utf-8")

print("NORMALIZER_WIRED_INTO_DELEGATED_WORKFORCE_RUNTIME")
print(f"Backup: {backup_dir}")
print(f"Updated: {runtime_file}")
print(f"Created: {test_file}")