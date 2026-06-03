from pathlib import Path
import importlib.util
import py_compile

ROOT = Path.cwd()

runtime_file = ROOT / "backend" / "app" / "runtime" / "creative_agent_premium_plugin_routing.py"
main_file = ROOT / "backend" / "app" / "main.py"
doc_file = ROOT / "docs" / "creative-agent-premium-plugin-routing.md"
registry_file = ROOT / "backend" / "app" / "runtime" / "creative_premium_media_plugin_registry.py"

required_files = [runtime_file, main_file, doc_file, registry_file]

for path in required_files:
    if not path.exists():
        raise AssertionError(f"Missing required file: {path}")

py_compile.compile(str(runtime_file), doraise=True)

spec = importlib.util.spec_from_file_location("creative_agent_premium_plugin_routing", runtime_file)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

status = module.get_creative_agent_premium_plugin_routing()
client_status = module.get_client_safe_creative_agent_premium_plugin_routing()

required_agents = [
    "ugc_creative_agent",
    "product_image_agent",
    "marketing_specialist_agent",
    "social_media_agent",
    "paid_ads_agent",
    "brand_strategy_agent",
    "sales_closer_agent",
    "product_copywriting_agent",
]

agent_keys = [record["agent_key"] for record in status["routing_records"]]

for agent in required_agents:
    if agent not in agent_keys:
        raise AssertionError(f"Missing routed creative agent: {agent}")

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

runtime_text = runtime_file.read_text(encoding="utf-8")
main_text = main_file.read_text(encoding="utf-8")
doc_text = doc_file.read_text(encoding="utf-8")
combined_text = runtime_text + "\n" + main_text + "\n" + doc_text

for plugin in required_plugins:
    if plugin not in combined_text:
        raise AssertionError(f"Missing routed premium plugin: {plugin}")

required_true_flags = [
    "premium_plugin_registry_required",
    "creative_agent_routing_enabled",
    "owner_activation_required_for_paid_providers",
    "tenant_isolation_preserved",
    "customer_safe_visibility_preserved",
]

for flag in required_true_flags:
    if status.get(flag) is not True:
        raise AssertionError(f"Expected true flag missing or false: {flag}")

for unsafe_flag in ["credential_values_exposed", "external_actions_performed", "live_provider_calls_triggered"]:
    if status.get(unsafe_flag) is not False:
        raise AssertionError(f"Unsafe flag must be false: {unsafe_flag}")
    if client_status.get(unsafe_flag) is not False:
        raise AssertionError(f"Client unsafe flag must be false: {unsafe_flag}")

route_markers = [
    "/creative/agent-premium-plugin-routing",
    "/admin/creative/agent-premium-plugin-routing",
    "get_creative_agent_premium_plugin_routing",
]

for marker in route_markers:
    if marker not in main_text:
        raise AssertionError(f"Missing route marker: {marker}")

print("CREATIVE_AGENT_PREMIUM_PLUGIN_ROUTING_PASSED")
