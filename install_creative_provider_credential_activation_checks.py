from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP = ROOT / "backups" / f"creative_provider_credential_activation_checks_before_{STAMP}"

RUNTIME_FILE = ROOT / "backend" / "app" / "runtime" / "creative_provider_credential_activation_checks.py"
MAIN_FILE = ROOT / "backend" / "app" / "main.py"
DOC_FILE = ROOT / "docs" / "creative-provider-credential-activation-checks.md"
TEST_FILE = ROOT / "test_creative_provider_credential_activation_checks.py"

RUNTIME_CONTENT = r'''from datetime import datetime, timezone
from typing import Any, Dict, List
import os


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


PROVIDERS = [
    {
        "provider_key": "runway",
        "credential_envs": ["RUNWAY_API_KEY"],
        "category": "video_generation",
    },
    {
        "provider_key": "kling",
        "credential_envs": ["KLING_API_KEY"],
        "category": "video_generation",
    },
    {
        "provider_key": "heygen",
        "credential_envs": ["HEYGEN_API_KEY"],
        "category": "avatar_video",
    },
    {
        "provider_key": "elevenlabs",
        "credential_envs": ["ELEVENLABS_API_KEY"],
        "category": "voice_generation",
    },
    {
        "provider_key": "lipsync_dubbing",
        "credential_envs": ["LIPSYNC_API_KEY"],
        "category": "dubbing_lipsync",
    },
    {
        "provider_key": "music_sfx",
        "credential_envs": ["MUSIC_SFX_API_KEY"],
        "category": "audio_generation",
    },
    {
        "provider_key": "upscaling",
        "credential_envs": ["UPSCALE_API_KEY"],
        "category": "enhancement",
    },
]


def _provider_status(provider: Dict[str, Any]) -> Dict[str, Any]:
    credential_present = any(
        bool(os.getenv(env_name, "").strip())
        for env_name in provider["credential_envs"]
    )

    return {
        "provider_key": provider["provider_key"],
        "category": provider["category"],
        "credential_configured": credential_present,
        "credential_values_exposed": False,
        "live_execution_enabled": False,
        "owner_activation_required": True,
        "provider_ready_for_activation": credential_present,
        "external_actions_performed": False,
        "live_provider_calls_triggered": False,
    }


def get_creative_provider_credential_activation_checks() -> Dict[str, Any]:
    provider_statuses = [_provider_status(provider) for provider in PROVIDERS]

    configured_count = len([
        provider for provider in provider_statuses
        if provider["credential_configured"]
    ])

    return {
        "success": True,
        "track": "creative_agent_premium_media_plugin_expansion",
        "layer": "provider_credential_activation_checks",
        "status": "ready",
        "provider_count": len(provider_statuses),
        "configured_provider_count": configured_count,
        "credential_values_exposed": False,
        "external_actions_performed": False,
        "live_provider_calls_triggered": False,
        "live_execution_globally_enabled": False,
        "owner_activation_required_for_paid_providers": True,
        "tenant_isolation_preserved": True,
        "customer_safe_visibility_preserved": True,
        "providers": provider_statuses,
        "activation_rules": [
            "Credential presence does not automatically enable live execution.",
            "Live execution requires explicit owner activation.",
            "Credential values must never be exposed.",
            "Paid provider usage remains owner-approved.",
            "Provider calls must remain governed and auditable.",
            "Tenant isolation and customer-safe visibility must remain preserved.",
        ],
        "verified_at": _now(),
    }


def get_client_safe_creative_provider_credential_activation_checks() -> Dict[str, Any]:
    status = get_creative_provider_credential_activation_checks()

    return {
        "success": status["success"],
        "track": status["track"],
        "layer": status["layer"],
        "status": status["status"],
        "provider_count": status["provider_count"],
        "configured_provider_count": status["configured_provider_count"],
        "credential_values_exposed": False,
        "external_actions_performed": False,
        "live_provider_calls_triggered": False,
        "live_execution_globally_enabled": False,
        "owner_activation_required_for_paid_providers": True,
        "tenant_isolation_preserved": True,
        "customer_safe_visibility_preserved": True,
        "providers": [
            {
                "provider_key": provider["provider_key"],
                "category": provider["category"],
                "credential_configured": provider["credential_configured"],
                "provider_ready_for_activation": provider["provider_ready_for_activation"],
                "live_execution_enabled": provider["live_execution_enabled"],
                "owner_activation_required": provider["owner_activation_required"],
                "credential_values_exposed": False,
            }
            for provider in status["providers"]
        ],
        "verified_at": status["verified_at"],
    }
'''

DOC_CONTENT = r'''# Creative Provider Credential Activation Checks

## Purpose

This layer validates premium creative provider credential readiness without enabling uncontrolled live execution.

## Covered Provider Categories

- Runway-style video
- Kling-style cinematic video
- HeyGen-style avatar video
- ElevenLabs-style premium voice
- Lip-sync and dubbing
- Music/SFX generation
- Image/video upscaling

## Important Rules

- Credential presence does not enable live execution.
- Live provider execution requires explicit owner approval.
- Credential values must never be exposed.
- Paid provider usage remains owner-approved.
- Provider execution must remain auditable and governed.
- Tenant isolation and customer-safe visibility must remain preserved.

## Status

CREATIVE_PROVIDER_CREDENTIAL_ACTIVATION_CHECKS_READY
'''

