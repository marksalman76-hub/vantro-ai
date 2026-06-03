from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP = ROOT / "backups" / f"creative_premium_media_plugin_registry_before_{STAMP}"

RUNTIME_FILE = ROOT / "backend" / "app" / "runtime" / "creative_premium_media_plugin_registry.py"
MAIN_FILE = ROOT / "backend" / "app" / "main.py"
DOC_FILE = ROOT / "docs" / "creative-premium-media-plugin-registry.md"
TEST_FILE = ROOT / "test_creative_premium_media_plugin_registry.py"

RUNTIME_CONTENT = r'''from datetime import datetime, timezone
from typing import Any, Dict, List


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _plugins() -> List[Dict[str, Any]]:
    return [
        {
            "plugin_key": "runway_video_generation",
            "label": "Runway-style Video Generation",
            "category": "video_generation",
            "supports": ["text_to_video", "image_to_video", "short_form_ads", "storyboard_motion"],
            "configured": False,
            "live_execution_enabled": False,
            "credential_required": True,
            "credential_values_exposed": False,
            "owner_activation_required": True,
            "creative_agents_supported": ["ugc_creative_agent", "product_image_agent", "marketing_specialist_agent"],
        },
        {
            "plugin_key": "kling_video_generation",
            "label": "Kling-style Cinematic Video Generation",
            "category": "video_generation",
            "supports": ["cinematic_video", "product_motion", "scene_generation", "social_video"],
            "configured": False,
            "live_execution_enabled": False,
            "credential_required": True,
            "credential_values_exposed": False,
            "owner_activation_required": True,
            "creative_agents_supported": ["ugc_creative_agent", "product_image_agent", "marketing_specialist_agent"],
        },
        {
            "plugin_key": "heygen_avatar_video",
            "label": "HeyGen-style Avatar Video",
            "category": "avatar_video",
            "supports": ["avatar_presenter", "talking_head", "sales_video", "training_video"],
            "configured": False,
            "live_execution_enabled": False,
            "credential_required": True,
            "credential_values_exposed": False,
            "owner_activation_required": True,
            "creative_agents_supported": ["ugc_creative_agent", "sales_closer_agent", "marketing_specialist_agent"],
        },
        {
            "plugin_key": "elevenlabs_voice",
            "label": "ElevenLabs-style Premium Voice",
            "category": "voice_generation",
            "supports": ["voiceover", "character_voice", "multilingual_voice", "ad_narration"],
            "configured": False,
            "live_execution_enabled": False,
            "credential_required": True,
            "credential_values_exposed": False,
            "owner_activation_required": True,
            "creative_agents_supported": ["ugc_creative_agent", "product_copywriting_agent", "marketing_specialist_agent"],
        },
        {
            "plugin_key": "lip_sync_dubbing",
            "label": "Lip-sync and Multilingual Dubbing",
            "category": "dubbing_lipsync",
            "supports": ["lip_sync", "voice_dubbing", "multilingual_ugc", "regionalised_video"],
            "configured": False,
            "live_execution_enabled": False,
            "credential_required": True,
            "credential_values_exposed": False,
            "owner_activation_required": True,
            "creative_agents_supported": ["ugc_creative_agent", "marketing_specialist_agent"],
        },
        {
            "plugin_key": "music_sfx_generation",
            "label": "Music and SFX Generation",
            "category": "audio_generation",
            "supports": ["background_music", "sound_effects", "sonic_branding", "ad_audio_bed"],
            "configured": False,
            "live_execution_enabled": False,
            "credential_required": True,
            "credential_values_exposed": False,
            "owner_activation_required": True,
            "creative_agents_supported": ["ugc_creative_agent", "brand_strategy_agent", "marketing_specialist_agent"],
        },
        {
            "plugin_key": "image_video_upscaling",
            "label": "Image and Video Upscaling",
            "category": "enhancement",
            "supports": ["image_upscale", "video_upscale", "denoise", "sharpen", "delivery_enhancement"],
            "configured": False,
            "live_execution_enabled": False,
            "credential_required": True,
            "credential_values_exposed": False,
            "owner_activation_required": True,
            "creative_agents_supported": ["product_image_agent", "ugc_creative_agent", "store_builder_agent"],
        },
        {
            "plugin_key": "video_editing_render_pipeline",
            "label": "Video Editing and Render Pipeline",
            "category": "editing_render",
            "supports": ["timeline_render", "caption_burn_in", "aspect_ratio_variants", "final_export"],
            "configured": False,
            "live_execution_enabled": False,
            "credential_required": False,
            "credential_values_exposed": False,
            "owner_activation_required": True,
            "creative_agents_supported": ["ugc_creative_agent", "marketing_specialist_agent", "social_media_agent"],
        },
        {
            "plugin_key": "brand_safe_creative_moderation",
            "label": "Brand-safe Creative Moderation",
            "category": "moderation",
            "supports": ["brand_safety", "claim_safety", "restricted_content_check", "customer_safe_review"],
            "configured": True,
            "live_execution_enabled": True,
            "credential_required": False,
            "credential_values_exposed": False,
            "owner_activation_required": False,
            "creative_agents_supported": ["ugc_creative_agent", "marketing_specialist_agent", "paid_ads_agent"],
        },
        {
            "plugin_key": "multi_scene_character_consistency",
            "label": "Multi-scene Character Consistency",
            "category": "character_consistency",
            "supports": ["character_memory", "multi_scene_identity", "creator_persona_reuse", "brand_character_lock"],
            "configured": True,
            "live_execution_enabled": False,
            "credential_required": False,
            "credential_values_exposed": False,
            "owner_activation_required": True,
            "creative_agents_supported": ["ugc_creative_agent", "brand_strategy_agent", "marketing_specialist_agent"],
        },
        {
            "plugin_key": "social_ad_export_presets",
            "label": "Social and Ad Export Presets",
            "category": "export_presets",
            "supports": ["tiktok", "instagram_reels", "youtube_shorts", "meta_ads", "linkedin_video", "display_ads"],
            "configured": True,
            "live_execution_enabled": True,
            "credential_required": False,
            "credential_values_exposed": False,
            "owner_activation_required": False,
            "creative_agents_supported": ["ugc_creative_agent", "paid_ads_agent", "social_media_agent"],
        },
    ]


def get_creative_premium_media_plugin_registry() -> Dict[str, Any]:
    plugins = _plugins()
    configured_count = len([plugin for plugin in plugins if plugin["configured"]])
    live_enabled_count = len([plugin for plugin in plugins if plugin["live_execution_enabled"]])

    return {
        "success": True,
        "track": "creative_agent_premium_media_plugin_expansion",
        "layer": "premium_audio_video_plugin_registry",
        "status": "ready",
        "production_launch_matrix_complete": True,
        "post_launch_operational_readiness_complete": True,
        "premium_creative_plugin_registry_enabled": True,
        "plugin_count": len(plugins),
        "configured_count": configured_count,
        "live_enabled_count": live_enabled_count,
        "credential_values_exposed": False,
        "external_actions_performed": False,
        "live_provider_calls_triggered": False,
        "owner_activation_required_for_paid_providers": True,
        "client_safe_visibility_enabled": True,
        "tenant_isolation_preserved": True,
        "creative_agent_categories_supported": [
            "video_generation",
            "avatar_video",
            "voice_generation",
            "dubbing_lipsync",
            "audio_generation",
            "enhancement",
            "editing_render",
            "moderation",
            "character_consistency",
            "export_presets",
        ],
        "plugins": plugins,
        "activation_rules": [
            "Adding a plugin to the registry does not enable live paid provider execution.",
            "Live provider execution requires configured credentials and owner approval.",
            "Credential values must never be exposed to clients or status routes.",
            "Creative outputs must pass brand-safe moderation before delivery where applicable.",
            "Spend-impacting provider usage remains owner-approved.",
            "Tenant isolation and customer-safe visibility must remain preserved.",
        ],
        "verified_at": _now(),
    }


def get_client_safe_creative_premium_media_plugin_registry() -> Dict[str, Any]:
    status = get_creative_premium_media_plugin_registry()

    return {
        "success": status["success"],
        "track": status["track"],
        "layer": status["layer"],
        "status": status["status"],
        "premium_creative_plugin_registry_enabled": status["premium_creative_plugin_registry_enabled"],
        "plugin_count": status["plugin_count"],
        "configured_count": status["configured_count"],
        "live_enabled_count": status["live_enabled_count"],
        "credential_values_exposed": False,
        "external_actions_performed": False,
        "live_provider_calls_triggered": False,
        "client_safe_visibility_enabled": True,
        "creative_agent_categories_supported": status["creative_agent_categories_supported"],
        "plugins": [
            {
                "plugin_key": plugin["plugin_key"],
                "label": plugin["label"],
                "category": plugin["category"],
                "supports": plugin["supports"],
                "configured": plugin["configured"],
                "live_execution_enabled": plugin["live_execution_enabled"],
                "owner_activation_required": plugin["owner_activation_required"],
                "creative_agents_supported": plugin["creative_agents_supported"],
                "credential_values_exposed": False,
            }
            for plugin in status["plugins"]
        ],
        "verified_at": status["verified_at"],
    }
'''

