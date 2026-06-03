from pathlib import Path
import importlib.util
import py_compile

ROOT = Path.cwd()

runtime_file = ROOT / "backend" / "app" / "runtime" / "creative_quality_refinement_loop.py"
doc_file = ROOT / "docs" / "creative-quality-refinement-loop.md"

for path in [runtime_file, doc_file]:
    if not path.exists():
        raise AssertionError(f"Missing required file: {path}")

py_compile.compile(str(runtime_file), doraise=True)

spec = importlib.util.spec_from_file_location("creative_quality_refinement_loop", runtime_file)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

status = module.get_creative_quality_refinement_loop_status()

required_true = [
    "provider_quality_scoring_enabled",
    "provider_comparison_enabled",
    "retry_recommendation_enabled",
    "refinement_recommendation_enabled",
    "learning_signal_generation_enabled",
]

for flag in required_true:
    if status.get(flag) is not True:
        raise AssertionError(f"Expected enabled flag missing: {flag}")

if status.get("hardcoded_provider_ranking") is not False:
    raise AssertionError("Provider ranking must remain flexible")

for unsafe in ["credential_values_exposed", "external_actions_performed", "live_provider_calls_triggered"]:
    if status.get(unsafe) is not False:
        raise AssertionError(f"Unsafe flag must be false: {unsafe}")

score = module.score_creative_output(
    provider="runway",
    creative_goal="Luxury cinematic SaaS commercial",
    target_platform="YouTube",
    multilingual=False,
)

if score.get("success") is not True:
    raise AssertionError("Scoring failed")

if score.get("final_quality_score", 0) < 70:
    raise AssertionError("Unexpectedly low quality score")

comparison = module.compare_creative_provider_options(
    creative_goal="Realistic multilingual UGC ad",
    providers=["runway", "kling", "heygen", "elevenlabs", "sync"],
    multilingual=True,
)

if comparison.get("success") is not True:
    raise AssertionError("Provider comparison failed")

if not comparison.get("ranked_provider_scores"):
    raise AssertionError("Expected ranked provider scores")

runtime_text = runtime_file.read_text(encoding="utf-8")
doc_text = doc_file.read_text(encoding="utf-8")
combined = runtime_text + "\n" + doc_text

required_markers = [
    "CREATIVE_QUALITY_REFINEMENT_LOOP_READY",
    "score_creative_output",
    "compare_creative_provider_options",
    "retry_recommended",
    "refinement_actions",
    "learning_signal_generation_enabled",
]

for marker in required_markers:
    if marker not in combined:
        raise AssertionError(f"Missing marker: {marker}")

print("CREATIVE_QUALITY_REFINEMENT_LOOP_PASSED")
