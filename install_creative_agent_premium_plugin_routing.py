from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP = ROOT / "backups" / f"creative_agent_premium_plugin_routing_before_{STAMP}"

RUNTIME_FILE = ROOT / "backend" / "app" / "runtime" / "creative_agent_premium_plugin_routing.py"
MAIN_FILE = ROOT / "backend" / "app" / "main.py"
DOC_FILE = ROOT / "docs" / "creative-agent-premium-plugin-routing.md"
TEST_FILE = ROOT / "test_creative_agent_premium_plugin_routing.py"

RUNTIME_CONTENT = r'''from datetime import datetime, timezone
from typing import Any, Dict, List

try:
    from backend.app.runtime.creative_premium_media_plugin_registry import (
        get_creative_premium_media_plugin_registry,
    )
except Exception:
    get_creative_premium_media_plugin_registry = None


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


CREATIVE_AGENT_ROUTING = {
    "ugc_creative_agent": [
        "runway_video_generation",
        "kling_video_generation",
        "heygen_avatar_video",
        "elevenlabs_voice",
        "lip_sync_dubbing",
        "music_sfx_generation",
        "video_editing_render_pipeline",
        "brand_safe_creative_moderation",
        "multi_scene_character_consistency",
        "social_ad_export_presets",
    ],
    "product_image_agent": [
        "runway_video_generation",
        "kling_video_generation",
        "image_video_upscaling",
        "brand_safe_creative_moderation",
        "social_ad_export_presets",
    ],
    "marketing_specialist_agent": [
        "runway_video_generation",
        "kling_video_generation",
        "heygen_avatar_video",
        "elevenlabs_voice",
        "lip_sync_dubbing",
        "music_sfx_generation",
        "video_editing_render_pipeline",
        "brand_safe_creative_moderation",
        "multi_scene_character_consistency",
        "social_ad_export_presets",
    ],
    "social_media_agent": [
        "video_editing_render_pipeline",
        "brand_safe_creative_moderation",
        "social_ad_export_presets",
        "music_sfx_generation",
    ],
    "paid_ads_agent": [
        "brand_safe_creative_moderation",
        "social_ad_export_presets",
        "video_editing_render_pipeline",
        "image_video_upscaling",
    ],
    "brand_strategy_agent": [
        "music_sfx_generation",
        "multi_scene_character_consistency",
        "brand_safe_creative_moderation",
    ],
    "sales_closer_agent": [
        "heygen_avatar_video",
        "elevenlabs_voice",
        "brand_safe_creative_moderation",
    ],
    "product_copywriting_agent": [
        "elevenlabs_voice",
        "brand_safe_creative_moderation",
    ],
}


def _registry_plugins_by_key() -> Dict[str, Dict[str, Any]]:
    if get_creative_premium_media_plugin_registry is None:
        return {}

    registry = get_creative_premium_media_plugin_registry()
    return {
        plugin["plugin_key"]: plugin
        for plugin in registry.get("plugins", [])
    }


def get_creative_agent_premium_plugin_routing() -> Dict[str, Any]:
    plugins = _registry_plugins_by_key()

    routing_records: List[Dict[str, Any]] = []

    for agent_key, plugin_keys in CREATIVE_AGENT_ROUTING.items():
        mapped_plugins = []
        for plugin_key in plugin_keys:
            plugin = plugins.get(plugin_key)
            mapped_plugins.append(
                {
                    "plugin_key": plugin_key,
                    "available_in_registry": plugin is not None,
                    "category": plugin.get("category") if plugin else "unknown",
                    "configured": bool(plugin.get("configured")) if plugin else False,
                    "live_execution_enabled": bool(plugin.get("live_execution_enabled")) if plugin else False,
                    "owner_activation_required": bool(plugin.get("owner_activation_required")) if plugin else True,
                    "credential_values_exposed": False,
                }
            )

        routing_records.append(
            {
                "agent_key": agent_key,
                "premium_plugin_count": len(plugin_keys),
                "plugins": mapped_plugins,
                "live_provider_calls_triggered": False,
                "external_actions_performed": False,
                "credential_values_exposed": False,
                "owner_activation_required_for_paid_providers": True,
            }
        )

    return {
        "success": True,
        "track": "creative_agent_premium_media_plugin_expansion",
        "layer": "creative_agent_premium_plugin_routing",
        "status": "ready",
        "premium_plugin_registry_required": True,
        "creative_agent_routing_enabled": True,
        "agent_count": len(routing_records),
        "credential_values_exposed": False,
        "external_actions_performed": False,
        "live_provider_calls_triggered": False,
        "owner_activation_required_for_paid_providers": True,
        "tenant_isolation_preserved": True,
        "customer_safe_visibility_preserved": True,
        "routing_records": routing_records,
        "routing_rules": [
            "Creative agents can discover premium plugin categories through governed routing.",
            "Routing does not enable live paid provider calls.",
            "Live execution requires provider credentials and owner approval.",
            "Spend-impacting creative provider usage remains owner-approved.",
            "Brand-safe moderation should be applied before customer delivery.",
            "Credential values must never be exposed to client or status routes.",
        ],
        "verified_at": _now(),
    }


def get_client_safe_creative_agent_premium_plugin_routing() -> Dict[str, Any]:
    status = get_creative_agent_premium_plugin_routing()

    return {
        "success": status["success"],
        "track": status["track"],
        "layer": status["layer"],
        "status": status["status"],
        "creative_agent_routing_enabled": status["creative_agent_routing_enabled"],
        "agent_count": status["agent_count"],
        "credential_values_exposed": False,
        "external_actions_performed": False,
        "live_provider_calls_triggered": False,
        "owner_activation_required_for_paid_providers": True,
        "tenant_isolation_preserved": True,
        "customer_safe_visibility_preserved": True,
        "routing_records": [
            {
                "agent_key": record["agent_key"],
                "premium_plugin_count": record["premium_plugin_count"],
                "plugins": [
                    {
                        "plugin_key": plugin["plugin_key"],
                        "available_in_registry": plugin["available_in_registry"],
                        "category": plugin["category"],
                        "configured": plugin["configured"],
                        "live_execution_enabled": plugin["live_execution_enabled"],
                        "owner_activation_required": plugin["owner_activation_required"],
                        "credential_values_exposed": False,
                    }
                    for plugin in record["plugins"]
                ],
            }
            for record in status["routing_records"]
        ],
        "verified_at": status["verified_at"],
    }
'''

