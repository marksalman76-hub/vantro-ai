import asyncio
import base64
import logging
import os
import time

import httpx
import jwt

logger = logging.getLogger(__name__)

KLING_BASE = os.getenv("KLING_BASE_URL", "https://api.klingai.com")
_POLL_INTERVAL = 10
_POLL_MAX = 72  # 12 min cap

# Internal model ID → (KlingAI API model name, mode, max_duration_s)
_MODEL_CONFIG: dict[str, tuple[str, str, int]] = {
    # 720p Turbo
    "kling3_0_turbo":       ("kling-v1-5",     "std",  10),
    "kling-3.0-turbo":      ("kling-v1-5",     "std",  10),
    # 1080p
    "kling3_0":             ("kling-v1-5",     "pro",  10),
    "kling-3.0":            ("kling-v1-5",     "pro",  10),
    "kling-v1-5":           ("kling-v1-5",     "pro",  10),
    # 4K Cinema Studio
    "cinematic_studio_3_0": ("kling-v2-master", "pro", 10),
    "cinema_studio_4k":     ("kling-v2-master", "pro", 10),
    "kling-v2-master":      ("kling-v2-master", "pro", 10),
    # Generic fallbacks
    "kling-v1":             ("kling-v1",        "std",  5),
}
_DEFAULT_MODEL = ("kling-v1-5", "std", 10)


def _resolve_model(model_id: str) -> tuple[str, str, int]:
    return _MODEL_CONFIG.get((model_id or "").strip(), _DEFAULT_MODEL)


def _make_jwt(access_key: str, secret_key: str) -> str:
    now = int(time.time())
    return jwt.encode(
        {"iss": access_key, "exp": now + 1800, "nbf": now - 5},
        secret_key,
        algorithm="HS256",
    )


async def _generate_elevenlabs_audio(
    *,
    script: str,
    voice_model_id: str,
    language: str,
    elevenlabs_api_key: str,
) -> bytes | None:
    """Generate audio bytes from ElevenLabs. Returns None on failure."""
    if not script or not elevenlabs_api_key:
        return None
    voice_id = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
                headers={"xi-api-key": elevenlabs_api_key, "Content-Type": "application/json"},
                json={
                    "text": script[:1500],
                    "model_id": voice_model_id or "eleven_multilingual_v2",
                    "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
                },
            )
            resp.raise_for_status()
            return resp.content
    except Exception as exc:
        logger.warning("ElevenLabs audio generation failed (continuing without voiceover): %s", exc)
        return None


async def _apply_lipsync(
    *,
    base: str,
    headers_fn,
    task_id: str,
    audio_bytes: bytes,
) -> str | None:
    """Attempt Kling lip-sync. Returns new video URL or None if unsupported."""
    audio_b64 = base64.b64encode(audio_bytes).decode()
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{base}/v1/videos/lip-sync",
                json={"video_id": task_id, "audio_type": "audio", "audio_file": audio_b64},
                headers=headers_fn(),
            )
            if resp.status_code >= 400:
                return None
            data = resp.json()
        sync_task_id = ((data.get("data") or {}).get("task_id")) or data.get("task_id")
        if not sync_task_id:
            return None

        for _ in range(24):  # 4 min max for lip-sync
            await asyncio.sleep(10)
            async with httpx.AsyncClient(timeout=30.0) as client:
                poll = await client.get(f"{base}/v1/videos/lip-sync/{sync_task_id}", headers=headers_fn())
                poll.raise_for_status()
                pd = poll.json()
            status = (pd.get("data") or {}).get("task_status", "")
            if status == "succeed":
                videos = ((pd.get("data") or {}).get("task_result") or {}).get("videos") or []
                return videos[0].get("url", "") if videos else None
            if status == "failed":
                return None
    except Exception as exc:
        logger.warning("Kling lip-sync failed (returning video without audio sync): %s", exc)
    return None


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
        model: str = "kling3_0_turbo",
        duration: int = 5,
        aspect_ratio: str = "9:16",
        reference_image_base64: str = "",
        reference_image_content_type: str = "image/jpeg",
        voiceover_script: str = "",
        voice_model_id: str = "eleven_multilingual_v2",
        language: str = "English",
        **kwargs,
    ) -> dict:
        if not self.is_ready():
            raise RuntimeError("Kling credentials not configured (KLING_ACCESS_KEY / KLING_SECRET_KEY)")

        api_model, mode, max_dur = _resolve_model(model)
        base = KLING_BASE.rstrip("/")
        duration_s = str(min(max(int(duration), 5), max_dur))

        if reference_image_base64:
            endpoint = f"{base}/v1/videos/image2video"
            body: dict = {
                "model_name": api_model,
                "image": reference_image_base64,
                "prompt": prompt,
                "cfg_scale": 0.5,
                "mode": mode,
                "duration": duration_s,
            }
            poll_path = "image2video"
        else:
            endpoint = f"{base}/v1/videos/text2video"
            body = {
                "model_name": api_model,
                "prompt": prompt,
                "negative_prompt": "",
                "cfg_scale": 0.5,
                "mode": mode,
                "aspect_ratio": aspect_ratio,
                "duration": duration_s,
            }
            poll_path = "text2video"

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(endpoint, json=body, headers=self._headers())
            resp.raise_for_status()
            data = resp.json()

        task_id = ((data.get("data") or {}).get("task_id")) or data.get("task_id")
        if not task_id:
            raise RuntimeError(f"Kling API returned no task_id: {data}")

        logger.info("Kling task submitted: %s (model=%s mode=%s)", task_id, api_model, mode)

        poll_url = f"{base}/v1/videos/{poll_path}/{task_id}"
        video_url = ""
        for attempt in range(_POLL_MAX):
            await asyncio.sleep(_POLL_INTERVAL)
            async with httpx.AsyncClient(timeout=30.0) as client:
                pr = await client.get(poll_url, headers=self._headers())
                pr.raise_for_status()
                pd = pr.json()

            task_data = pd.get("data") or {}
            status = task_data.get("task_status", "")
            logger.debug("Kling poll %d/%d task=%s status=%s", attempt + 1, _POLL_MAX, task_id, status)

            if status == "succeed":
                videos = (task_data.get("task_result") or {}).get("videos") or []
                video_url = videos[0].get("url", "") if videos else ""
                break
            if status == "failed":
                raise RuntimeError(f"Kling task {task_id} failed: {task_data.get('task_status_msg')}")
        else:
            raise TimeoutError(f"Kling task {task_id} timed out after {_POLL_MAX * _POLL_INTERVAL}s")

        # ElevenLabs voiceover → optional lip-sync
        audio_url = ""
        final_video_url = video_url
        elevenlabs_key = os.getenv("ELEVENLABS_API_KEY", "")
        if voiceover_script and elevenlabs_key and video_url:
            audio_bytes = await _generate_elevenlabs_audio(
                script=voiceover_script,
                voice_model_id=voice_model_id,
                language=language,
                elevenlabs_api_key=elevenlabs_key,
            )
            if audio_bytes:
                synced_url = await _apply_lipsync(
                    base=base,
                    headers_fn=self._headers,
                    task_id=task_id,
                    audio_bytes=audio_bytes,
                )
                if synced_url:
                    final_video_url = synced_url
                # Store audio as base64 for fallback overlay on frontend
                audio_url = "data:audio/mpeg;base64," + base64.b64encode(audio_bytes).decode()

        return {
            "asset_url": final_video_url,
            "video_url": final_video_url,
            "audio_url": audio_url,
            "task_id": task_id,
            "provider": "kling_direct",
            "api_model": api_model,
            "mode": mode,
            "status": "completed",
        }
