import os
import logging
import httpx
import requests
from typing import Optional

logger = logging.getLogger(__name__)

HEYGEN_API_KEY = os.getenv("HEYGEN_API_KEY", "")
HEYGEN_BASE_URL = "https://api.heygen.com"

# Map internal avatar slugs → HeyGen avatar_ids.
# Override any of these via environment variables.
AVATAR_MAP: dict[str, str] = {
    "alex":  os.getenv("HEYGEN_AVATAR_ALEX",  ""),
    "sofia": os.getenv("HEYGEN_AVATAR_SOFIA", ""),
    "james": os.getenv("HEYGEN_AVATAR_JAMES", ""),
    "maria": os.getenv("HEYGEN_AVATAR_MARIA", ""),
    "kai":   os.getenv("HEYGEN_AVATAR_KAI",   ""),
    "nova":  os.getenv("HEYGEN_AVATAR_NOVA",  ""),
}

# Map internal voice slugs → HeyGen voice_ids
VOICE_MAP: dict[str, str] = {
    "natural":      os.getenv("HEYGEN_VOICE_NATURAL",      ""),
    "professional": os.getenv("HEYGEN_VOICE_PROFESSIONAL", ""),
    "energetic":    os.getenv("HEYGEN_VOICE_ENERGETIC",    ""),
    "calm":         os.getenv("HEYGEN_VOICE_CALM",         ""),
}


def _headers() -> dict:
    return {"X-Api-Key": HEYGEN_API_KEY, "Content-Type": "application/json"}


def is_configured() -> bool:
    return bool(HEYGEN_API_KEY)


async def submit_video(
    avatar_id: str,
    voice_id: str,
    script: str,
    language: str = "en",
) -> Optional[str]:
    """
    Submit a video generation request to HeyGen.
    Returns the HeyGen video_id, or None on failure.
    """
    if not is_configured():
        logger.warning("HEYGEN_API_KEY not set — skipping video generation")
        return None

    heygen_avatar = AVATAR_MAP.get(avatar_id, avatar_id)
    heygen_voice = VOICE_MAP.get(voice_id, voice_id)

    if not heygen_avatar or not heygen_voice:
        logger.error(
            "Missing HeyGen mapping for avatar=%s voice=%s. "
            "Set HEYGEN_AVATAR_* and HEYGEN_VOICE_* env vars.",
            avatar_id,
            voice_id,
        )
        return None

    payload = {
        "video_inputs": [
            {
                "character": {
                    "type": "avatar",
                    "avatar_id": heygen_avatar,
                    "avatar_style": "normal",
                },
                "voice": {
                    "type": "text",
                    "input_text": script,
                    "voice_id": heygen_voice,
                    "speed": 1.0,
                },
                "background": {"type": "color", "value": "#ffffff"},
            }
        ],
        "dimension": {"width": 1280, "height": 720},
        "test": False,
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{HEYGEN_BASE_URL}/v2/video/generate",
                json=payload,
                headers=_headers(),
            )
            resp.raise_for_status()
            data = resp.json()
            video_id = data.get("data", {}).get("video_id")
            logger.info("HeyGen video submitted: video_id=%s", video_id)
            return video_id
    except httpx.HTTPStatusError as e:
        logger.error("HeyGen submit error %s: %s", e.response.status_code, e.response.text)
        return None
    except Exception as e:
        logger.error("HeyGen submit exception: %s", e)
        return None


async def get_video_status(video_id: str) -> dict:
    """
    Poll HeyGen for job status.
    Returns {"status": "pending|processing|completed|failed", "video_url": str|None}
    """
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(
                f"{HEYGEN_BASE_URL}/v1/video_status.get",
                params={"video_id": video_id},
                headers=_headers(),
            )
            resp.raise_for_status()
            data = resp.json().get("data", {})
            raw_status = data.get("status", "pending")

            # HeyGen statuses: pending, processing, completed, failed
            status_map = {
                "pending":    "processing",
                "processing": "processing",
                "completed":  "completed",
                "failed":     "failed",
            }
            return {
                "status":    status_map.get(raw_status, "processing"),
                "video_url": data.get("video_url"),
                "error":     data.get("error"),
            }
    except Exception as e:
        logger.error("HeyGen status check error for %s: %s", video_id, e)
        return {"status": "processing", "video_url": None, "error": str(e)}


class HeyGenService:
    """Synchronous class-based wrapper used by the worker and tests."""

    BASE_URL = "https://api.heygen.com"

    def __init__(self, api_key: str = ""):
        self._api_key = api_key or HEYGEN_API_KEY
        self._headers = {"X-Api-Key": self._api_key, "Content-Type": "application/json"}

    def submit_video(
        self,
        avatar_id: str,
        voice_id: str,
        script: str,
        language: str = "en",
        tone: str = "professional",
    ) -> Optional[str]:
        payload = {
            "video_inputs": [
                {
                    "character": {"type": "avatar", "avatar_id": avatar_id},
                    "voice": {"type": "text", "input_text": script, "voice_id": voice_id},
                    "background": {"type": "color", "value": "#ffffff"},
                }
            ],
            "dimension": {"width": 1280, "height": 720},
            "test": False,
        }
        resp = requests.post(
            f"{self.BASE_URL}/v2/video/generate",
            json=payload,
            headers=self._headers,
        )
        if resp.status_code == 200:
            return resp.json().get("data", {}).get("video_id")
        logger.error("HeyGenService submit error %s: %s", resp.status_code, resp.text[:200])
        return None

    def check_status(self, video_id: str) -> tuple:
        resp = requests.get(
            f"{self.BASE_URL}/v1/video_status.get",
            params={"video_id": video_id},
            headers=self._headers,
        )
        if resp.status_code == 200:
            data = resp.json().get("data", {})
            return data.get("status", "pending"), data.get("video_url")
        return "unknown", None