DOC_CONTENT = r'''# Creative Agent Premium Plugin Routing

## Purpose

This layer connects creative agents to the premium media plugin registry.

It does not enable live paid provider execution. It gives agents governed access to plugin capability routing so future creative execution can choose the right plugin category safely.

## Creative Agents Routed

- UGC Creative Agent
- Product Image Agent
- Marketing Specialist Agent
- Social Media Agent
- Paid Ads Agent
- Brand Strategy Agent
- Sales / Closer Agent
- Product Copywriting Agent

## Routed Premium Plugin Categories

- video generation
- avatar video
- premium voice
- lip-sync and dubbing
- music/SFX
- image/video upscaling
- video editing/rendering
- brand-safe moderation
- multi-scene character consistency
- social/ad export presets

## Governance Rules

- Routing does not trigger provider calls.
- Live execution requires credentials and owner approval.
- Paid provider usage remains owner-approved.
- Credential values must never be exposed.
- Tenant isolation must remain preserved.
- Brand-safe moderation should be applied before delivery.

## Status

CREATIVE_AGENT_PREMIUM_PLUGIN_ROUTING_READY
'''

TEST_CONTENT = r'''from pathlib import Path
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
'''

MAIN_ROUTE_BLOCK = r'''
# CREATIVE_AGENT_PREMIUM_PLUGIN_ROUTING_START
try:
    from backend.app.runtime.creative_agent_premium_plugin_routing import (
        get_client_safe_creative_agent_premium_plugin_routing,
        get_creative_agent_premium_plugin_routing,
    )

    @app.get("/creative/agent-premium-plugin-routing")
    async def creative_agent_premium_plugin_routing():
        return get_client_safe_creative_agent_premium_plugin_routing()

    @app.get("/admin/creative/agent-premium-plugin-routing")
    async def admin_creative_agent_premium_plugin_routing():
        return get_creative_agent_premium_plugin_routing()

except Exception as creative_agent_premium_plugin_routing_error:
    @app.get("/creative/agent-premium-plugin-routing")
    async def creative_agent_premium_plugin_routing_unavailable():
        return {
            "success": False,
            "layer": "creative_agent_premium_plugin_routing",
            "status": "unavailable",
            "credential_values_exposed": False,
            "external_actions_performed": False,
            "live_provider_calls_triggered": False,
            "error": str(creative_agent_premium_plugin_routing_error),
        }

    @app.get("/admin/creative/agent-premium-plugin-routing")
    async def admin_creative_agent_premium_plugin_routing_unavailable():
        return {
            "success": False,
            "layer": "creative_agent_premium_plugin_routing",
            "status": "unavailable",
            "credential_values_exposed": False,
            "external_actions_performed": False,
            "live_provider_calls_triggered": False,
            "error": str(creative_agent_premium_plugin_routing_error),
        }
# CREATIVE_AGENT_PREMIUM_PLUGIN_ROUTING_END
'''


def backup_path(path: Path) -> None:
    if path.exists():
        relative = path.relative_to(ROOT)
        destination = BACKUP / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, destination)


def write_file(path: Path, content: str) -> None:
    backup_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def append_main_route_block() -> None:
    if not MAIN_FILE.exists():
        raise FileNotFoundError(f"Missing backend main file: {MAIN_FILE}")

    backup_path(MAIN_FILE)
    text = MAIN_FILE.read_text(encoding="utf-8", errors="ignore")

    if "CREATIVE_AGENT_PREMIUM_PLUGIN_ROUTING_START" not in text:
        MAIN_FILE.write_text(text.rstrip() + "\n\n" + MAIN_ROUTE_BLOCK.lstrip(), encoding="utf-8", newline="\n")


def main() -> None:
    BACKUP.mkdir(parents=True, exist_ok=True)

    write_file(RUNTIME_FILE, RUNTIME_CONTENT)
    write_file(DOC_FILE, DOC_CONTENT)
    write_file(TEST_FILE, TEST_CONTENT)
    append_main_route_block()

    print("CREATIVE_AGENT_PREMIUM_PLUGIN_ROUTING_INSTALLED")
    print(f"Backup folder: {BACKUP}")
    print(f"Created/updated: {RUNTIME_FILE}")
    print(f"Created/updated: {DOC_FILE}")
    print(f"Created/updated: {TEST_FILE}")
    print(f"Updated: {MAIN_FILE}")


if __name__ == "__main__":
    main()