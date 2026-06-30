import asyncio

from app.providers.adapters import elevenlabs as elevenlabs_module
from app.providers.adapters.elevenlabs import ElevenLabsProvider


class _FakeResponse:
    content = b"audio-bytes"

    def raise_for_status(self):
        return None


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


def test_elevenlabs_execute_uses_requested_multilingual_model(monkeypatch):
    monkeypatch.setattr(elevenlabs_module.httpx, "AsyncClient", _FakeAsyncClient)
    provider = ElevenLabsProvider()
    provider.set_api_key("test-key")

    result = asyncio.run(
        provider.execute(
            text="Bonjour",
            language="fr",
            model_id="eleven_multilingual_v2_custom_test",
        )
    )

    assert result["status"] == "success"
    assert _FakeAsyncClient.posted_json["model_id"] == "eleven_multilingual_v2_custom_test"
