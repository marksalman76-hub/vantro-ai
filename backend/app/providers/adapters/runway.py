import httpx
import logging

from ..base import BaseProvider, ProviderCategory, ProviderStatus

logger = logging.getLogger(__name__)

RUNWAY_BASE = "https://api.dev.runwayml.com/v1"
RUNWAY_API_VERSION = "2024-11-06"


class RunwayProvider(BaseProvider):
    """Runway Gen-3 text-to-video provider."""

    def __init__(self):
        super().__init__(
            name="runway",
            category=ProviderCategory.TEXT_TO_VIDEO,
            status=ProviderStatus.API_KEY_PENDING,
        )

    async def execute(
        self,
        prompt: str,
        duration: int = 5,
        ratio: str = "1280:720",
        **kwargs,
    ) -> dict:
        if not self.is_ready():
            return {"error": "Runway API key not configured", "provider": "runway"}

        payload = {
            "promptText": prompt,
            "model": "gen3a_turbo",
            "duration": duration,
            "ratio": ratio,
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{RUNWAY_BASE}/image_to_video",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                        "X-Runway-Version": RUNWAY_API_VERSION,
                    },
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()

            task_id = data.get("id")
            return {
                "status": "pending",
                "provider": "runway",
                "task_id": task_id,
                "poll_url": f"{RUNWAY_BASE}/tasks/{task_id}",
                "duration": duration,
                "message": "Video generation started. Poll poll_url for completion.",
            }

        except httpx.HTTPStatusError as e:
            logger.error("Runway API error %s: %s", e.response.status_code, e.response.text)
            return {"error": f"Runway API error {e.response.status_code}", "provider": "runway"}
        except Exception as e:
            logger.error("Runway unexpected error: %s", e)
            return {"error": str(e), "provider": "runway"}

    async def get_task_status(self, task_id: str) -> dict:
        """Poll Runway for task completion."""
        if not self.is_ready():
            return {"error": "Runway API key not configured"}
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(
                    f"{RUNWAY_BASE}/tasks/{task_id}",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "X-Runway-Version": RUNWAY_API_VERSION,
                    },
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error("Runway task poll error: %s", e)
            return {"error": str(e)}

    def estimate_cost(self, duration: int = 5, **kwargs) -> float:
        # Runway Gen-3: ~$0.05/s on standard plan → 5 credits per second
        return max(1.0, duration * 5.0)
