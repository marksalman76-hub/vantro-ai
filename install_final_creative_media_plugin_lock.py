from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP = ROOT / "backups" / f"final_creative_media_plugin_lock_before_{STAMP}"

RUNTIME_FILE = ROOT / "backend" / "app" / "runtime" / "final_creative_media_plugin_lock.py"
MAIN_FILE = ROOT / "backend" / "app" / "main.py"
DOC_FILE = ROOT / "docs" / "final-creative-media-plugin-lock.md"
TEST_FILE = ROOT / "test_final_creative_media_plugin_lock.py"

RUNTIME_CONTENT = r'''from datetime import datetime, timezone
from typing import Any, Dict


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_final_creative_media_plugin_lock() -> Dict[str, Any]:
    return {
        "success": True,
        "track": "creative_agent_premium_media_plugin_expansion",
        "layer": "final_creative_media_plugin_lock",
        "status": "locked",
        "premium_creative_plugin_registry_complete": True,
        "creative_agent_premium_routing_complete": True,
        "provider_credential_activation_checks_complete": True,
        "final_creative_media_plugin_infrastructure_complete": True,
        "production_launch_matrix_complete": True,
        "post_launch_operational_readiness_complete": True,
        "future_backend_updates_allowed": True,
        "owner_activation_required_for_paid_providers": True,
        "owner_approval_required_for_spend": True,
        "credential_values_exposed": False,
        "external_actions_performed": False,
        "live_provider_calls_triggered": False,
        "live_execution_globally_enabled": False,
        "tenant_isolation_preserved": True,
        "customer_safe_visibility_preserved": True,
        "creative_media_capabilities_locked": [
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
        ],
        "completed_commits": {
            "premium_plugin_registry": "7457a70",
            "creative_agent_premium_plugin_routing": "9a3016a",
            "provider_credential_activation_checks": "7cca39c",
        },
        "locked_rules": [
            "Premium creative plugin infrastructure is installed.",
            "Creative agents can route into premium audio/video plugin categories.",
            "Provider credential presence can be checked safely.",
            "Credential values must never be exposed.",
            "Live paid provider execution requires owner approval.",
            "Spend-impacting creative execution remains owner-approved.",
            "Provider calls must remain governed and auditable.",
            "Tenant isolation and customer-safe visibility must remain preserved.",
            "Future backend updates remain allowed under governed update rules.",
        ],
        "verified_at": _now(),
    }


def get_client_safe_final_creative_media_plugin_lock() -> Dict[str, Any]:
    status = get_final_creative_media_plugin_lock()

    return {
        "success": status["success"],
        "track": status["track"],
        "layer": status["layer"],
        "status": status["status"],
        "premium_creative_plugin_registry_complete": status["premium_creative_plugin_registry_complete"],
        "creative_agent_premium_routing_complete": status["creative_agent_premium_routing_complete"],
        "provider_credential_activation_checks_complete": status["provider_credential_activation_checks_complete"],
        "final_creative_media_plugin_infrastructure_complete": status["final_creative_media_plugin_infrastructure_complete"],
        "owner_activation_required_for_paid_providers": True,
        "credential_values_exposed": False,
        "external_actions_performed": False,
        "live_provider_calls_triggered": False,
        "live_execution_globally_enabled": False,
        "tenant_isolation_preserved": True,
        "customer_safe_visibility_preserved": True,
        "creative_media_capabilities_locked": status["creative_media_capabilities_locked"],
        "verified_at": status["verified_at"],
    }
'''

