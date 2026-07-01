import asyncio
import logging
import os
import time

import httpx
import jwt

logger = logging.getLogger(__name__)

KLING_BASE = os.getenv("KLING_BASE_URL", "https://api.klingai.com")
_POLL_INTERVAL = 10
_POLL_MAX = 72  # 12 min cap


def _make_jwt(access_key: str, secret_key: str) -> str:
    now = int(time.time())
    return jwt.encode(
        {"iss": access_key, "exp": now + 1800, "nbf": now - 5},
        secret_key,
        algorithm="HS256",
    )


class KlingProvider:
    def __init__(self, access_key: str = "", secret_key: str = "") -> None:
        self._access_key = access_key or os.getenv("KLING_ACCESS_KEY", "")
        self._secret_key = secret_key or os.getenv("KLING_SECRET_KEY", "")

    def is_ready(self) -> bool:
        return bool(self._access_key and self._secret_key)

    def _headers(self) -> dict:
        token = _make_jwt(self._access_key, self._secret_key)
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    async def execute(
        self,
        *,
        prompt: str,
        model: str = "kling-v1",
        duration: int = 5,
        aspect_ratio: str = "9:16",
        reference_image_base64: str = "",
        reference_image_content_type: str = "image/jpeg",
        **kwargs,
    ) -> dict:
        if not self.is_ready():
            raise RuntimeError("Kling credentials not configured (KLING_ACCESS_KEY / KLING_SECRET_KEY)")

        base = KLING_BASE.rstrip("/")
        headers = self._headers()
        duration_s = str(min(max(int(duration), 5), 10))

        if reference_image_base64:
            endpoint = f"{base}/v1/videos/image2video"
            body: dict = {
                "model_name": model,
                "image": reference_image_base64,
                "prompt": prompt,
                "cfg_scale": 0.5,
                "mode": "std",
                "duration": duration_s,
            }
            poll_path = "image2video"
        else:
            endpoint = f"{base}/v1/videos/text2video"
            body = {
                "model_name": model,
                "prompt": prompt,
                "negative_prompt": "",
                "cfg_scale": 0.5,
                "mode": "std",
                "aspect_ratio": aspect_ratio,
                "duration": duration_s,
            }
            poll_path = "text2video"

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(endpoint, json=body, headers=headers)
            resp.raise_for_status()
            data = resp.json()

        task_id = ((data.get("data") or {}).get("task_id")) or data.get("task_id")
        if not task_id:
            raise RuntimeError(f"Kling API returned no task_id: {data}")

        logger.info("Kling task submitted: %s (model=%s)", task_id, model)

        poll_url = f"{base}/v1/videos/{poll_path}/{task_id}"
        for attempt in range(_POLL_MAX):
            await asyncio.sleep(_POLL_INTERVAL)
            async with httpx.AsyncClient(timeout=30.0) as client:
                poll_resp = await client.get(poll_url, headers=self._headers())
                poll_resp.raise_for_status()
                poll = poll_resp.json()

            task_data = poll.get("data") or {}
            status = task_data.get("task_status", "")
            logger.debug("Kling poll %d/%d task=%s status=%s", attempt + 1, _POLL_MAX, task_id, status)

            if status == "succeed":
                videos = (task_data.get("task_result") or {}).get("videos") or []
                video_url = videos[0].get("url", "") if videos else ""
                return {
                    "asset_url": video_url,
                    "video_url": video_url,
                    "task_id": task_id,
                    "provider": "kling_direct",
                    "model": model,
                    "status": "completed",
                }

            if status == "failed":
                msg = task_data.get("task_status_msg") or "unknown error"
                raise RuntimeError(f"Kling task {task_id} failed: {msg}")

        raise TimeoutError(f"Kling task {task_id} did not complete within {_POLL_MAX * _POLL_INTERVAL}s")
