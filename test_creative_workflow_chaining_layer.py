from pathlib import Path
import importlib.util
import py_compile

ROOT = Path.cwd()

runtime_file = ROOT / "backend" / "app" / "runtime" / "creative_workflow_chaining_layer.py"
doc_file = ROOT / "docs" / "creative-workflow-chaining-layer.md"

for path in [runtime_file, doc_file]:
    if not path.exists():
        raise AssertionError(f"Missing required file: {path}")

py_compile.compile(str(runtime_file), doraise=True)

spec = importlib.util.spec_from_file_location("creative_workflow_chaining_layer", runtime_file)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

status = module.get_creative_workflow_chaining_status()

if status.get("multi_provider_chaining_enabled") is not True:
    raise AssertionError("Multi-provider chaining must be enabled")

if status.get("hardcoded_single_provider_path") is not False:
    raise AssertionError("Workflow must not be hardcoded to one provider")

for unsafe in ["credential_values_exposed", "external_actions_performed", "live_provider_calls_triggered"]:
    if status.get(unsafe) is not False:
        raise AssertionError(f"Unsafe flag must be false: {unsafe}")

required_templates = [
    "premium_voiceover_ad",
    "realistic_ugc_ad",
    "cinematic_commercial",
    "avatar_spokesperson_video",
    "multilingual_localised_campaign",
]

for template in required_templates:
    if template not in status.get("workflow_templates", {}):
        raise AssertionError(f"Missing workflow template: {template}")

plan = module.create_creative_workflow_chain(
    workflow_goal="Create a multilingual avatar spokesperson video",
    target_platform="Instagram Reels",
    language="Spanish",
    region="Spain",
    owner_approved_live_execution=False,
)

if plan.get("selected_template") != "avatar_spokesperson_video" and plan.get("selected_template") != "multilingual_localised_campaign":
    raise AssertionError("Expected avatar or multilingual workflow")

if plan.get("execution_allowed") is not False:
    raise AssertionError("Execution must remain blocked without owner approval")

runtime_text = runtime_file.read_text(encoding="utf-8")
doc_text = doc_file.read_text(encoding="utf-8")
combined = runtime_text + "\n" + doc_text

required_markers = [
    "CREATIVE_WORKFLOW_CHAINING_LAYER_READY",
    "create_creative_workflow_chain",
    "elevenlabs_voiceover",
    "runway_cinematic_generation",
    "kling_social_video_generation",
    "heygen_avatar_generation",
    "sync_dubbing_lipsync",
    "quality_scoring",
]

for marker in required_markers:
    if marker not in combined:
        raise AssertionError(f"Missing marker: {marker}")

print("CREATIVE_WORKFLOW_CHAINING_LAYER_PASSED")
