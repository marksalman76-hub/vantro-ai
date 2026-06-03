from pathlib import Path
import importlib.util
import py_compile

ROOT = Path.cwd()

runtime_file = ROOT / "backend" / "app" / "runtime" / "post_launch_final_operational_readiness_lock.py"
main_file = ROOT / "backend" / "app" / "main.py"
doc_file = ROOT / "docs" / "post-launch-final-operational-readiness-lock.md"

dependency_tests = [
    ROOT / "test_post_launch_infrastructure_scaling_readiness.py",
    ROOT / "test_post_launch_commercial_operations_sops.py",
    ROOT / "test_row22_final_production_release_candidate.py",
]

required_files = [runtime_file, main_file, doc_file] + dependency_tests

for path in required_files:
    if not path.exists():
        raise AssertionError(f"Missing required file: {path}")

py_compile.compile(str(runtime_file), doraise=True)

spec = importlib.util.spec_from_file_location(
    "post_launch_final_operational_readiness_lock",
    runtime_file,
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

status = module.get_post_launch_final_operational_readiness_lock()
client_status = module.get_client_safe_post_launch_final_operational_readiness_lock()

required_true_flags = [
    "production_launch_matrix_complete",
    "final_production_release_candidate_complete",
    "post_launch_operational_maturity_complete",
    "infrastructure_scaling_validation_complete",
    "commercial_operations_sops_complete",
    "backend_update_allowance_enabled",
    "future_backend_updates_allowed",
    "future_updates_require_tests",
    "future_high_risk_updates_require_owner_approval",
    "future_schema_changes_require_backup_and_review",
    "future_provider_scaling_requires_owner_approval",
    "future_pricing_changes_require_owner_approval",
    "owner_governance_preserved",
    "tenant_isolation_preserved",
    "customer_safe_visibility_preserved",
]

for flag in required_true_flags:
    if status.get(flag) is not True:
        raise AssertionError(f"Expected true flag missing or false: {flag}")

if status.get("credential_values_exposed") is not False:
    raise AssertionError("Credential exposure flag must be false")

if status.get("external_actions_performed") is not False:
    raise AssertionError("Status route must not perform external actions")

if client_status.get("credential_values_exposed") is not False:
    raise AssertionError("Client-safe status must not expose credentials")

runtime_text = runtime_file.read_text(encoding="utf-8")
main_text = main_file.read_text(encoding="utf-8")
doc_text = doc_file.read_text(encoding="utf-8")

required_markers = [
    "FULL_FINAL_PRODUCTION_LAUNCH_MATRIX_COMPLETE",
    "POST_LAUNCH_OPERATIONAL_READINESS_COMPLETE",
    "backend_update_allowance_enabled",
    "future_backend_updates_allowed",
    "future_high_risk_updates_require_owner_approval",
    "future_schema_changes_require_backup_and_review",
    "future_provider_scaling_requires_owner_approval",
    "future_pricing_changes_require_owner_approval",
    "owner_governance_preserved",
    "tenant_isolation_preserved",
    "credential_values_exposed",
    "external_actions_performed",
]

combined_text = runtime_text + "\n" + main_text + "\n" + doc_text

for marker in required_markers:
    if marker not in combined_text:
        raise AssertionError(f"Missing marker: {marker}")

route_markers = [
    "/post-launch/final-operational-readiness-lock",
    "/admin/post-launch/final-operational-readiness-lock",
    "get_post_launch_final_operational_readiness_lock",
]

for marker in route_markers:
    if marker not in main_text:
        raise AssertionError(f"Missing backend route marker: {marker}")

print("POST_LAUNCH_FINAL_OPERATIONAL_READINESS_LOCK_PASSED")
