from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
runtime_file = ROOT / "backend" / "app" / "runtime" / "delegated_workforce_execution_runtime.py"

backup_dir = ROOT / "backups" / f"external_action_records_delegated_runtime_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)
shutil.copy2(runtime_file, backup_dir / runtime_file.name)

content = runtime_file.read_text(encoding="utf-8")

old_import = """from backend.app.runtime.intelligent_action_packet_normalizer import (
    normalize_implementation_plan,
)
"""

new_import = """from backend.app.runtime.intelligent_action_packet_normalizer import (
    normalize_implementation_plan,
)
from backend.app.runtime.durable_external_action_records import (
    record_external_actions,
)
"""

if old_import not in content:
    raise SystemExit("NORMALIZER_IMPORT_BLOCK_NOT_FOUND")

content = content.replace(old_import, new_import)

old_history_block = """            history_record = record_action_execution(
                tenant_id="owner_admin" if enterprise_access else "client",
                packet_id=packet_result.get("packet_id"),
                assigned_agent=assigned_agent,
                execution_payload=packet_result,
            )
            packet_result["history_id"] = history_record.get("history_id")
            packet_result["history_persisted"] = True
            execution_results.append(packet_result)
"""

new_history_block = """            history_record = record_action_execution(
                tenant_id="owner_admin" if enterprise_access else "client",
                packet_id=packet_result.get("packet_id"),
                assigned_agent=assigned_agent,
                execution_payload=packet_result,
            )
            packet_result["history_id"] = history_record.get("history_id")
            packet_result["history_persisted"] = True

            external_records = record_external_actions(
                tenant_id="owner_admin" if enterprise_access else "client",
                execution_id=packet_result.get("execution_id"),
                packet_id=packet_result.get("packet_id"),
                assigned_agent=assigned_agent,
                deliverable=packet_result.get("deliverable"),
            )
            packet_result["external_action_record_count"] = external_records.get("record_count", 0)
            packet_result["external_action_records_persisted"] = external_records.get("record_count", 0) > 0
            packet_result["external_action_records"] = external_records.get("records", [])

            execution_results.append(packet_result)
"""

if old_history_block not in content:
    raise SystemExit("HISTORY_BLOCK_NOT_FOUND")

content = content.replace(old_history_block, new_history_block)

runtime_file.write_text(content, encoding="utf-8")

test_file = ROOT / "test_external_action_records_delegated_runtime.py"
test_file.write_text(r'''
from backend.app.runtime.delegated_workforce_execution_runtime import execute_delegated_workforce_plan
from backend.app.runtime.durable_external_action_records import list_external_action_records

plan = {
    "action_packets": [
        {
            "packet_id": "external_records_runtime_001",
            "recommended_agent": "marketing_specialist_agent",
            "title": "Commission targeted healthcare technology market research and client interviews",
            "risk_level": "medium",
            "approval_required": False,
        }
    ]
}

result = execute_delegated_workforce_plan(
    implementation_plan=plan,
    owner_approved=False,
    client_owned_agents=["marketing_specialist_agent"],
    package_tier="enterprise",
    connected_integrations=["email", "crm", "calendar"],
)

assert result["success"] is True
assert result["completed_count"] == 1

completed = result["completed_results"][0]
assert completed["external_action_performed"] is True
assert completed["live_external_call_executed"] is True
assert completed["external_action_records_persisted"] is True
assert completed["external_action_record_count"] >= 3

records = list_external_action_records(tenant_id="owner_admin", limit=20)
assert records["success"] is True
assert any(r.get("packet_id") == "external_records_runtime_001" for r in records["records"])

print("EXTERNAL_ACTION_RECORDS_DELEGATED_RUNTIME_TEST_PASSED")
''', encoding="utf-8")

print("EXTERNAL_ACTION_RECORDS_WIRED_INTO_DELEGATED_RUNTIME")
print(f"Backup: {backup_dir}")
print(f"Updated: {runtime_file}")
print(f"Created: {test_file}")