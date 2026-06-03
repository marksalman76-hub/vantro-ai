from pathlib import Path
import importlib.util
import py_compile

ROOT = Path.cwd()

runtime_file = ROOT / "backend" / "app" / "runtime" / "post_launch_infrastructure_scaling_readiness.py"
main_file = ROOT / "backend" / "app" / "main.py"
doc_file = ROOT / "docs" / "post-launch-infrastructure-scaling-validation.md"

required_files = [runtime_file, main_file, doc_file]

for path in required_files:
    if not path.exists():
        raise AssertionError(f"Missing required file: {path}")

py_compile.compile(str(runtime_file), doraise=True)

spec = importlib.util.spec_from_file_location(
    "post_launch_infrastructure_scaling_readiness",
    runtime_file,
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

status = module.get_post_launch_infrastructure_scaling_readiness()
client_status = module.get_client_safe_post_launch_infrastructure_scaling_readiness()

required_true_flags = [
    "production_launch_matrix_complete",
    "infrastructure_scaling_validation_enabled",
    "heavier_concurrent_load_validation_ready",
    "cdn_optimisation_review_ready",
    "db_growth_validation_ready",
    "redis_queue_scaling_review_ready",
    "autoscaling_rules_review_ready",
    "provider_throughput_limits_review_ready",
    "backend_update_allowance_enabled",
    "safe_backend_update_mode_enabled",
    "backend_updates_require_owner_approval",
    "no_live_migration_without_owner_approval",
    "rollback_plan_required_for_backend_updates",
    "schema_change_review_required",
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
    "heavier_concurrent_load",
    "cdn_optimisation",
    "db_growth_validation",
    "redis_queue_scaling",
    "autoscaling_rules",
    "provider_throughput_limits",
    "backend_update_allowance_enabled",
    "backend_updates_require_owner_approval",
    "credential_values_exposed",
    "external_actions_performed",
]

combined_text = runtime_text + "\n" + main_text + "\n" + doc_text

for marker in required_markers:
    if marker not in combined_text:
        raise AssertionError(f"Missing marker: {marker}")

route_markers = [
    "/post-launch/infrastructure-scaling-readiness",
    "/admin/post-launch/infrastructure-scaling-readiness",
    "get_post_launch_infrastructure_scaling_readiness",
]

for marker in route_markers:
    if marker not in main_text:
        raise AssertionError(f"Missing backend route marker: {marker}")

print("POST_LAUNCH_INFRASTRUCTURE_SCALING_READINESS_PASSED")
