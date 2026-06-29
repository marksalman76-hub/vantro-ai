import asyncio

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
