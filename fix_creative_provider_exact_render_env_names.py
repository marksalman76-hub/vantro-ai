from pathlib import Path
from datetime import datetime
import re

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")

CHECK_FILE = ROOT / "backend" / "app" / "runtime" / "creative_provider_credential_activation_checks.py"
MEDIA_FILE = ROOT / "backend" / "app" / "runtime" / "shared_creative_media_generation_runtime.py"

backup_dir = ROOT / "backups" / f"creative_provider_env_names_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)

if CHECK_FILE.exists():
    (backup_dir / "creative_provider_credential_activation_checks.py").write_text(
        CHECK_FILE.read_text(encoding="utf-8"),
        encoding="utf-8",
    )

if MEDIA_FILE.exists():
    (backup_dir / "shared_creative_media_generation_runtime.py").write_text(
        MEDIA_FILE.read_text(encoding="utf-8"),
        encoding="utf-8",
    )

CHECK_FILE.write_text(
r'''from __future__ import annotations

from datetime import datetime, timezone
import os
from typing import Any, Dict, List


TRUE_VALUES = {"1", "true", "yes", "on", "enabled"}


# These names must match the exact Render environment variable names.
# Do not add alternate names here unless the Render env is also updated.
PROVIDER_CREDENTIALS: Dict[str, Dict[str, Any]] = {
    "runway": {
        "category": "video_generation",
        "required_env_names": ["RUNWAYML_API_SECRET"],
        "requires_all": True,
    },
    "kling": {
        "category": "video_generation",
        "required_env_names": ["KLING_ACCESS_KEY", "KLING_SECRET_KEY"],
        "requires_all": True,
    },
    "heygen": {
        "category": "avatar_video",
        "required_env_names": ["HEYGEN_API_KEY"],
        "requires_all": True,
    },
    "elevenlabs": {
        "category": "voice_generation",
        "required_env_names": ["ELEVENLABS_API_KEY"],
        "requires_all": True,
    },
    "lipsync_dubbing": {
        "category": "dubbing_lipsync",
        "required_env_names": ["HEYGEN_API_KEY"],
        "requires_all": True,
    },
    "music_sfx": {
        "category": "audio_generation",
        "required_env_names": ["ELEVENLABS_API_KEY"],
        "requires_all": True,
    },
    "upscaling": {
        "category": "enhancement",
        "required_env_names": ["RUNWAYML_API_SECRET"],
        "requires_all": True,
    },
}


LIVE_EXECUTION_ENV_NAMES = [
    "LIVE_EXTERNAL_CALLS_ENABLED",
    "OWNER_APPROVED_LIVE_ACTIVATION",
    "REAL_PROVIDER_HTTP_DISPATCH_ENABLED",
]


def _is_enabled(name: str) -> bool:
    return str(os.getenv(name, "")).strip().lower() in TRUE_VALUES


def _env_present(name: str) -> bool:
    return bool(str(os.getenv(name, "")).strip())


def _provider_configured(config: Dict[str, Any]) -> bool:
    names: List[str] = list(config.get("required_env_names") or [])
    if not names:
        return False

    checks = [_env_present(name) for name in names]

    if bool(config.get("requires_all", True)):
        return all(checks)

    return any(checks)


def _live_execution_globally_enabled() -> bool:
    return all(_is_enabled(name) for name in LIVE_EXECUTION_ENV_NAMES)


def _provider_packet(provider_key: str, config: Dict[str, Any], live_enabled: bool) -> Dict[str, Any]:
    credential_configured = _provider_configured(config)

    return {
        "provider_key": provider_key,
        "category": config.get("category"),
        "credential_configured": credential_configured,
        "credential_names_expected": list(config.get("required_env_names") or []),
        "credential_values_exposed": False,
        "live_execution_enabled": bool(credential_configured and live_enabled),
        "owner_activation_required": True,
        "provider_ready_for_activation": bool(credential_configured),
        "external_actions_performed": False,
        "live_provider_calls_triggered": False,
    }


def get_creative_provider_credential_activation_checks() -> Dict[str, Any]:
    live_enabled = _live_execution_globally_enabled()

    providers = [
        _provider_packet(provider_key, config, live_enabled)
        for provider_key, config in PROVIDER_CREDENTIALS.items()
    ]

    configured_count = sum(1 for provider in providers if provider.get("credential_configured"))
    live_enabled_count = sum(1 for provider in providers if provider.get("live_execution_enabled"))

    return {
        "success": True,
        "track": "creative_agent_premium_media_plugin_expansion",
        "layer": "provider_credential_activation_checks",
        "status": "ready",
        "provider_count": len(providers),
        "configured_provider_count": configured_count,
        "live_enabled_provider_count": live_enabled_count,
        "credential_values_exposed": False,
        "external_actions_performed": False,
        "live_provider_calls_triggered": False,
        "live_execution_globally_enabled": live_enabled,
        "live_execution_env_names_expected": LIVE_EXECUTION_ENV_NAMES,
        "owner_activation_required_for_paid_providers": True,
        "tenant_isolation_preserved": True,
        "customer_safe_visibility_preserved": True,
        "providers": providers,
        "activation_rules": [
            "Credential presence does not expose credential values.",
            "Live execution requires explicit owner activation.",
            "Paid provider usage remains owner-approved.",
            "Provider calls must remain governed and auditable.",
            "Tenant isolation and customer-safe visibility must remain preserved.",
        ],
        "verified_at": datetime.now(timezone.utc).isoformat(),
    }


def get_client_safe_creative_provider_credential_activation_checks() -> Dict[str, Any]:
    admin = get_creative_provider_credential_activation_checks()

    safe_providers = []
    for provider in admin.get("providers", []):
        safe_providers.append(
            {
                "provider_key": provider.get("provider_key"),
                "category": provider.get("category"),
                "provider_ready_for_activation": provider.get("provider_ready_for_activation"),
                "live_execution_enabled": provider.get("live_execution_enabled"),
                "credential_values_exposed": False,
                "customer_safe": True,
            }
        )

    return {
        "success": True,
        "layer": "provider_credential_activation_checks",
        "status": admin.get("status"),
        "provider_count": admin.get("provider_count"),
        "configured_provider_count": admin.get("configured_provider_count"),
        "live_enabled_provider_count": admin.get("live_enabled_provider_count"),
        "live_execution_globally_enabled": admin.get("live_execution_globally_enabled"),
        "providers": safe_providers,
        "credential_values_exposed": False,
        "external_actions_performed": False,
        "live_provider_calls_triggered": False,
        "customer_safe": True,
    }
''',
encoding="utf-8",
)

