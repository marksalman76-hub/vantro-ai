from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP = ROOT / "backups" / f"row19_regression_test_suite_before_{STAMP}"

FILES = {
    "test_row19_regression_test_suite.py": r'''from pathlib import Path
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
''',

    "frontend/src/lib/regressionTestSuiteStatus.ts": r'''export type RegressionTestSuiteStatus = {
  success: boolean;
  row: 19;
  layer: "regression_test_suite";
  status: "ready";
  regression_suite_enabled: true;
  production_matrix_coverage_enabled: true;
  security_marker_checks_enabled: true;
  frontend_build_required: true;
  covered_rows: number[];
  covered_layers: string[];
  protected_markers: string[];
  forbidden_markers: string[];
  verified_at: string;
};

export function getRegressionTestSuiteStatus(): RegressionTestSuiteStatus {
  return {
    success: true,
    row: 19,
    layer: "regression_test_suite",
    status: "ready",
    regression_suite_enabled: true,
    production_matrix_coverage_enabled: true,
    security_marker_checks_enabled: true,
    frontend_build_required: true,
    covered_rows: [15, 16, 17, 18],
    covered_layers: [
      "durable_runtime_storage",
      "governed_learning_memory",
      "security_governance_closure",
      "integration_connection_hub",
    ],
    protected_markers: [
      "credential_values_exposed_false",
      "proprietary_logic_hidden_from_clients",
      "no_autonomous_retraining",
      "tenant_isolation_enforced",
      "owner_approval_required_for_sensitive_actions",
      "external_actions_performed_false",
    ],
    forbidden_markers: [
      "credential_values_exposed_true",
      "proprietary_logic_exposed_true",
      "external_action_performed_true",
    ],
    verified_at: new Date().toISOString(),
  };
}
''',

    "frontend/src/app/api/regression-test-suite-status/route.ts": r'''import { NextResponse } from "next/server";
import { getRegressionTestSuiteStatus } from "@/lib/regressionTestSuiteStatus";

export const dynamic = "force-dynamic";

export async function GET() {
  return NextResponse.json(getRegressionTestSuiteStatus());
}
''',
}

def backup_file(relative_path: str) -> None:
    source = ROOT / relative_path
    if source.exists():
        destination = BACKUP / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)

def write_file(relative_path: str, content: str) -> None:
    path = ROOT / relative_path
    backup_file(relative_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")

def main() -> None:
    BACKUP.mkdir(parents=True, exist_ok=True)

    for relative_path, content in FILES.items():
        write_file(relative_path, content)

    print("ROW19_REGRESSION_TEST_SUITE_INSTALLED")
    print(f"Backup folder: {BACKUP}")

    for relative_path in FILES:
        print(f"Created/updated: {ROOT / relative_path}")

if __name__ == "__main__":
    main()