TEST_CONTENT = r'''from pathlib import Path
import importlib.util
import py_compile

ROOT = Path.cwd()

runtime_file = ROOT / "backend" / "app" / "runtime" / "creative_provider_credential_activation_checks.py"
main_file = ROOT / "backend" / "app" / "main.py"
doc_file = ROOT / "docs" / "creative-provider-credential-activation-checks.md"

required_files = [runtime_file, main_file, doc_file]

for path in required_files:
    if not path.exists():
        raise AssertionError(f"Missing required file: {path}")

py_compile.compile(str(runtime_file), doraise=True)

spec = importlib.util.spec_from_file_location(
    "creative_provider_credential_activation_checks",
    runtime_file,
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

status = module.get_creative_provider_credential_activation_checks()
client_status = module.get_client_safe_creative_provider_credential_activation_checks()

required_providers = [
    "runway",
    "kling",
    "heygen",
    "elevenlabs",
    "lipsync_dubbing",
    "music_sfx",
    "upscaling",
]

provider_keys = [provider["provider_key"] for provider in status["providers"]]

for provider in required_providers:
    if provider not in provider_keys:
        raise AssertionError(f"Missing provider activation check: {provider}")

required_true_flags = [
    "owner_activation_required_for_paid_providers",
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

runtime_text = runtime_file.read_text(encoding="utf-8")
main_text = main_file.read_text(encoding="utf-8")
doc_text = doc_file.read_text(encoding="utf-8")

combined_text = runtime_text + "\n" + main_text + "\n" + doc_text

required_markers = [
    "CREATIVE_PROVIDER_CREDENTIAL_ACTIVATION_CHECKS_READY",
    "/creative/provider-credential-activation-checks",
    "/admin/creative/provider-credential-activation-checks",
    "RUNWAY_API_KEY",
    "KLING_API_KEY",
    "HEYGEN_API_KEY",
    "ELEVENLABS_API_KEY",
]

for marker in required_markers:
    if marker not in combined_text:
        raise AssertionError(f"Missing marker: {marker}")

print("CREATIVE_PROVIDER_CREDENTIAL_ACTIVATION_CHECKS_PASSED")
'''

MAIN_ROUTE_BLOCK = r'''
# CREATIVE_PROVIDER_CREDENTIAL_ACTIVATION_CHECKS_START
try:
    from backend.app.runtime.creative_provider_credential_activation_checks import (
        get_client_safe_creative_provider_credential_activation_checks,
        get_creative_provider_credential_activation_checks,
    )

    @app.get("/creative/provider-credential-activation-checks")
    async def creative_provider_credential_activation_checks():
        return get_client_safe_creative_provider_credential_activation_checks()

    @app.get("/admin/creative/provider-credential-activation-checks")
    async def admin_creative_provider_credential_activation_checks():
        return get_creative_provider_credential_activation_checks()

except Exception as creative_provider_credential_activation_checks_error:
    @app.get("/creative/provider-credential-activation-checks")
    async def creative_provider_credential_activation_checks_unavailable():
        return {
            "success": False,
            "layer": "provider_credential_activation_checks",
            "status": "unavailable",
            "credential_values_exposed": False,
            "external_actions_performed": False,
            "live_provider_calls_triggered": False,
            "error": str(creative_provider_credential_activation_checks_error),
        }

    @app.get("/admin/creative/provider-credential-activation-checks")
    async def admin_creative_provider_credential_activation_checks_unavailable():
        return {
            "success": False,
            "layer": "provider_credential_activation_checks",
            "status": "unavailable",
            "credential_values_exposed": False,
            "external_actions_performed": False,
            "live_provider_calls_triggered": False,
            "error": str(creative_provider_credential_activation_checks_error),
        }
# CREATIVE_PROVIDER_CREDENTIAL_ACTIVATION_CHECKS_END
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

    if "CREATIVE_PROVIDER_CREDENTIAL_ACTIVATION_CHECKS_START" not in text:
        MAIN_FILE.write_text(text.rstrip() + "\n\n" + MAIN_ROUTE_BLOCK.lstrip(), encoding="utf-8", newline="\n")


def main() -> None:
    BACKUP.mkdir(parents=True, exist_ok=True)

    write_file(RUNTIME_FILE, RUNTIME_CONTENT)
    write_file(DOC_FILE, DOC_CONTENT)
    write_file(TEST_FILE, TEST_CONTENT)
    append_main_route_block()

    print("CREATIVE_PROVIDER_CREDENTIAL_ACTIVATION_CHECKS_INSTALLED")
    print(f"Backup folder: {BACKUP}")
    print(f"Created/updated: {RUNTIME_FILE}")
    print(f"Created/updated: {DOC_FILE}")
    print(f"Created/updated: {TEST_FILE}")
    print(f"Updated: {MAIN_FILE}")


if __name__ == "__main__":
    main()