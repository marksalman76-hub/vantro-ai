from pathlib import Path
import re
import subprocess
import sys

ROOT = Path.cwd()

required_files = [
    ROOT / "frontend" / "src" / "lib" / "finalProductionReleaseCandidate.ts",
    ROOT / "frontend" / "src" / "app" / "api" / "final-production-release-candidate-status" / "route.ts",
]

for path in required_files:
    if not path.exists():
        raise AssertionError(f"Missing required file: {path}")

lib_text = required_files[0].read_text(encoding="utf-8")

required_markers = [
    "full_matrix_complete",
    "production_release_candidate_enabled",
    "client_execution_ready",
    "admin_control_ready",
    "billing_ready",
    "package_credit_ready",
    "durable_storage_ready",
    "governed_learning_ready",
    "security_governance_ready",
    "integration_hub_ready",
    "regression_suite_ready",
    "monitoring_incident_ready",
    "sales_demo_ready",
    "credential_values_exposed: false",
    "external_actions_performed: false",
    "final_production_release_candidate_complete",
]

for marker in required_markers:
    if marker not in lib_text:
        raise AssertionError(f"Missing final release candidate marker: {marker}")

if re.search(r"credential_values_exposed:\s*true", lib_text):
    raise AssertionError("Credential exposure violation found")

if re.search(r"external_actions_performed:\s*true", lib_text):
    raise AssertionError("External action execution violation found")

route_text = required_files[1].read_text(encoding="utf-8")

if "getFinalProductionReleaseCandidateStatus" not in route_text:
    raise AssertionError("Final release candidate route must expose status function")

regression = ROOT / "test_row19_regression_test_suite.py"
if not regression.exists():
    raise AssertionError("Missing Row 19 regression suite")

result = subprocess.run(
    [sys.executable, "-X", "utf8", str(regression)],
    cwd=ROOT,
    text=True,
    capture_output=True,
)

if result.returncode != 0:
    raise AssertionError(
        f"Regression suite failed during final RC check\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    )

print(result.stdout.strip())
print("ROW22_FINAL_PRODUCTION_RELEASE_CANDIDATE_PASSED")
