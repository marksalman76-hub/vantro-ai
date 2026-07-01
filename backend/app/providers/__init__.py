import os
import logging

from .base import BaseProvider, ProviderCategory, ProviderStatus
from .registry import registry
from .router import router

logger = logging.getLogger(__name__)

__all__ = [
    "BaseProvider",
    "ProviderCategory",
    "ProviderStatus",
    "registry",
    "router",
    "init_providers",
]


def init_providers() -> None:
    """
    Load platform API keys from environment and register active providers.
    Called once at app startup inside the lifespan context manager.
    Silently skips any provider whose key is absent.
    """
    from .adapters import (
        SynthesiaProvider,
        ElevenLabsProvider,
        MubertProvider,
        AssemblyAIProvider,
        PikaProvider,
    )

    _register_if_key("ELEVENLABS_API_KEY", ElevenLabsProvider, "ElevenLabs (voice)")
    _register_if_key("MUBERT_API_KEY", MubertProvider, "Mubert (music)")
    _register_if_key("ASSEMBLYAI_API_KEY", AssemblyAIProvider, "AssemblyAI (captions)")
    _register_if_key("PIKA_API_KEY", PikaProvider, "Pika (text-to-video alt)")

    active = [name for name, p in registry.providers.items() if p.is_ready()]
    if active:
        logger.info("Media providers active: %s", ", ".join(active))
    else:
        logger.info("No media provider API keys configured — creative agents will return briefs only")


def _register_if_key(env_var: str, provider_cls, label: str) -> None:
    key = os.getenv(env_var, "").strip()
    if not key:
        return
    try:
        provider = provider_cls()
        provider.set_api_key(key)
        registry.register(provider)
        logger.info("Provider registered: %s", label)
    except Exception as e:
        logger.warning("Failed to register provider %s: %s", label, e)
