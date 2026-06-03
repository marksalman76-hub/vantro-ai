from pathlib import Path
import importlib.util
import py_compile

ROOT = Path.cwd()

runtime_file = ROOT / "backend" / "app" / "runtime" / "runtime_creative_execution_integration.py"
doc_file = ROOT / "docs" / "runtime-creative-execution-integration.md"

for path in [runtime_file, doc_file]:
    if not path.exists():
        raise AssertionError(f"Missing required file: {path}")

py_compile.compile(str(runtime_file), doraise=True)

spec = importlib.util.spec_from_file_location("runtime_creative_execution_integration", runtime_file)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

status = module.get_runtime_creative_execution_integration_status()

required_true = [
    "orchestration_connected",
    "workflow_chaining_connected",
    "quality_refinement_connected",
    "runtime_planning_enabled",
    "provider_fallback_ready",
    "retry_refinement_ready",
    "learning_signal_handoff_ready",
    "deliverable_generation_ready",
    "owner_approval_required_for_live_execution",
]

for flag in required_true:
    if status.get(flag) is not True:
        raise AssertionError(f"Expected true flag missing: {flag}")

if status.get("hardcoded_execution_path") is not False:
    raise AssertionError("Runtime execution path must not be hardcoded")

for unsafe in ["credential_values_exposed", "external_actions_performed", "live_provider_calls_triggered"]:
    if status.get(unsafe) is not False:
        raise AssertionError(f"Unsafe flag must be false: {unsafe}")

plan = module.create_runtime_creative_execution_plan(
    creative_goal="Create a multilingual avatar UGC ad for Instagram Reels",
    content_type="video ad",
    target_platform="Instagram Reels",
    language="Spanish",
    region="Spain",
    requires_avatar=True,
    requires_dubbing=True,
    requires_ugc_realism=True,
    owner_approved_live_execution=False,
)

if plan.get("success") is not True:
    raise AssertionError("Runtime creative execution plan failed")

if plan.get("execution_allowed") is not False:
    raise AssertionError("Execution must remain blocked without owner approval")

for expected in ["provider_plan", "workflow_chain", "quality_comparison"]:
    if expected not in plan:
        raise AssertionError(f"Missing runtime plan section: {expected}")

if not plan.get("selected_providers"):
    raise AssertionError("Expected selected providers")

if not plan.get("workflow_steps"):
    raise AssertionError("Expected workflow steps")

runtime_text = runtime_file.read_text(encoding="utf-8")
doc_text = doc_file.read_text(encoding="utf-8")
combined = runtime_text + "\n" + doc_text

required_markers = [
    "RUNTIME_CREATIVE_EXECUTION_INTEGRATION_READY",
    "create_runtime_creative_execution_plan",
    "provider_plan",
    "workflow_chain",
    "quality_comparison",
    "learning_signal_handoff_ready",
    "retry_refinement_ready",
]

for marker in required_markers:
    if marker not in combined:
        raise AssertionError(f"Missing marker: {marker}")

print("RUNTIME_CREATIVE_EXECUTION_INTEGRATION_PASSED")