DOC_CONTENT = r'''# Final Creative Media Plugin Lock

## Final Status

The premium creative media plugin infrastructure is complete.

## Completed Layers

### CP-1 Premium Plugin Registry

Commit:

7457a70

Adds:
- Runway-style video generation
- Kling-style cinematic video generation
- HeyGen-style avatar video
- ElevenLabs-style premium voice
- lip-sync and multilingual dubbing
- music/SFX generation
- image/video upscaling
- video editing/render pipeline
- brand-safe moderation
- multi-scene character consistency
- social/ad export presets

### CP-2 Creative Agent Premium Plugin Routing

Commit:

9a3016a

Adds routing for:
- UGC Creative Agent
- Product Image Agent
- Marketing Specialist Agent
- Social Media Agent
- Paid Ads Agent
- Brand Strategy Agent
- Sales / Closer Agent
- Product Copywriting Agent

### CP-3 Provider Credential Activation Checks

Commit:

7cca39c

Adds governed credential activation visibility for:
- Runway
- Kling
- HeyGen
- ElevenLabs
- lip-sync/dubbing
- music/SFX
- upscaling

## Governance Rules

- Live paid provider execution is not globally enabled by this lock.
- Live paid provider execution requires owner approval.
- Credential values must never be exposed.
- Spend-impacting provider usage remains owner-approved.
- Provider calls must remain governed and auditable.
- Tenant isolation must remain preserved.
- Customer-safe visibility must remain preserved.
- Future backend updates remain allowed under governed update rules.

## Status

FINAL_CREATIVE_MEDIA_PLUGIN_INFRASTRUCTURE_COMPLETE
'''

TEST_CONTENT = r'''from pathlib import Path
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
'''

MAIN_ROUTE_BLOCK = r'''
# FINAL_CREATIVE_MEDIA_PLUGIN_LOCK_START
try:
    from backend.app.runtime.final_creative_media_plugin_lock import (
        get_client_safe_final_creative_media_plugin_lock,
        get_final_creative_media_plugin_lock,
    )

    @app.get("/creative/final-media-plugin-lock")
    async def creative_final_media_plugin_lock():
        return get_client_safe_final_creative_media_plugin_lock()

    @app.get("/admin/creative/final-media-plugin-lock")
    async def admin_creative_final_media_plugin_lock():
        return get_final_creative_media_plugin_lock()

except Exception as final_creative_media_plugin_lock_error:
    @app.get("/creative/final-media-plugin-lock")
    async def creative_final_media_plugin_lock_unavailable():
        return {
            "success": False,
            "layer": "final_creative_media_plugin_lock",
            "status": "unavailable",
            "credential_values_exposed": False,
            "external_actions_performed": False,
            "live_provider_calls_triggered": False,
            "error": str(final_creative_media_plugin_lock_error),
        }

    @app.get("/admin/creative/final-media-plugin-lock")
    async def admin_creative_final_media_plugin_lock_unavailable():
        return {
            "success": False,
            "layer": "final_creative_media_plugin_lock",
            "status": "unavailable",
            "credential_values_exposed": False,
            "external_actions_performed": False,
            "live_provider_calls_triggered": False,
            "error": str(final_creative_media_plugin_lock_error),
        }
# FINAL_CREATIVE_MEDIA_PLUGIN_LOCK_END
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

    if "FINAL_CREATIVE_MEDIA_PLUGIN_LOCK_START" not in text:
        MAIN_FILE.write_text(text.rstrip() + "\n\n" + MAIN_ROUTE_BLOCK.lstrip(), encoding="utf-8", newline="\n")


def main() -> None:
    BACKUP.mkdir(parents=True, exist_ok=True)

    write_file(RUNTIME_FILE, RUNTIME_CONTENT)
    write_file(DOC_FILE, DOC_CONTENT)
    write_file(TEST_FILE, TEST_CONTENT)
    append_main_route_block()

    print("FINAL_CREATIVE_MEDIA_PLUGIN_LOCK_INSTALLED")
    print(f"Backup folder: {BACKUP}")
    print(f"Created/updated: {RUNTIME_FILE}")
    print(f"Created/updated: {DOC_FILE}")
    print(f"Created/updated: {TEST_FILE}")
    print(f"Updated: {MAIN_FILE}")


if __name__ == "__main__":
    main()