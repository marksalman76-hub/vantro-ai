import httpx
import base64
import logging

from ..base import BaseProvider, ProviderCategory, ProviderStatus

logger = logging.getLogger(__name__)

ELEVENLABS_BASE = "https://api.elevenlabs.io/v1"
DEFAULT_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # Rachel — neutral, clear


class ElevenLabsProvider(BaseProvider):
    """ElevenLabs text-to-speech provider."""

    def __init__(self):
        super().__init__(
            name="elevenlabs",
            category=ProviderCategory.VOICE,
            status=ProviderStatus.API_KEY_PENDING,
        )

    async def execute(
        self,
        text: str,
        voice_id: str = DEFAULT_VOICE_ID,
        language: str = "en",
        stability: float = 0.5,
        similarity_boost: float = 0.75,
        **kwargs,
    ) -> dict:
        if not self.is_ready():
            return {"error": "ElevenLabs API key not configured", "provider": "elevenlabs"}

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{ELEVENLABS_BASE}/text-to-speech/{voice_id}",
                    headers={
                        "xi-api-key": self.api_key,
                        "Content-Type": "application/json",
                    },
                    json={
                        "text": text,
                        "model_id": "eleven_multilingual_v2",
                        "voice_settings": {
                            "stability": stability,
                            "similarity_boost": similarity_boost,
                        },
                    },
                )
                response.raise_for_status()

            audio_b64 = base64.b64encode(response.content).decode()
            return {
                "status": "success",
                "provider": "elevenlabs",
                "voice_id": voice_id,
                "audio_base64": audio_b64,
                "content_type": "audio/mpeg",
                "character_count": len(text),
            }

        except httpx.HTTPStatusError as e:
            logger.error("ElevenLabs API error %s: %s", e.response.status_code, e.response.text)
            return {"error": f"ElevenLabs API error {e.response.status_code}", "provider": "elevenlabs"}
        except Exception as e:
            logger.error("ElevenLabs unexpected error: %s", e)
            return {"error": str(e), "provider": "elevenlabs"}

    def estimate_cost(self, character_count: int = 1000, **kwargs) -> float:
        # $0.30 per 1000 chars on Creator plan → 30 credits per 1000 chars
        return max(1.0, (character_count / 1000) * 30.0)
