import asyncio
import base64
import json

from app.providers.adapters import higgsfield as higgsfield_module
from app.providers.adapters.higgsfield import HiggsfieldProvider


class _FakeResponse:
    def raise_for_status(self):
        return None

    def json(self):
        return {"id": "task-123"}


class _FakeAsyncClient:
    posted_json = None

    def __init__(self, *args, **kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return None

    async def post(self, *args, **kwargs):
        _FakeAsyncClient.posted_json = kwargs["json"]
        return _FakeResponse()


def test_higgsfield_execute_sends_selected_model(monkeypatch):
    monkeypatch.setenv("HIGGSFIELD_EXECUTION_SURFACE", "api_key")
    monkeypatch.setattr(higgsfield_module.httpx, "AsyncClient", _FakeAsyncClient)
    provider = HiggsfieldProvider()
    provider.set_api_key("test-key")

    result = asyncio.run(
        provider.execute(
            prompt="Create a cinematic product launch clip",
            model="Cinema Studio 4K",
        )
    )

    assert result["status"] == "queued"
    assert _FakeAsyncClient.posted_json["model"] == "Cinema Studio 4K"


def test_higgsfield_execute_sends_audio_media_reference(monkeypatch):
    monkeypatch.setenv("HIGGSFIELD_EXECUTION_SURFACE", "api_key")
    monkeypatch.setattr(higgsfield_module.httpx, "AsyncClient", _FakeAsyncClient)
    provider = HiggsfieldProvider()
    provider.set_api_key("test-key")

    result = asyncio.run(
        provider.execute(
            prompt="Create a product launch clip with uploaded narration",
            model="seedance_2_0",
            audio_media_id="audio-media-123",
        )
    )

    assert result["status"] == "queued"
    assert _FakeAsyncClient.posted_json["model"] == "seedance_2_0"
    assert _FakeAsyncClient.posted_json["medias"] == [
        {"value": "audio-media-123", "role": "audio"}
    ]


def test_higgsfield_mcp_execute_uses_claude_generate_video(monkeypatch):
    captured = {}

    async def fake_run(prompt, *, timeout_seconds, allowed_tools=None):
        captured["prompt"] = prompt
        captured["timeout_seconds"] = timeout_seconds
        return json.dumps({"job_id": "higgs-job-123", "status": "queued"})

    monkeypatch.setenv("HIGGSFIELD_EXECUTION_SURFACE", "claude_code_mcp")
    monkeypatch.setattr(higgsfield_module.shutil, "which", lambda name: "claude")
    monkeypatch.setattr(higgsfield_module, "_run_claude_mcp_prompt", fake_run)

    provider = HiggsfieldProvider()
    result = asyncio.run(
        provider.execute(
            prompt="Create a 5 second product launch clip",
            model="kling3_0_turbo",
            duration=5,
            aspect_ratio="9:16",
            get_cost=False,
        )
    )

    assert result["status"] == "queued"
    assert result["provider"] == "higgsfield"
    assert result["execution_surface"] == "claude_code_mcp"
    assert result["task_id"] == "higgs-job-123"
    assert "mcp__higgsfield__generate_video" in captured["prompt"]
    assert '"model": "kling3_0_turbo"' in captured["prompt"]
    assert '"duration": 5' in captured["prompt"]


def test_higgsfield_mcp_execute_extracts_nested_result_task_id(monkeypatch):
    async def fake_run(prompt, *, timeout_seconds, allowed_tools=None):
        return json.dumps({"results": [{"id": "nested-video-123", "status": "pending"}]})

    monkeypatch.setenv("HIGGSFIELD_EXECUTION_SURFACE", "claude_code_mcp")
    monkeypatch.setattr(higgsfield_module.shutil, "which", lambda name: "claude")
    monkeypatch.setattr(higgsfield_module, "_run_claude_mcp_prompt", fake_run)

    result = asyncio.run(
        HiggsfieldProvider().execute(
            prompt="Create a 5 second product launch clip",
            model="kling3_0_turbo",
            duration=5,
            aspect_ratio="9:16",
        )
    )

    assert result["status"] == "pending"
    assert result["task_id"] == "nested-video-123"


def test_higgsfield_mcp_generates_elevenlabs_audio_and_attaches_it(monkeypatch):
    calls = []
    uploaded = {}

    class FakeElevenLabsProvider:
        def set_api_key(self, api_key):
            uploaded["elevenlabs_key"] = api_key

        async def execute(self, **kwargs):
            uploaded["elevenlabs_request"] = kwargs
            return {
                "status": "success",
                "audio_base64": base64.b64encode(b"hello-audio").decode("ascii"),
                "content_type": "audio/mpeg",
            }

    class FakeAsyncClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return None

        async def put(self, url, **kwargs):
            uploaded["put_url"] = url
            uploaded["put_content"] = kwargs["content"]
            uploaded["put_headers"] = kwargs["headers"]

            class Response:
                def raise_for_status(self):
                    return None

            return Response()

    async def fake_run(prompt, *, timeout_seconds, allowed_tools=None):
        calls.append({"prompt": prompt, "allowed_tools": allowed_tools})
        if allowed_tools == "mcp__higgsfield__media_upload":
            return json.dumps({"media_id": "audio-media-123", "upload_url": "https://upload.example/audio.mp3"})
        if allowed_tools == "mcp__higgsfield__media_confirm":
            return json.dumps({"media_id": "audio-media-123", "status": "ready"})
        return json.dumps({"job_id": "higgs-job-123", "status": "queued"})

    monkeypatch.setenv("HIGGSFIELD_EXECUTION_SURFACE", "claude_code_mcp")
    monkeypatch.setenv("ELEVENLABS_API_KEY", "eleven-key")
    monkeypatch.setattr(higgsfield_module.shutil, "which", lambda name: "claude")
    monkeypatch.setattr(higgsfield_module, "ElevenLabsProvider", FakeElevenLabsProvider, raising=False)
    monkeypatch.setattr(higgsfield_module.httpx, "AsyncClient", FakeAsyncClient)
    monkeypatch.setattr(higgsfield_module, "_run_claude_mcp_prompt", fake_run)

    result = asyncio.run(
        HiggsfieldProvider().execute(
            prompt="Create a product launch clip",
            model="kling3_0_turbo",
            voiceover_script="Bonjour, decouvrez notre nouveau produit.",
            voice_provider="elevenlabs",
            voice_language="fr",
            voice_model_id="eleven_multilingual_v2",
        )
    )

    assert result["status"] == "queued"
    assert result["task_id"] == "higgs-job-123"
    assert uploaded["elevenlabs_key"] == "eleven-key"
    assert uploaded["elevenlabs_request"]["text"] == "Bonjour, decouvrez notre nouveau produit."
    assert uploaded["elevenlabs_request"]["language"] == "fr"
    assert uploaded["put_url"] == "https://upload.example/audio.mp3"
    assert uploaded["put_content"] == b"hello-audio"
    assert uploaded["put_headers"]["Content-Type"] == "audio/mpeg"
    generate_call = calls[-1]
    assert generate_call["allowed_tools"] == "mcp__higgsfield__generate_video"
    assert '"medias": [{"role": "audio", "value": "audio-media-123"}]' in generate_call["prompt"]


def test_higgsfield_mcp_readiness_uses_secret_credentials(tmp_path, monkeypatch):
    created = {}

    def fake_run(*args, **kwargs):
        created["args"] = args[0]
        class Result:
            returncode = 0
            stdout = "[]"
            stderr = ""
        return Result()

    monkeypatch.setenv(
        "HIGGSFIELD_MCP_CREDENTIALS_JSON",
        '{"access_token":"test-access","refresh_token":"test-refresh"}',
    )
    monkeypatch.setenv("HIGGSFIELD_MCP_CONFIG_HOME", str(tmp_path))
    monkeypatch.setattr(higgsfield_module.shutil, "which", lambda name: "claude")
    monkeypatch.setattr(higgsfield_module.subprocess, "run", fake_run)
    higgsfield_module._MCP_READY_CACHE.update({"checked_at": 0.0, "ready": False})

    provider = HiggsfieldProvider()

    assert provider.is_mcp_ready() is True
    credentials_path = tmp_path / "higgsfield" / "credentials.json"
    assert credentials_path.exists()
    assert "test-access" in credentials_path.read_text(encoding="utf-8")
    assert "--mcp-config" in created["args"]
    assert "--strict-mcp-config" in created["args"]
