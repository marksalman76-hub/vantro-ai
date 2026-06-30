import asyncio
import base64
import json
import httpx
import logging
import os
from pathlib import Path
import re
import shutil
import subprocess
import time
from uuid import uuid4

from ..base import BaseProvider, ProviderCategory, ProviderStatus
from .elevenlabs import DEFAULT_VOICE_ID, ElevenLabsProvider

logger = logging.getLogger(__name__)

HIGGSFIELD_BASE = os.getenv("HIGGSFIELD_BASE_URL", "https://api.higgsfield.ai/v1")
MCP_CONFIG_PATH = Path(__file__).resolve().parents[3] / "claude-mcp.higgsfield.json"
_MCP_READY_CACHE = {"checked_at": 0.0, "ready": False}


def _execution_surface() -> str:
    return os.getenv("HIGGSFIELD_EXECUTION_SURFACE", "claude_code_mcp").strip().lower()


def _extract_json_payload(text: str) -> dict:
    cleaned = (text or "").strip()
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", cleaned, flags=re.DOTALL | re.IGNORECASE)
    if fenced:
        cleaned = fenced.group(1)
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start >= 0 and end >= start:
        cleaned = cleaned[start : end + 1]
    try:
        parsed = json.loads(cleaned)
    except (TypeError, ValueError):
        return {"raw_output": text}
    return parsed if isinstance(parsed, dict) else {"raw_output": text}


def _higgsfield_config_home() -> Path:
    configured = os.getenv("HIGGSFIELD_MCP_CONFIG_HOME")
    if configured:
        return Path(configured)
    xdg_config = os.getenv("XDG_CONFIG_HOME")
    if xdg_config:
        return Path(xdg_config)
    return Path.home() / ".config"


def _prepare_higgsfield_mcp_credentials() -> None:
    raw_credentials = os.getenv("HIGGSFIELD_MCP_CREDENTIALS_JSON", "").strip()
    if not raw_credentials:
        return
    parsed = json.loads(raw_credentials)
    if not isinstance(parsed, dict) or not parsed.get("access_token") or not parsed.get("refresh_token"):
        raise ValueError("HIGGSFIELD_MCP_CREDENTIALS_JSON must contain access_token and refresh_token")
    credentials_dir = _higgsfield_config_home() / "higgsfield"
    credentials_dir.mkdir(parents=True, exist_ok=True)
    credentials_path = credentials_dir / "credentials.json"
    credentials_path.write_text(json.dumps(parsed), encoding="utf-8")
    try:
        credentials_path.chmod(0o600)
    except OSError:
        pass


def _mcp_process_env() -> dict:
    env = os.environ.copy()
    configured_home = os.getenv("HIGGSFIELD_MCP_CONFIG_HOME")
    if configured_home:
        env["XDG_CONFIG_HOME"] = configured_home
    return env


async def _run_claude_mcp_prompt(
    prompt: str,
    *,
    timeout_seconds: int,
    allowed_tools: str = "mcp__higgsfield__generate_video",
) -> str:
    _prepare_higgsfield_mcp_credentials()
    process = await asyncio.create_subprocess_exec(
        "claude",
        "-p",
        prompt,
        "--mcp-config",
        str(MCP_CONFIG_PATH),
        "--strict-mcp-config",
        "--allowedTools",
        allowed_tools,
        "--permission-mode",
        "auto",
        "--output-format",
        "text",
        "--max-budget-usd",
        os.getenv("HIGGSFIELD_MCP_MAX_BUDGET_USD", "1.00"),
        env=_mcp_process_env(),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout_seconds)
    except asyncio.TimeoutError:
        process.kill()
        await process.communicate()
        raise TimeoutError("Higgsfield Claude Code MCP execution timed out")
    if process.returncode != 0:
        raise RuntimeError((stderr or stdout).decode("utf-8", errors="replace").strip())
    return stdout.decode("utf-8", errors="replace")


def _find_first_key(value: object, keys: set[str]) -> str:
    if isinstance(value, dict):
        for key, item in value.items():
            if key in keys and isinstance(item, str) and item.strip():
                return item.strip()
        for item in value.values():
            found = _find_first_key(item, keys)
            if found:
                return found
    if isinstance(value, list):
        for item in value:
            found = _find_first_key(item, keys)
            if found:
                return found
    return ""


def _first_higgsfield_result(data: dict) -> dict:
    results = data.get("results")
    if isinstance(results, list) and results and isinstance(results[0], dict):
        return results[0]
    return {}


