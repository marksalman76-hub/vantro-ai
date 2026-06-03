from pathlib import Path
import re

ROOT = Path.cwd()

required_files = [
    ROOT / "frontend" / "src" / "lib" / "governedLearningMemory.ts",
    ROOT / "frontend" / "src" / "app" / "api" / "governed-learning-memory-status" / "route.ts",
    ROOT / "frontend" / "src" / "app" / "api" / "admin-governed-learning-memory-status" / "route.ts",
]

for path in required_files:
    if not path.exists():
        raise AssertionError(f"Missing required file: {path}")

lib_text = required_files[0].read_text(encoding="utf-8")

required_markers = [
    "governed_memory_enabled",
    "client_safe_visibility",
    "proprietary_logic_hidden_from_clients",
    "owner_admin_diagnostics_enabled",
    "no_autonomous_retraining",
    "owner_approval_required_for_learning_policy_changes",
    "tenant_isolation_enforced",
    "proprietary_logic_exposed: false",
    "getClientSafeGovernedLearningMemoryStatus",
]

for marker in required_markers:
    if marker not in lib_text:
        raise AssertionError(f"Missing governed learning memory marker: {marker}")

if re.search(r"proprietary_logic_exposed:\s*true", lib_text):
    raise AssertionError("Client/proprietary exposure violation found")

client_route = required_files[1].read_text(encoding="utf-8")
admin_route = required_files[2].read_text(encoding="utf-8")

if "getClientSafeGovernedLearningMemoryStatus" not in client_route:
    raise AssertionError("Client route must use client-safe governed memory status")

if "getGovernedLearningMemoryStatus" not in admin_route:
    raise AssertionError("Admin route must use full governed memory status")

print("ROW16_GOVERNED_LEARNING_MEMORY_PASSED")
