import httpx
import logging
import os

from ..base import BaseProvider, ProviderCategory, ProviderStatus

logger = logging.getLogger(__name__)

HIGGSFIELD_BASE = os.getenv("HIGGSFIELD_BASE_URL", "https://api.higgsfield.ai/v1")


class HiggsfieldProvider(BaseProvider):
    """Higgsfield UGC video generation provider."""

    def __init__(self):
        super().__init__(
            name="higgsfield",
            category=ProviderCategory.TEXT_TO_VIDEO,
            status=ProviderStatus.API_KEY_PENDING,
        )

    async def execute(
        self,
        prompt: str,
        duration: int = 30,
        aspect_ratio: str = "9:16",
        platform: str = "tiktok",
        tone: str = "professional",
        quality: str = "1080p",
        language: str = "en",
        **kwargs,
    ) -> dict:
        """Submit UGC video generation task to Higgsfield."""
        if not self.is_ready():
            return {"error": "Higgsfield API key not configured", "provider": "higgsfield"}

        payload = {
            "prompt": prompt,
            "duration": duration,
            "aspect_ratio": aspect_ratio,
            "platform": platform,
            "tone": tone,
            "quality": quality,
            "language": language,
            "model": "ugc_pro",
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{HIGGSFIELD_BASE}/generate/video",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()

            task_id = data.get("id") or data.get("task_id")
            return {
                "status": "queued",
                "provider": "higgsfield",
                "task_id": task_id,
                "poll_url": f"{HIGGSFIELD_BASE}/tasks/{task_id}",
                "message": "UGC video generation queued. Poll poll_url for completion.",
            }

        except httpx.HTTPStatusError as e:
            logger.error("Higgsfield API error %s: %s", e.response.status_code, e.response.text)
            return {"error": f"Higgsfield API error {e.response.status_code}", "provider": "higgsfield"}
        except Exception as e:
            logger.error("Higgsfield unexpected error: %s", e)
            return {"error": str(e), "provider": "higgsfield"}

    async def get_task_status(self, task_id: str) -> dict:
        """Poll Higgsfield for task completion."""
        if not self.is_ready():
            return {"error": "Higgsfield API key not configured"}
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(
                    f"{HIGGSFIELD_BASE}/tasks/{task_id}",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                    },
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error("Higgsfield task poll error: %s", e)
            return {"error": str(e)}

    def estimate_cost(self, duration: int = 30, **kwargs) -> float:
        """Estimate cost in credits. Higgsfield: ~2 credits/second."""
        return max(5.0, duration * 2.0)