async def _upload_audio_base64_to_higgsfield_mcp(
    *,
    audio_base64: str,
    content_type: str,
    timeout_seconds: int,
) -> dict:
    filename = f"elevenlabs-voiceover-{uuid4().hex}.mp3"
    upload_params = {
        "method": "upload_url",
        "filename": filename,
        "content_type": content_type or "audio/mpeg",
    }
    upload_prompt = (
        "Use the connected Higgsfield MCP tool mcp__higgsfield__media_upload "
        f"with this exact JSON params object: {json.dumps(upload_params, sort_keys=True)}. "
        "Return only the raw JSON result."
    )
    upload_raw = await _run_claude_mcp_prompt(
        upload_prompt,
        timeout_seconds=timeout_seconds,
        allowed_tools="mcp__higgsfield__media_upload",
    )
    upload_data = _extract_json_payload(upload_raw)
    upload_url = _find_first_key(upload_data, {"upload_url", "url", "presigned_url", "put_url"})
    media_id = _find_first_key(upload_data, {"media_id", "id"})
    if not upload_url or not media_id:
        raise RuntimeError("Higgsfield MCP media_upload did not return upload_url and media_id")

    audio_bytes = base64.b64decode(audio_base64)
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.put(
            upload_url,
            content=audio_bytes,
            headers={"Content-Type": content_type or "audio/mpeg"},
        )
        response.raise_for_status()

    confirm_params = {"media_id": media_id, "type": "audio"}
    confirm_prompt = (
        "Use the connected Higgsfield MCP tool mcp__higgsfield__media_confirm "
        f"with this exact JSON params object: {json.dumps(confirm_params, sort_keys=True)}. "
        "Return only the raw JSON result."
    )
    confirm_raw = await _run_claude_mcp_prompt(
        confirm_prompt,
        timeout_seconds=timeout_seconds,
        allowed_tools="mcp__higgsfield__media_confirm",
    )
    return {
        "media_id": media_id,
        "upload": upload_data,
        "confirm": _extract_json_payload(confirm_raw),
    }


