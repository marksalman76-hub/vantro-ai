from pathlib import Path
import importlib.util
import py_compile

ROOT = Path.cwd()

runtime_file = ROOT / "backend" / "app" / "runtime" / "post_launch_commercial_operations_sops.py"
main_file = ROOT / "backend" / "app" / "main.py"
doc_file = ROOT / "docs" / "post-launch-commercial-operations-sops.md"

required_files = [runtime_file, main_file, doc_file]

for path in required_files:
    if not path.exists():
        raise AssertionError(f"Missing required file: {path}")

py_compile.compile(str(runtime_file), doraise=True)

spec = importlib.util.spec_from_file_location(
    "post_launch_commercial_operations_sops",
    runtime_file,
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

status = module.get_post_launch_commercial_operations_sops()
client_status = module.get_client_safe_post_launch_commercial_operations_sops()

required_true_flags = [
    "production_launch_matrix_complete",
    "commercial_operations_sops_enabled",
    "onboarding_sop_ready",
    "customer_support_sop_ready",
    "refund_dispute_handling_ready",
    "incident_playbooks_ready",
    "pricing_optimisation_review_ready",
    "sales_process_refinement_ready",
    "backend_update_allowance_preserved",
    "owner_approval_required_for_refunds_disputes_and_pricing_changes",
    "owner_approval_required_for_enterprise_terms",
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
    "client_onboarding",
    "customer_support",
    "refund_dispute_handling",
    "incident_playbooks",
    "pricing_optimisation",
    "sales_process_refinement",
    "backend_update_allowance_preserved",
    "owner_approval_required_for_refunds_disputes_and_pricing_changes",
    "credential_values_exposed",
    "external_actions_performed",
]

combined_text = runtime_text + "\n" + main_text + "\n" + doc_text

for marker in required_markers:
    if marker not in combined_text:
        raise AssertionError(f"Missing marker: {marker}")

route_markers = [
    "/post-launch/commercial-operations-sops",
    "/admin/post-launch/commercial-operations-sops",
    "get_post_launch_commercial_operations_sops",
]

for marker in route_markers:
    if marker not in main_text:
        raise AssertionError(f"Missing backend route marker: {marker}")

print("POST_LAUNCH_COMMERCIAL_OPERATIONS_SOPS_PASSED")