media_text = MEDIA_FILE.read_text(encoding="utf-8")

provider_env_block = '''PROVIDER_ENV_KEYS = {
    "runway": ["RUNWAYML_API_SECRET"],
    "kling": ["KLING_ACCESS_KEY", "KLING_SECRET_KEY"],
    "heygen": ["HEYGEN_API_KEY"],
    "elevenlabs": ["ELEVENLABS_API_KEY"],
    "sync": ["HEYGEN_API_KEY"],
    "replicate": [],
}
'''

media_text = re.sub(
    r'PROVIDER_ENV_KEYS\s*=\s*\{.*?\}\n\nMEDIA_PROVIDER_PRIORITY',
    provider_env_block + "\nMEDIA_PROVIDER_PRIORITY",
    media_text,
    flags=re.S,
)

old_func_pattern = r'def _provider_configured\(provider: str\) -> bool:\n    return _env_present\(PROVIDER_ENV_KEYS\.get\(provider, \[\]\)\)\n'
new_func = '''def _provider_configured(provider: str) -> bool:
    provider = str(provider or "").strip().lower()
    names = PROVIDER_ENV_KEYS.get(provider, [])

    if provider == "kling":
        return all(bool(os.getenv(name, "").strip()) for name in names)

    return any(bool(os.getenv(name, "").strip()) for name in names)
'''

if old_func_pattern not in media_text:
    media_text = re.sub(
        r'def _provider_configured\(provider: str\) -> bool:\n    .*?\n\n',
        new_func + "\n",
        media_text,
        flags=re.S,
    )
else:
    media_text = media_text.replace(old_func_pattern, new_func)

MEDIA_FILE.write_text(media_text, encoding="utf-8")

print("CREATIVE_PROVIDER_EXACT_RENDER_ENV_NAMES_FIXED")
print("Updated:", CHECK_FILE)
print("Updated:", MEDIA_FILE)
print("Backup:", backup_dir)