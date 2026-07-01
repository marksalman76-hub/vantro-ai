import asyncio
import logging
import os

import httpx

logger = logging.getLogger(__name__)

ARCADS_BASE = os.getenv("ARCADS_BASE_URL", "https://external-api.arcads.ai")
_POLL_INTERVAL = 10
_POLL_MAX = 72  # 12 min cap

# Map generic model aliases to Arcads API model IDs
_MODEL_MAP: dict[str, str] = {
    "kling-3.0": "kling-3.0",
    "kling-v3": "kling-3.0",
    "kling": "kling-3.0",
    "seedance-2.0": "seedance-2.0",
    "seedance": "seedance-2.0",
    "nano-banana": "nano-banana-2",
    "nano-banana-2": "nano-banana-2",
    "veo31": "veo31",
    "veo3": "veo31",
    "sora2": "sora2",
}


def _resolve_model(model: str) -> str:
    return _MODEL_MAP.get((model or "").lower().strip(), model or "kling-3.0")


class ArcadsProvider:
    def __init__(self, api_key: str = "") -> None:
        self._api_key = api_key or os.getenv("ARCADS_API_KEY", "")

    def is_ready(self) -> bool:
        return bool(self._api_key)

    def _auth(self) -> tuple:
        return (self._api_key, "")

    async def execute(
        self,
        *,
        prompt: str,
        model: str = "kling-3.0",
        duration: int = 5,
        aspect_ratio: str = "9:16",
        reference_image_base64: str = "",
        reference_image_content_type: str = "image/jpeg",
        audio_enabled: bool = False,
        **kwargs,
    ) -> dict:
        if not self.is_ready():
            raise RuntimeError("Arcads API key not configured (ARCADS_API_KEY)")

        base = ARCADS_BASE.rstrip("/")
        resolved_model = _resolve_model(model)

        body: dict = {
            "model": resolved_model,
            "prompt": prompt,
            "aspectRatio": aspect_ratio,
        }

        if resolved_model == "seedance-2.0":
            body["duration"] = min(max(int(duration), 4), 15)
            body["audioEnabled"] = audio_enabled
        elif resolved_model in ("sora2",):
            body["duration"] = min(max(int(duration), 4), 20)
        else:
            body["duration"] = min(max(int(duration), 4), 10)

        if reference_image_base64:
            body["startFrame"] = f"data:{reference_image_content_type};base64,{reference_image_base64}"

        async with httpx.AsyncClient(timeout=90.0) as client:
            resp = await client.post(
                f"{base}/v2/videos/generate",
                json=body,
                auth=self._auth(),
            )
            resp.raise_for_status()
            data = resp.json()

        asset_id = ((data.get("data") or {}).get("id")) or data.get("id")
        if not asset_id:
            raise RuntimeError(f"Arcads API returned no asset id: {data}")

        logger.info("Arcads video submitted: %s (model=%s)", asset_id, resolved_model)

        for attempt in range(_POLL_MAX):
            await asyncio.sleep(_POLL_INTERVAL)
            async with httpx.AsyncClient(timeout=30.0) as client:
                poll_resp = await client.get(
                    f"{base}/v1/assets/{asset_id}",
                    auth=self._auth(),
                )
                poll_resp.raise_for_status()
                poll = poll_resp.json()

            asset = poll.get("data") or {}
            status = asset.get("status", "")
            logger.debug("Arcads poll %d/%d id=%s status=%s", attempt + 1, _POLL_MAX, asset_id, status)

            if status == "completed":
                video_url = asset.get("video_url") or asset.get("url") or ""
                return {
                    "asset_url": video_url,
                    "video_url": video_url,
                    "task_id": str(asset_id),
                    "provider": "arcads",
                    "model": resolved_model,
                    "status": "completed",
                }

            if status == "failed":
                raise RuntimeError(f"Arcads asset {asset_id} failed")

        raise TimeoutError(f"Arcads asset {asset_id} did not complete within {_POLL_MAX * _POLL_INTERVAL}s")

    async def generate_image(
        self,
        *,
        prompt: str,
        model: str = "nano-banana-2",
        reference_image_base64: str = "",
        reference_image_content_type: str = "image/jpeg",
        **kwargs,
    ) -> dict:
        if not self.is_ready():
            raise RuntimeError("Arcads API key not configured (ARCADS_API_KEY)")

        base = ARCADS_BASE.rstrip("/")
        resolved_model = _resolve_model(model)

        body: dict = {"model": resolved_model, "prompt": prompt}
        if reference_image_base64:
            body["refImageAsBase64"] = f"data:{reference_image_content_type};base64,{reference_image_base64}"

        async with httpx.AsyncClient(timeout=90.0) as client:
            resp = await client.post(
                f"{base}/v2/images/generate",
                json=body,
                auth=self._auth(),
            )
            resp.raise_for_status()
            data = resp.json()

        asset_id = ((data.get("data") or {}).get("id")) or data.get("id")
        if not asset_id:
            raise RuntimeError(f"Arcads image API returned no asset id: {data}")

        for attempt in range(_POLL_MAX):
            await asyncio.sleep(_POLL_INTERVAL)
            async with httpx.AsyncClient(timeout=30.0) as client:
                poll_resp = await client.get(f"{base}/v1/assets/{asset_id}", auth=self._auth())
                poll_resp.raise_for_status()
                poll = poll_resp.json()

            asset = poll.get("data") or {}
            status = asset.get("status", "")
            if status == "completed":
                image_url = asset.get("image_url") or asset.get("url") or ""
                return {"asset_url": image_url, "task_id": str(asset_id), "provider": "arcads", "model": resolved_model, "status": "completed"}
            if status == "failed":
                raise RuntimeError(f"Arcads image {asset_id} failed")

        raise TimeoutError(f"Arcads image {asset_id} did not complete")
