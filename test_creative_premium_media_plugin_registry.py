from pathlib import Path
import importlib.util
import py_compile

ROOT = Path.cwd()

runtime_file = ROOT / "backend" / "app" / "runtime" / "creative_premium_media_plugin_registry.py"
main_file = ROOT / "backend" / "app" / "main.py"
doc_file = ROOT / "docs" / "creative-premium-media-plugin-registry.md"

required_files = [runtime_file, main_file, doc_file]

for path in required_files:
    if not path.exists():
        raise AssertionError(f"Missing required file: {path}")

py_compile.compile(str(runtime_file), doraise=True)

spec = importlib.util.spec_from_file_location("creative_premium_media_plugin_registry", runtime_file)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

status = module.get_creative_premium_media_plugin_registry()
client_status = module.get_client_safe_creative_premium_media_plugin_registry()

if status.get("plugin_count") < 11:
    raise AssertionError("Expected at least 11 premium creative plugins")

required_plugins = [
    "runway_video_generation",
    "kling_video_generation",
    "heygen_avatar_video",
    "elevenlabs_voice",
    "lip_sync_dubbing",
    "music_sfx_generation",
    "image_video_upscaling",
    "video_editing_render_pipeline",
    "brand_safe_creative_moderation",
    "multi_scene_character_consistency",
    "social_ad_export_presets",
]

plugin_keys = [plugin["plugin_key"] for plugin in status["plugins"]]

for key in required_plugins:
    if key not in plugin_keys:
        raise AssertionError(f"Missing premium creative plugin: {key}")

required_true_flags = [
    "production_launch_matrix_complete",
    "post_launch_operational_readiness_complete",
    "premium_creative_plugin_registry_enabled",
    "owner_activation_required_for_paid_providers",
    "client_safe_visibility_enabled",
    "tenant_isolation_preserved",
]

for flag in required_true_flags:
    if status.get(flag) is not True:
        raise AssertionError(f"Expected true flag missing or false: {flag}")

for unsafe_flag in ["credential_values_exposed", "external_actions_performed", "live_provider_calls_triggered"]:
    if status.get(unsafe_flag) is not False:
        raise AssertionError(f"Unsafe flag must be false: {unsafe_flag}")
    if client_status.get(unsafe_flag) is not False:
        raise AssertionError(f"Client unsafe flag must be false: {unsafe_flag}")

runtime_text = runtime_file.read_text(encoding="utf-8")
main_text = main_file.read_text(encoding="utf-8")
doc_text = doc_file.read_text(encoding="utf-8")
combined_text = runtime_text + "\n" + main_text + "\n" + doc_text

required_markers = required_plugins + [
    "CREATIVE_PREMIUM_MEDIA_PLUGIN_REGISTRY_READY",
    "/creative/premium-media-plugin-registry",
    "/admin/creative/premium-media-plugin-registry",
    "get_creative_premium_media_plugin_registry",
]

for marker in required_markers:
    if marker not in combined_text:
        raise AssertionError(f"Missing marker: {marker}")

print("CREATIVE_PREMIUM_MEDIA_PLUGIN_REGISTRY_PASSED")
