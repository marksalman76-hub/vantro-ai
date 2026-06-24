import logging
from typing import Optional

from .base import ProviderCategory
from .registry import registry

logger = logging.getLogger(__name__)


class ProviderRouter:
    """Routes media requests to the appropriate active provider."""

    def __init__(self):
        self.registry = registry

    async def route_avatar_video(
        self,
        script: str,
        avatar_id: Optional[str] = None,
        voice_id: Optional[str] = None,
        **kwargs,
    ) -> dict:
        providers = self.registry.get_active_by_category(ProviderCategory.AVATAR_VIDEO)
        if not providers:
            return {"error": "No active avatar video provider. Configure HEYGEN_API_KEY."}
        return await providers[0].execute(
            script=script,
            avatar_id=avatar_id,
            voice_id=voice_id,
            **kwargs,
        )

    async def route_voice(
        self,
        text: str,
        voice_id: Optional[str] = None,
        language: str = "en",
        **kwargs,
    ) -> dict:
        providers = self.registry.get_active_by_category(ProviderCategory.VOICE)
        if not providers:
            return {"error": "No active voice provider. Configure ELEVENLABS_API_KEY."}
        kwargs_with_voice = {**kwargs}
        if voice_id:
            kwargs_with_voice["voice_id"] = voice_id
        return await providers[0].execute(text=text, language=language, **kwargs_with_voice)

    async def route_text_to_video(
        self,
        prompt: str,
        duration: int = 5,
        **kwargs,
    ) -> dict:
        providers = self.registry.get_active_by_category(ProviderCategory.TEXT_TO_VIDEO)
        if not providers:
            return {"error": "No active text-to-video provider. Configure RUNWAY_API_KEY."}
        return await providers[0].execute(prompt=prompt, duration=duration, **kwargs)

    async def route_music(
        self,
        description: str,
        duration: int = 60,
        **kwargs,
    ) -> dict:
        providers = self.registry.get_active_by_category(ProviderCategory.MUSIC)
        if not providers:
            return {"error": "No active music provider. Configure MUBERT_API_KEY."}
        return await providers[0].execute(description=description, duration=duration, **kwargs)

    async def route_captions(
        self,
        audio_url: str,
        language: str = "en",
        **kwargs,
    ) -> dict:
        providers = self.registry.get_active_by_category(ProviderCategory.CAPTIONS)
        if not providers:
            return {"error": "No active caption provider. Configure ASSEMBLYAI_API_KEY."}
        return await providers[0].execute(audio_file=audio_url, language=language, **kwargs)

    def estimate_cost(self, category: ProviderCategory, **kwargs) -> float:
        providers = self.registry.get_active_by_category(category)
        if not providers:
            return 0.0
        return providers[0].estimate_cost(**kwargs)

    def provider_status(self) -> dict:
        return self.registry.status_report()

    def available_categories(self) -> list[str]:
        """Return categories that have at least one active provider."""
        return [
            cat.value
            for cat in ProviderCategory
            if self.registry.get_active_by_category(cat)
        ]


# Global router instance
router = ProviderRouter()
