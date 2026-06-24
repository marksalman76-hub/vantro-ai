import httpx
import logging

from ..base import BaseProvider, ProviderCategory, ProviderStatus

logger = logging.getLogger(__name__)

HEYGEN_BASE = "https://api.heygen.com"
DEFAULT_AVATAR_ID = "Daisy-inskirt-20220818"
DEFAULT_VOICE_ID = "1bd001e7e50f421d891986aad5158bc8"  # HeyGen built-in English voice


class SynthesiaProvider(BaseProvider):
    """
    Avatar video provider — powered by HeyGen API (HEYGEN_API_KEY).
    Class kept as SynthesiaProvider for registry compatibility.
    """

    def __init__(self):
        super().__init__(
            name="synthesia",
            category=ProviderCategory.AVATAR_VIDEO,
            status=ProviderStatus.API_KEY_PENDING,
        )

    async def execute(
        self,
        script: str,
        avatar_id: str = DEFAULT_AVATAR_ID,
        voice_id: str = DEFAULT_VOICE_ID,
        width: int = 1280,
        height: int = 720,
        test_mode: bool = True,
        **kwargs,
    ) -> dict:
        if not self.is_ready():
            return {"error": "HeyGen API key not configured", "provider": "heygen"}

        payload = {
            "video_inputs": [
                {
                    "character": {
                        "type": "avatar",
                        "avatar_id": avatar_id,
                        "avatar_style": "normal",
                    },
                    "voice": {
                        "type": "text",
                        "input_text": script,
                        "voice_id": voice_id,
                    },
                }
            ],
            "dimension": {"width": width, "height": height},
            "test": test_mode,
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{HEYGEN_BASE}/v2/video/generate",
                    headers={
                        "X-Api-Key": self.api_key,
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()

            video_id = data.get("data", {}).get("video_id")
            return {
                "status": "pending",
                "provider": "heygen",
                "video_id": video_id,
                "poll_url": f"{HEYGEN_BASE}/v1/video_status.get?video_id={video_id}",
                "message": "Video generation started. Poll poll_url for completion status.",
                "test_mode": test_mode,
            }

        except httpx.HTTPStatusError as e:
            logger.error("HeyGen API error %s: %s", e.response.status_code, e.response.text)
            return {"error": f"HeyGen API error {e.response.status_code}", "provider": "heygen"}
        except Exception as e:
            logger.error("HeyGen unexpected error: %s", e)
            return {"error": str(e), "provider": "heygen"}

    async def get_video_status(self, video_id: str) -> dict:
        """Poll HeyGen for video completion status."""
        if not self.is_ready():
            return {"error": "HeyGen API key not configured"}
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(
                    f"{HEYGEN_BASE}/v1/video_status.get",
                    params={"video_id": video_id},
                    headers={"X-Api-Key": self.api_key},
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error("HeyGen status poll error: %s", e)
            return {"error": str(e)}

    def estimate_cost(self, duration_seconds: int = 60, **kwargs) -> float:
        # HeyGen: ~$0.24/min on Creator plan → 24 credits per minute
        minutes = duration_seconds / 60
        return max(1.0, minutes * 24.0)
