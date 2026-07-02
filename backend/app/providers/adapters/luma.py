import asyncio
import logging
import os

import httpx

logger = logging.getLogger(__name__)

LUMA_BASE = "https://api.lumalabs.ai/dream-machine/v1"
_POLL_INTERVAL = 8
_POLL_MAX = 90  # 12 min cap

_ASPECT_RATIO_MAP = {
    "9:16": "9:16",
    "16:9": "16:9",
    "1:1": "1:1",
    "4:5": "4:5",
    "4:3": "4:3",
    "3:4": "3:4",
    "21:9": "21:9",
}


class LumaProvider:
    """Luma Dream Machine provider for 15s+ video clips."""

    def __init__(self, api_key: str = "") -> None:
        self._api_key = api_key or os.getenv("LUMAAI_API_KEY", "")

    def is_ready(self) -> bool:
        return bool(self._api_key)

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

    def _normalize_aspect_ratio(self, ratio: str) -> str:
        r = (ratio or "9:16").split("(")[0].strip()
        return _ASPECT_RATIO_MAP.get(r, "9:16")

    async def _create_generation(self, prompt: str, aspect_ratio: str, keyframe_gen_id: str = "") -> str:
        body: dict = {"prompt": prompt, "aspect_ratio": aspect_ratio}
        if keyframe_gen_id:
            # Extend from last frame of previous generation
            body["keyframes"] = {"frame0": {"type": "generation", "id": keyframe_gen_id}}
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(f"{LUMA_BASE}/generations", json=body, headers=self._headers())
            resp.raise_for_status()
            data = resp.json()
        gen_id = data.get("id")
        if not gen_id:
            raise RuntimeError(f"Luma API returned no generation id: {data}")
        logger.info("Luma generation submitted: %s (extend=%s)", gen_id, bool(keyframe_gen_id))
        return gen_id

    async def _poll_generation(self, gen_id: str) -> str:
        for attempt in range(_POLL_MAX):
            await asyncio.sleep(_POLL_INTERVAL)
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.get(f"{LUMA_BASE}/generations/{gen_id}", headers=self._headers())
                resp.raise_for_status()
                data = resp.json()
            state = data.get("state", "")
            logger.debug("Luma poll %d/%d id=%s state=%s", attempt + 1, _POLL_MAX, gen_id, state)
            if state == "completed":
                assets = data.get("assets") or {}
                video_url = assets.get("video", "")
                if video_url:
                    return video_url
                raise RuntimeError(f"Luma generation {gen_id} completed but no video URL in assets")
            if state == "failed":
                failure = data.get("failure_reason", "unknown")
                raise RuntimeError(f"Luma generation {gen_id} failed: {failure}")
        raise TimeoutError(f"Luma generation {gen_id} timed out after {_POLL_MAX * _POLL_INTERVAL}s")

    async def execute(
        self,
        *,
        prompt: str,
        duration: int = 5,
        aspect_ratio: str = "9:16",
        **kwargs,
    ) -> dict:
        if not self.is_ready():
            raise RuntimeError("Luma credentials not configured (LUMAAI_API_KEY)")

        ar = self._normalize_aspect_ratio(aspect_ratio)
        # Each Luma Dream Machine generation is ~5s; chain for longer clips
        clips_needed = max(1, round(duration / 5))

        gen_id = await self._create_generation(prompt, ar)
        video_url = await self._poll_generation(gen_id)
        prev_gen_id = gen_id

        for i in range(1, clips_needed):
            logger.info("Luma extending clip %d/%d for %ds target", i + 1, clips_needed, duration)
            next_gen_id = await self._create_generation(prompt, ar, keyframe_gen_id=prev_gen_id)
            video_url = await self._poll_generation(next_gen_id)
            prev_gen_id = next_gen_id

        return {
            "asset_url": video_url,
            "video_url": video_url,
            "audio_url": "",
            "task_id": gen_id,
            "provider": "luma_dream_machine",
            "clips_generated": clips_needed,
            "target_duration_s": duration,
            "status": "completed",
        }
