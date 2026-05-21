from pathlib import Path
import importlib

print("PRIORITY4_QUEUE_COMPLETION_PERSISTENCE_TEST")

queue_text = Path("backend/app/core/execution_queue_runtime.py").read_text(encoding="utf-8")
worker_text = Path("backend/app/core/execution_queue_worker_runtime.py").read_text(encoding="utf-8")

checks = {
    "completion_function": "def mark_execution_completed(" in queue_text,
    "success_alias": "def mark_execution_succeeded(" in queue_text,
    "worker_import": "mark_execution_completed" in worker_text,
    "completion_marker": "queue_completion_persistence_locked" in queue_text,
    "status_completed": "status = 'completed'" in queue_text,
    "worker_result_payload": "worker_result" in queue_text,
}

for key, value in checks.items():
    print(key, value)

assert all(checks.values())

queue_mod = importlib.import_module("backend.app.core.execution_queue_runtime")
worker_mod = importlib.import_module("backend.app.core.execution_queue_worker_runtime")

assert hasattr(queue_mod, "mark_execution_completed")
assert hasattr(queue_mod, "mark_execution_succeeded")

sample = {
    "queue_id": None,
    "tenant_id": "tenant_test",
    "agent_id": "marketing_specialist_agent",
    "action_type": "completion_persistence_test",
}

result = worker_mod._process_item_safely(sample)
print("sample_result", result)

assert result["execution_mode"] == "worker_lifecycle_completed"
assert result["status"] == "processed_successfully"
assert result["provider_direct_execution"] is False

print("PRIORITY4_QUEUE_COMPLETION_PERSISTENCE_OK")
