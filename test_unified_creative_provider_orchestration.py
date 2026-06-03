from pathlib import Path
import importlib.util
import py_compile

ROOT = Path.cwd()

runtime_file = ROOT / "backend" / "app" / "runtime" / "unified_creative_provider_orchestration.py"
doc_file = ROOT / "docs" / "unified-creative-provider-orchestration.md"

for path in [runtime_file, doc_file]:
    if not path.exists():
        raise AssertionError(f"Missing required file: {path}")

py_compile.compile(str(runtime_file), doraise=True)

spec = importlib.util.spec_from_file_location("unified_creative_provider_orchestration", runtime_file)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

status = module.get_unified_creative_provider_orchestration_status()

required_true = [
    "flexible_provider_selection_enabled",
    "policy_driven_routing_enabled",
    "learning_aware_routing_ready",
    "owner_approval_required_for_live_execution",
]

for flag in required_true:
    if status.get(flag) is not True:
        raise AssertionError(f"Expected true flag missing: {flag}")

if status.get("hardcoded_provider_paths") is not False:
    raise AssertionError("Provider paths must not be hardcoded")

for unsafe in ["credential_values_exposed", "external_actions_performed", "live_provider_calls_triggered"]:
    if status.get(unsafe) is not False:
        raise AssertionError(f"Unsafe flag must be false: {unsafe}")

plan = module.choose_creative_provider_mix(
    creative_goal="Create a multilingual avatar spokesperson UGC ad",
    content_type="video ad",
    target_platform="TikTok",
    language="Spanish",
    requires_avatar=True,
    requires_dubbing=True,
    requires_ugc_realism=True,
    requires_voiceover=True,
    owner_approved_live_execution=False,
)

for provider in ["elevenlabs", "heygen", "sync", "kling"]:
    if provider not in plan["selected_providers"]:
        raise AssertionError(f"Expected provider missing from plan: {provider}")

if plan["execution_allowed"] is not False:
    raise AssertionError("Execution must remain blocked without owner approval")

if plan["hardcoded_provider_path"] is not False:
    raise AssertionError("Plan must not be hardcoded")

runtime_text = runtime_file.read_text(encoding="utf-8")
doc_text = doc_file.read_text(encoding="utf-8")
combined = runtime_text + "\n" + doc_text

required_markers = [
    "UNIFIED_CREATIVE_PROVIDER_ORCHESTRATION_READY",
    "choose_creative_provider_mix",
    "policy_driven_selection",
    "learning_aware_selection_ready",
    "elevenlabs",
    "runway",
    "kling",
    "heygen",
    "sync",
]

for marker in required_markers:
    if marker not in combined:
        raise AssertionError(f"Missing marker: {marker}")

print("UNIFIED_CREATIVE_PROVIDER_ORCHESTRATION_PASSED")
