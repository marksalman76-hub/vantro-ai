# Provider routing logic

from .base import ProviderCategory, BaseProvider
from .registry import registry
from typing import Optional, List

class ProviderRouter:
    """Routes media requests to appropriate providers"""

    def __init__(self):
        self.registry = registry

    async def route_avatar_video(
        self, 
        script: str,
        avatar_id: Optional[str] = None,
        voice_id: Optional[str] = None,
        **kwargs
    ) -> dict:
        """Route avatar video request to Synthesia"""
        providers = self.registry.get_active_by_category(ProviderCategory.AVATAR_VIDEO)
        if not providers:
            return {"error": "No active avatar video providers"}
ECHO is on.
        # Use first available provider (Synthesia preferred)
        provider = providers[0]
        return await provider.execute(
            script=script,
            avatar_id=avatar_id,
            voice_id=voice_id,
            **kwargs
        )

    async def route_voice(
        self,
        text: str,
        language: str = "en",
        **kwargs
    ) -> dict:
        """Route voice generation to ElevenLabs"""
        providers = self.registry.get_active_by_category(ProviderCategory.VOICE)
        if not providers:
            return {"error": "No active voice providers"}
ECHO is on.
        provider = providers[0]
        return await provider.execute(text=text, language=language, **kwargs)

    async def route_music(self, description: str, duration: int, **kwargs) -> dict:
        """Route music generation to Mubert"""
        providers = self.registry.get_active_by_category(ProviderCategory.MUSIC)
        if not providers:
            return {"error": "No active music providers"}
ECHO is on.
        provider = providers[0]
        return await provider.execute(description=description, duration=duration, **kwargs)

    async def route_captions(self, audio_file: str, language: str = "en", **kwargs) -> dict:
        """Route caption generation to AssemblyAI"""
        providers = self.registry.get_active_by_category(ProviderCategory.CAPTIONS)
        if not providers:
            return {"error": "No active caption providers"}
ECHO is on.
        provider = providers[0]
        return await provider.execute(audio_file=audio_file, language=language, **kwargs)

    def estimate_cost(
        self,
        category: ProviderCategory,
        **kwargs
    ) -> float:
        """Estimate cost for a request"""
        providers = self.registry.get_active_by_category(category)
        if not providers:
            return 0.0
ECHO is on.
        # Use first provider's estimate
        return providers[0].estimate_cost(**kwargs)

    def provider_status(self) -> dict:
        """Get status of all providers"""
        return self.registry.status_report()

# Global router instance
router = ProviderRouter()