async def _prepare_elevenlabs_audio_media(
    *,
    script: str,
    language: str,
    model_id: str,
    voice_id: str,
    timeout_seconds: int,
) -> dict:
    api_key = os.getenv("ELEVENLABS_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("ELEVENLABS_API_KEY is required for multilingual Higgsfield voiceover")

    elevenlabs = ElevenLabsProvider()
    elevenlabs.set_api_key(api_key)
    audio_result = await elevenlabs.execute(
        text=script,
        voice_id=voice_id or os.getenv("ELEVENLABS_VOICE_ID", DEFAULT_VOICE_ID),
        language=language or "en",
        model_id=model_id or os.getenv("ELEVENLABS_MODEL_ID", "eleven_multilingual_v2"),
    )
    if audio_result.get("error"):
        raise RuntimeError(str(audio_result["error"]))
    audio_base64 = audio_result.get("audio_base64")
    if not isinstance(audio_base64, str) or not audio_base64.strip():
        raise RuntimeError("ElevenLabs did not return audio_base64")

    upload_result = await _upload_audio_base64_to_higgsfield_mcp(
        audio_base64=audio_base64,
        content_type=str(audio_result.get("content_type") or "audio/mpeg"),
        timeout_seconds=timeout_seconds,
    )
    return {
        "provider": "elevenlabs",
        "media_id": upload_result["media_id"],
        "language": language,
        "model_id": model_id,
        "voice_id": voice_id,
        "character_count": audio_result.get("character_count"),
        "upload": upload_result,
    }


class HiggsfieldProvider(BaseProvider):
    """Higgsfield UGC video generation provider."""

    def __init__(self):
        super().__init__(
            name="higgsfield",
            category=ProviderCategory.TEXT_TO_VIDEO,
            status=ProviderStatus.API_KEY_PENDING,
        )

    @property
    def execution_surface(self) -> str:
        return _execution_surface()

    def is_mcp_ready(self) -> bool:
        cache_seconds = int(os.getenv("HIGGSFIELD_MCP_READINESS_CACHE_SECONDS", "300"))
        now = time.monotonic()
        if now - float(_MCP_READY_CACHE["checked_at"]) < cache_seconds:
            return bool(_MCP_READY_CACHE["ready"])

        if shutil.which("claude") is None:
            _MCP_READY_CACHE.update({"checked_at": now, "ready": False})
            return False
        try:
            _prepare_higgsfield_mcp_credentials()

            result = subprocess.run(
                [
                    "claude",
                    "-p",
                    "List Higgsfield MCP tools only. Do not create media. Return [].",
                    "--mcp-config",
                    str(MCP_CONFIG_PATH),
                    "--strict-mcp-config",
                    "--allowedTools",
                    "mcp__higgsfield__*",
                    "--permission-mode",
                    "auto",
                    "--output-format",
                    "text",
                    "--max-budget-usd",
                    os.getenv("HIGGSFIELD_MCP_READINESS_BUDGET_USD", "1.00"),
                ],
                capture_output=True,
                text=True,
                timeout=60,
                check=False,
                env=_mcp_process_env(),
            )
        except Exception:
            _MCP_READY_CACHE.update({"checked_at": now, "ready": False})
            return False
        ready = result.returncode == 0
        _MCP_READY_CACHE.update({"checked_at": now, "ready": ready})
        return ready

    def is_ready(self) -> bool:
        if self.execution_surface == "claude_code_mcp":
            return self.is_mcp_ready()
        return super().is_ready()

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
        payload = {
            "prompt": prompt,
            "duration": duration,
            "aspect_ratio": aspect_ratio,
            "platform": platform,
            "tone": tone,
            "quality": quality,
            "language": language,
            "model": kwargs.get("model") or "ugc_pro",
        }
        medias = kwargs.get("medias")
        if not medias and kwargs.get("audio_media_id"):
            medias = [{"value": kwargs["audio_media_id"], "role": "audio"}]
        if medias:
            payload["medias"] = medias
        if kwargs.get("get_cost") is not None:
            payload["get_cost"] = bool(kwargs["get_cost"])

        if self.execution_surface == "claude_code_mcp":
            if shutil.which("claude") is None:
                return {
                    "error": "Claude Code CLI is not installed for Higgsfield MCP execution",
                    "provider": "higgsfield",
                    "execution_surface": "claude_code_mcp",
                }
            timeout_seconds = int(os.getenv("HIGGSFIELD_MCP_TIMEOUT_SECONDS", "300"))
            voiceover_script = kwargs.get("voiceover_script")
            wants_elevenlabs_voiceover = (
                isinstance(voiceover_script, str)
                and voiceover_script.strip()
                and str(kwargs.get("voice_provider") or "").lower() == "elevenlabs"
                and not medias
            )
            elevenlabs_audio = None
            if wants_elevenlabs_voiceover:
                try:
                    elevenlabs_audio = await _prepare_elevenlabs_audio_media(
                        script=voiceover_script.strip(),
                        language=str(kwargs.get("voice_language") or language or "en"),
                        model_id=str(kwargs.get("voice_model_id") or os.getenv("ELEVENLABS_MODEL_ID", "eleven_multilingual_v2")),
                        voice_id=str(kwargs.get("voice_id") or os.getenv("ELEVENLABS_VOICE_ID", DEFAULT_VOICE_ID)),
                        timeout_seconds=timeout_seconds,
                    )
                    medias = [{"value": elevenlabs_audio["media_id"], "role": "audio"}]
                except Exception as exc:
                    logger.error("ElevenLabs to Higgsfield audio bridge error: %s", exc)
                    return {
                        "error": str(exc),
                        "provider": "higgsfield",
                        "execution_surface": "claude_code_mcp",
                        "audio_provider": "elevenlabs",
                    }
            mcp_params = {
                "model": payload["model"],
                "prompt": prompt,
                "aspect_ratio": aspect_ratio,
                "duration": duration,
                "count": kwargs.get("count") or 1,
            }
            if medias:
                mcp_params["medias"] = medias
            if kwargs.get("preset_id"):
                mcp_params["preset_id"] = kwargs["preset_id"]
            if kwargs.get("get_cost") is not None:
                mcp_params["get_cost"] = bool(kwargs["get_cost"])
            mcp_prompt = (
                "Use the connected Higgsfield MCP tool mcp__higgsfield__generate_video "
                f"with this exact JSON params object: {json.dumps(mcp_params, sort_keys=True)}. "
                "Return only the raw JSON result."
            )
            try:
                raw_output = await _run_claude_mcp_prompt(
                    mcp_prompt,
                    timeout_seconds=timeout_seconds,
                    allowed_tools="mcp__higgsfield__generate_video",
                )
            except Exception as exc:
                logger.error("Higgsfield Claude Code MCP error: %s", exc)
                return {
                    "error": str(exc),
                    "provider": "higgsfield",
                    "execution_surface": "claude_code_mcp",
                }
            data = _extract_json_payload(raw_output)
            first_result = _first_higgsfield_result(data)
            task_id = (
                data.get("job_id")
                or data.get("id")
                or data.get("task_id")
                or first_result.get("job_id")
                or first_result.get("id")
                or first_result.get("task_id")
            )
            return {
                "status": data.get("status") or first_result.get("status") or ("queued" if task_id else "submitted"),
                "provider": "higgsfield",
                "execution_surface": "claude_code_mcp",
                "task_id": task_id,
                "mcp_result": data,
                "audio_media_id": elevenlabs_audio.get("media_id") if isinstance(elevenlabs_audio, dict) else None,
                "audio_provider": "elevenlabs" if isinstance(elevenlabs_audio, dict) else None,
                "message": "Higgsfield video generation submitted through Claude Code MCP.",
            }

        if not self.is_ready():
            return {"error": "Higgsfield API key not configured", "provider": "higgsfield"}

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
