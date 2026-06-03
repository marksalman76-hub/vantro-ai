from pathlib import Path
import importlib.util
import py_compile

ROOT = Path.cwd()

runtime_file = ROOT / "backend" / "app" / "runtime" / "dynamic_agent_learning_verification.py"
main_file = ROOT / "backend" / "app" / "main.py"
doc_file = ROOT / "docs" / "dynamic-agent-learning-verification.md"

required_files = [runtime_file, main_file, doc_file]

for path in required_files:
    if not path.exists():
        raise AssertionError(f"Missing required file: {path}")

py_compile.compile(str(runtime_file), doraise=True)

spec = importlib.util.spec_from_file_location("dynamic_agent_learning_verification", runtime_file)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

status = module.get_dynamic_agent_learning_verification()
client_status = module.get_client_safe_dynamic_agent_learning_verification()

required_true_flags = [
    "dynamic_learning_enabled",
    "governed_learning_memory_enabled",
    "outcome_scoring_enabled",
    "feedback_based_adaptation_enabled",
    "provider_outcome_learning_enabled",
    "approval_revision_learning_enabled",
    "tenant_specific_learning_enabled",
    "business_profile_context_learning_enabled",
    "owner_approval_required_for_learning_policy_changes",
]

for flag in required_true_flags:
    if status.get(flag) is not True:
        raise AssertionError(f"Expected true flag missing or false: {flag}")

required_false_flags = [
    "autonomous_core_model_retraining_allowed",
    "governance_override_allowed",
    "prompt_or_internal_logic_exposure_allowed",
    "credential_values_exposed",
    "external_actions_performed",
]

for flag in required_false_flags:
    if status.get(flag) is not False:
        raise AssertionError(f"Unsafe flag must be false: {flag}")
    if client_status.get(flag) is not False:
        raise AssertionError(f"Client unsafe flag must be false: {flag}")

if status.get("agent_count", 0) < 10:
    raise AssertionError("Expected at least 10 agent learning records")

runtime_text = runtime_file.read_text(encoding="utf-8")
main_text = main_file.read_text(encoding="utf-8")
doc_text = doc_file.read_text(encoding="utf-8")
combined_text = runtime_text + "\n" + main_text + "\n" + doc_text

required_markers = [
    "DYNAMIC_AGENT_LEARNING_VERIFICATION_READY",
    "business_profile_context",
    "deliverable_output_quality",
    "approval_revision_history",
    "client_feedback_signal",
    "execution_outcome_score",
    "provider_quality_result",
    "tenant_memory_context",
    "/dynamic-agent-learning-verification",
    "/admin/dynamic-agent-learning-verification",
    "get_dynamic_agent_learning_verification",
]

for marker in required_markers:
    if marker not in combined_text:
        raise AssertionError(f"Missing marker: {marker}")

print("DYNAMIC_AGENT_LEARNING_VERIFICATION_PASSED")
