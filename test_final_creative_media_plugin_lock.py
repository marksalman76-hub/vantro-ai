from pathlib import Path
import importlib.util
import py_compile
import subprocess
import sys

ROOT = Path.cwd()

runtime_file = ROOT / "backend" / "app" / "runtime" / "final_creative_media_plugin_lock.py"
main_file = ROOT / "backend" / "app" / "main.py"
doc_file = ROOT / "docs" / "final-creative-media-plugin-lock.md"

dependency_tests = [
    ROOT / "test_creative_premium_media_plugin_registry.py",
    ROOT / "test_creative_agent_premium_plugin_routing.py",
    ROOT / "test_creative_provider_credential_activation_checks.py",
    ROOT / "test_post_launch_final_operational_readiness_lock.py",
]

required_files = [runtime_file, main_file, doc_file] + dependency_tests

for path in required_files:
    if not path.exists():
        raise AssertionError(f"Missing required file: {path}")

py_compile.compile(str(runtime_file), doraise=True)

spec = importlib.util.spec_from_file_location(
    "final_creative_media_plugin_lock",
    runtime_file,
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

status = module.get_final_creative_media_plugin_lock()
client_status = module.get_client_safe_final_creative_media_plugin_lock()

required_true_flags = [
    "premium_creative_plugin_registry_complete",
    "creative_agent_premium_routing_complete",
    "provider_credential_activation_checks_complete",
    "final_creative_media_plugin_infrastructure_complete",
    "production_launch_matrix_complete",
    "post_launch_operational_readiness_complete",
    "future_backend_updates_allowed",
    "owner_activation_required_for_paid_providers",
    "owner_approval_required_for_spend",
    "tenant_isolation_preserved",
    "customer_safe_visibility_preserved",
]

for flag in required_true_flags:
    if status.get(flag) is not True:
        raise AssertionError(f"Expected true flag missing or false: {flag}")

required_false_flags = [
    "credential_values_exposed",
    "external_actions_performed",
    "live_provider_calls_triggered",
    "live_execution_globally_enabled",
]

for flag in required_false_flags:
    if status.get(flag) is not False:
        raise AssertionError(f"Unsafe flag must be false: {flag}")
    if client_status.get(flag) is not False:
        raise AssertionError(f"Client unsafe flag must be false: {flag}")

required_capabilities = [
    "runway_style_video_generation",
    "kling_style_cinematic_video_generation",
    "heygen_style_avatar_video",
    "elevenlabs_style_premium_voice",
    "lip_sync_and_multilingual_dubbing",
    "music_and_sfx_generation",
    "image_video_upscaling",
    "video_editing_render_pipeline",
    "brand_safe_creative_moderation",
    "multi_scene_character_consistency",
    "social_ad_export_presets",
]

for capability in required_capabilities:
    if capability not in status.get("creative_media_capabilities_locked", []):
        raise AssertionError(f"Missing locked creative capability: {capability}")

runtime_text = runtime_file.read_text(encoding="utf-8")
main_text = main_file.read_text(encoding="utf-8")
doc_text = doc_file.read_text(encoding="utf-8")

combined_text = runtime_text + "\n" + main_text + "\n" + doc_text

required_markers = [
    "FINAL_CREATIVE_MEDIA_PLUGIN_INFRASTRUCTURE_COMPLETE",
    "/creative/final-media-plugin-lock",
    "/admin/creative/final-media-plugin-lock",
    "get_final_creative_media_plugin_lock",
    "7457a70",
    "9a3016a",
    "7cca39c",
]

for marker in required_markers:
    if marker not in combined_text:
        raise AssertionError(f"Missing marker: {marker}")

for test_file in dependency_tests:
    result = subprocess.run(
        [sys.executable, "-X", "utf8", str(test_file)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        raise AssertionError(
            f"Dependency test failed: {test_file.name}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )
    print(result.stdout.strip())

print("FINAL_CREATIVE_MEDIA_PLUGIN_LOCK_PASSED")