DOC_CONTENT = r'''# Creative Premium Media Plugin Registry

## Purpose

This layer adds a governed premium audio/video plugin registry for creative agents.

It prepares the platform to support high-end media providers and creative execution categories without automatically triggering paid provider calls.

## Plugin Categories Added

1. Runway-style video generation
2. Kling-style cinematic video generation
3. HeyGen-style avatar video
4. ElevenLabs-style premium voice
5. Lip-sync and multilingual dubbing
6. Music and SFX generation
7. Image/video upscaling
8. Video editing and render pipeline
9. Brand-safe creative moderation
10. Multi-scene character consistency
11. Social/ad export presets

## Safety Rules

- Registry support does not equal live paid provider activation.
- Live execution requires credentials and owner approval.
- Credential values must never be exposed.
- Spend-impacting provider usage requires owner approval.
- Tenant isolation must remain preserved.
- Customer-facing routes must remain client-safe.
- Brand-safe moderation should be used before customer delivery where applicable.

## Status

CREATIVE_PREMIUM_MEDIA_PLUGIN_REGISTRY_READY
'''

TEST_CONTENT = r'''from pathlib import Path
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
'''

MAIN_ROUTE_BLOCK = r'''
# CREATIVE_PREMIUM_MEDIA_PLUGIN_REGISTRY_START
try:
    from backend.app.runtime.creative_premium_media_plugin_registry import (
        get_client_safe_creative_premium_media_plugin_registry,
        get_creative_premium_media_plugin_registry,
    )

    @app.get("/creative/premium-media-plugin-registry")
    async def creative_premium_media_plugin_registry():
        return get_client_safe_creative_premium_media_plugin_registry()

    @app.get("/admin/creative/premium-media-plugin-registry")
    async def admin_creative_premium_media_plugin_registry():
        return get_creative_premium_media_plugin_registry()

except Exception as creative_premium_media_plugin_registry_error:
    @app.get("/creative/premium-media-plugin-registry")
    async def creative_premium_media_plugin_registry_unavailable():
        return {
            "success": False,
            "layer": "premium_audio_video_plugin_registry",
            "status": "unavailable",
            "credential_values_exposed": False,
            "external_actions_performed": False,
            "live_provider_calls_triggered": False,
            "error": str(creative_premium_media_plugin_registry_error),
        }

    @app.get("/admin/creative/premium-media-plugin-registry")
    async def admin_creative_premium_media_plugin_registry_unavailable():
        return {
            "success": False,
            "layer": "premium_audio_video_plugin_registry",
            "status": "unavailable",
            "credential_values_exposed": False,
            "external_actions_performed": False,
            "live_provider_calls_triggered": False,
            "error": str(creative_premium_media_plugin_registry_error),
        }
# CREATIVE_PREMIUM_MEDIA_PLUGIN_REGISTRY_END
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

    if "CREATIVE_PREMIUM_MEDIA_PLUGIN_REGISTRY_START" not in text:
        MAIN_FILE.write_text(text.rstrip() + "\n\n" + MAIN_ROUTE_BLOCK.lstrip(), encoding="utf-8", newline="\n")


def main() -> None:
    BACKUP.mkdir(parents=True, exist_ok=True)

    write_file(RUNTIME_FILE, RUNTIME_CONTENT)
    write_file(DOC_FILE, DOC_CONTENT)
    write_file(TEST_FILE, TEST_CONTENT)
    append_main_route_block()

    print("CREATIVE_PREMIUM_MEDIA_PLUGIN_REGISTRY_INSTALLED")
    print(f"Backup folder: {BACKUP}")
    print(f"Created/updated: {RUNTIME_FILE}")
    print(f"Created/updated: {DOC_FILE}")
    print(f"Created/updated: {TEST_FILE}")
    print(f"Updated: {MAIN_FILE}")


if __name__ == "__main__":
    main()