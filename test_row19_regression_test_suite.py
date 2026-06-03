from pathlib import Path
import subprocess
import sys

ROOT = Path.cwd()

ROW_TESTS = [
    "test_row15_durable_runtime_storage.py",
    "test_row16_governed_learning_memory.py",
    "test_row17_security_governance_closure.py",
    "test_row18_integration_connection_hub.py",
]

REQUIRED_FRONTEND_FILES = [
    "frontend/src/lib/durableRuntimeStorage.ts",
    "frontend/src/lib/governedLearningMemory.ts",
    "frontend/src/lib/securityGovernanceClosure.ts",
    "frontend/src/lib/integrationConnectionHub.ts",
    "frontend/src/app/api/durable-runtime-storage-status/route.ts",
    "frontend/src/app/api/admin-durable-runtime-storage-status/route.ts",
    "frontend/src/app/api/governed-learning-memory-status/route.ts",
    "frontend/src/app/api/admin-governed-learning-memory-status/route.ts",
    "frontend/src/app/api/security-governance-closure-status/route.ts",
    "frontend/src/app/api/admin-security-governance-closure-status/route.ts",
    "frontend/src/app/api/integration-connection-hub-status/route.ts",
    "frontend/src/app/api/admin-integration-connection-hub-status/route.ts",
]

REQUIRED_SECURITY_MARKERS = [
    "credential_values_exposed: false",
    "proprietary_logic_hidden_from_clients",
    "no_autonomous_retraining",
    "tenant_isolation_enforced",
    "owner_approval_required_for_sensitive_actions",
    "external_actions_performed: false",
]

def run_python_test(test_file: str) -> None:
    path = ROOT / test_file
    if not path.exists():
        raise AssertionError(f"Missing regression dependency: {test_file}")

    result = subprocess.run(
        [sys.executable, "-X", "utf8", str(path)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    if result.returncode != 0:
        raise AssertionError(
            f"Regression dependency failed: {test_file}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )

    print(result.stdout.strip())

def assert_required_files() -> None:
    missing = [file for file in REQUIRED_FRONTEND_FILES if not (ROOT / file).exists()]
    if missing:
        raise AssertionError(f"Missing required production files: {missing}")

def assert_security_markers() -> None:
    combined_text = ""
    for file in REQUIRED_FRONTEND_FILES:
        path = ROOT / file
        if path.exists():
            combined_text += "\n" + path.read_text(encoding="utf-8", errors="ignore")

    missing = [marker for marker in REQUIRED_SECURITY_MARKERS if marker not in combined_text]
    if missing:
        raise AssertionError(f"Missing regression security markers: {missing}")

    forbidden_markers = [
        "credential_values_exposed: true",
        "proprietary_logic_exposed: true",
        "external_action_performed: true",
    ]

    found_forbidden = [marker for marker in forbidden_markers if marker in combined_text]
    if found_forbidden:
        raise AssertionError(f"Forbidden unsafe markers found: {found_forbidden}")

def main() -> None:
    assert_required_files()
    assert_security_markers()

    for test_file in ROW_TESTS:
        run_python_test(test_file)

    print("ROW19_REGRESSION_TEST_SUITE_PASSED")

if __name__ == "__main__":
    main()
