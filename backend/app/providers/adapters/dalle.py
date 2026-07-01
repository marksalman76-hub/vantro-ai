import logging
import os

import httpx

logger = logging.getLogger(__name__)

DALLE_BASE = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

_QUALITY_MAP: dict[str, str] = {
    "hd": "hd",
    "standard": "standard",
    "DALL-E 3 HD": "hd",
    "DALL-E 3": "standard",
}

_SIZE_FOR_RATIO: dict[str, str] = {
    "1:1": "1024x1024",
    "16:9": "1792x1024",
    "9:16": "1024x1792",
}
_DEFAULT_SIZE = "1024x1024"


class DalleProvider:
    def __init__(self, api_key: str = "") -> None:
        self._api_key = api_key or os.getenv("OPENAI_API_KEY", "")

    def is_ready(self) -> bool:
        return bool(self._api_key)

    async def execute(
        self,
        *,
        prompt: str,
        model: str = "dall-e-3",
        quality: str = "standard",
        aspect_ratio: str = "1:1",
        n: int = 1,
        **kwargs,
    ) -> dict:
        if not self.is_ready():
            raise RuntimeError("DALL-E credentials not configured (OPENAI_API_KEY)")

        resolved_quality = _QUALITY_MAP.get(quality, "standard")
        size = _SIZE_FOR_RATIO.get(aspect_ratio, _DEFAULT_SIZE)

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{DALLE_BASE}/images/generations",
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "prompt": prompt[:4000],
                    "n": n,
                    "size": size,
                    "quality": resolved_quality,
                    "response_format": "url",
                },
            )
            resp.raise_for_status()
            data = resp.json()

        images = data.get("data") or []
        image_url = images[0].get("url", "") if images else ""

        return {
            "asset_url": image_url,
            "image_url": image_url,
            "provider": "openai_dalle",
            "api_model": model,
            "quality": resolved_quality,
            "size": size,
            "status": "completed",
        }
